#!/usr/bin/env python3
"""onboarding-git 실습 채점 — GitHub에서 증거를 모으고 평가표(rubric.md)의 자동 판정까지 한다.

사용법 (gh CLI 로그인 필요: gh auth login)
    python grading/collect.py 주인아이디/onboarding-git                 # 평가표 형식 Markdown
    python grading/collect.py 주인1/onboarding-git 주인2/onboarding-git  # 여러 조 한꺼번에
    python grading/collect.py --list repos.txt --format json > evidence.json
    python grading/collect.py --from-json raw.json                     # 저장해 둔 원자료로 다시 채점

판정은 GitHub에 남은 기록만 본다. «AI 확인» 표시가 붙은 항목(글의 내용)은
AI 또는 사람이 rubric.md의 기준으로 최종 판정한다.
"""
import argparse
import json
import re
import subprocess
import sys

TYPES = "feat|fix|docs|refactor|chore|init"
RE_BRANCH = re.compile(r"^(feat|fix|docs|refactor|chore)/#(\d+)-\S+$")
RE_COMMIT = re.compile(rf"^#(\d+) ({TYPES}): \S")
RE_PR_TITLE = re.compile(r"^\[#(\d+)\] \S")
RE_PR_TITLE_TYPED = re.compile(rf"^\[#\d+\] ({TYPES})\s*:")
RE_MARKER = re.compile(r"^(<<<<<<<|>>>>>>>)", re.M)
DEFAULT_TEAM = "팀 이름: (아직 정하지 않음)"

# 평가표와 같은 순서 · 배점 (합계 100)
ITEMS = [
    ("I1", "실습 1 · Issue", 5),
    ("B1", "실습 1 · Branch 이름", 5),
    ("C1", "실습 1 · Commit", 10),
    ("R1", "실습 1 · Pull Request 작성", 10),
    ("F1", "실습 1 · 자기소개 내용", 10),
    ("V1", "실습 1 · 상대 PR Review", 15),
    ("A1", "실습 1 · 받은 Review 반영", 10),
    ("M1", "실습 1 · Squash Merge 마무리", 10),
    ("K1", "실습 2 · 내 PR", 10),
    ("K2", "실습 2 · Conflict 해결 (조 공동)", 15),
]
POINTS = {k: p for k, _, p in ITEMS}
TITLES = {k: t for k, t, _ in ITEMS}
DIRECT_PUSH_PENALTY = 10
PASS_SCORE = 70  # 완료 = 70점 이상이고 «미충족» 항목이 없다

QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    nameWithOwner
    owner { login }
    defaultBranchRef {
      name
      target { ... on Commit {
        history(first: 100) { nodes {
          oid messageHeadline committedDate
          parents(first: 3) { totalCount }
          author { name user { login } }
          associatedPullRequests(first: 3) { nodes { number } }
        } }
      } }
    }
    refs(refPrefix: "refs/heads/", first: 100) { nodes { name } }
    team: object(expression: "HEAD:team.md") { ... on Blob { text } }
    members: object(expression: "HEAD:members") { ... on Tree { entries { name object { ... on Blob { text } } } } }
    issues(first: 100, orderBy: {field: CREATED_AT, direction: ASC}) { nodes {
      number title body state createdAt closedAt
      author { login }
      assignees(first: 5) { nodes { login } }
      closedByPullRequestsReferences(first: 5, includeClosedPrs: true) { nodes { number } }
    } }
    pullRequests(first: 100, orderBy: {field: CREATED_AT, direction: ASC}) { nodes {
      number title body state merged mergedAt createdAt headRefName
      author { login }
      mergedBy { login }
      headRef { name }
      mergeCommit { oid messageHeadline parents(first: 3) { totalCount } }
      closingIssuesReferences(first: 5) { nodes { number } }
      files(first: 50) { nodes { path } }
      commits(first: 100) { nodes { commit {
        oid messageHeadline committedDate
        parents(first: 3) { totalCount }
        author { name user { login } }
      } } }
      reviews(first: 50) { nodes {
        state submittedAt body
        author { login }
        comments(first: 20) { nodes { body } }
      } }
      reviewThreads(first: 50) { nodes {
        isResolved
        resolvedBy { login }
        comments(first: 20) { nodes { body createdAt author { login } } }
      } }
      timelineItems(first: 100, itemTypes: [REVIEW_REQUESTED_EVENT, HEAD_REF_DELETED_EVENT]) { nodes {
        __typename
        ... on ReviewRequestedEvent { createdAt actor { login } requestedReviewer { ... on User { login } } }
        ... on HeadRefDeletedEvent { createdAt actor { login } }
      } }
    } }
  }
}
"""


# ───────────────────────── 수집 ─────────────────────────

def fetch(repo):
    owner, name = parse_repo(repo)
    res = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"owner={owner}", "-F", f"name={name}"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if res.returncode != 0:
        raise SystemExit(f"[{repo}] gh api 실패: {res.stderr.strip()}")
    data = json.loads(res.stdout)
    if data.get("errors"):
        raise SystemExit(f"[{repo}] GraphQL 오류: {data['errors']}")
    return data["data"]["repository"]


def parse_repo(text):
    m = re.search(r"(?:github\.com[/:])?([\w.-]+)/([\w.-]+?)(?:\.git)?/?$", text.strip())
    if not m:
        raise SystemExit(f"저장소 형식을 알 수 없습니다: {text} (예: 아이디/onboarding-git)")
    return m.group(1), m.group(2)


# ───────────────────────── 판정 도우미 ─────────────────────────

def login_of(actor):
    return (actor or {}).get("login")


def is_bot(login):
    return not login or login.endswith("[bot]")


def nodes(obj, key):
    return ((obj or {}).get(key) or {}).get("nodes") or []


def commit_login(c):
    return login_of((c.get("author") or {}).get("user"))


def result(key, status, evidence, ai=False):
    full = POINTS[key]
    score = {"pass": full, "na": full, "partial": (full + 1) // 2, "fail": 0}[status]
    return {"id": key, "title": TITLES[key], "points": full, "status": status,
            "score": score, "ai_check": ai, "evidence": evidence}


def pr_kind(pr):
    paths = [f["path"] for f in nodes(pr, "files")]
    if any(p.startswith("members/") and p != "members/_template.md" for p in paths):
        return "p1"
    if "team.md" in paths:
        return "p2"
    return "other"


def linked_issue(pr):
    refs = [n["number"] for n in nodes(pr, "closingIssuesReferences")]
    if refs:
        return refs[0]
    for text in (pr["title"], pr["headRefName"]):
        m = re.search(r"#(\d+)", text or "")
        if m:
            return int(m.group(1))
    return None


def pick(prs):
    """같은 종류 PR이 여럿이면 합쳐진 것 → 가장 최근 것."""
    if not prs:
        return None
    merged = [p for p in prs if p["merged"]]
    return (merged or prs)[-1]


def url(repo, kind, n):
    return f"https://github.com/{repo}/{kind}/{n}"


def own_commits(pr, login, merges=False):
    out = []
    for n in nodes(pr, "commits"):
        c = n["commit"]
        if c["parents"]["totalCount"] >= 2 and not merges:
            continue  # 실습 1에서는 merge commit을 세지 않는다
        who = commit_login(c)
        if who is None or who == login:
            out.append(c)
    return out


def short(text, n=300):
    text = (text or "").strip().replace("\r", "")
    return text if len(text) <= n else text[:n] + "…"


# ───────────────────────── 항목별 판정 ─────────────────────────

def check_issue(repo, login, pr, issues):
    if not pr:
        return result("I1", "fail", ["실습 1 PR이 없어 연결된 Issue를 찾지 못했다"])
    n = linked_issue(pr)
    issue = issues.get(n)
    if not issue:
        return result("I1", "fail", [f"PR #{pr['number']}에서 Issue 번호를 찾지 못했다"])
    ev, ok = [f"Issue #{n} {url(repo, 'issues', n)}"], 0
    if login_of(issue["author"]) == login:
        ok += 1
    else:
        ev.append(f"작성자가 본인이 아니다 ({login_of(issue['author'])})")
    if login in [a["login"] for a in nodes(issue, "assignees")]:
        ok += 1
    else:
        ev.append("Assignees에 본인이 없다")
    if "## 할 일" in (issue["body"] or ""):
        ok += 1
    else:
        ev.append("«작업» 양식을 쓰지 않았다")
    return result("I1", "pass" if ok == 3 else "partial", ev)


def check_branch(repo, login, pr):
    if not pr:
        return result("B1", "fail", ["실습 1 PR이 없다"])
    name, n = pr["headRefName"], linked_issue(pr)
    m = RE_BRANCH.match(name)
    if m and int(m.group(2)) == n:
        return result("B1", "pass", [f"`{name}`"])
    if m:
        return result("B1", "partial", [f"`{name}` — Branch 번호(#{m.group(2)})가 Issue #{n}과 다르다"])
    return result("B1", "fail", [f"`{name}` — `type/#번호-설명` 형식이 아니다"])


def commit_rule_problems(commits, n):
    bad = []
    for c in commits:
        m = RE_COMMIT.match(c["messageHeadline"])
        if not m:
            bad.append(f"`{c['messageHeadline']}` — `#번호 type: 내용` 형식이 아니다")
        elif n is not None and int(m.group(1)) != n:
            bad.append(f"`{c['messageHeadline']}` — 번호가 Issue #{n}과 다르다")
    return bad


def check_commits(repo, login, pr):
    if not pr:
        return result("C1", "fail", ["실습 1 PR이 없다"])
    commits = own_commits(pr, login)
    n = linked_issue(pr)
    bad = commit_rule_problems(commits, n)
    ev = [f"본인 Commit {len(commits)}개: " + " / ".join(f"`{c['messageHeadline']}`" for c in commits)]
    ev += bad
    if any(commit_login(c) is None for c in commits):
        ev.append("참고: Commit 이메일이 GitHub 계정과 연결되지 않았다 (git config user.email 확인)")
    enough = len(commits) >= 2
    if enough and not bad:
        return result("C1", "pass", ev)
    if enough or (commits and not bad):
        if not enough:
            ev.append("Commit이 두 개보다 적다")
        return result("C1", "partial", ev)
    return result("C1", "fail", ev)


def requested_reviewers(pr):
    return [(login_of(e.get("requestedReviewer")), e["createdAt"], login_of(e.get("actor")))
            for e in nodes(pr, "timelineItems") if e["__typename"] == "ReviewRequestedEvent"]


def pr_rule_problems(pr):
    bad = []
    if not RE_PR_TITLE.match(pr["title"]):
        bad.append(f"제목 `{pr['title']}` — `[#번호] 내용` 형식이 아니다")
    elif RE_PR_TITLE_TYPED.match(pr["title"]):
        bad.append(f"제목 `{pr['title']}` — PR 제목에는 type을 쓰지 않는다")
    if not nodes(pr, "closingIssuesReferences"):
        bad.append("본문에 `Closes #번호`가 없다 (Issue와 연결되지 않음)")
    return bad


def check_pr(repo, login, pr, others):
    if not pr:
        return result("R1", "fail", ["실습 1 PR이 없다"])
    ev = [f"PR #{pr['number']} {url(repo, 'pull', pr['number'])} «{pr['title']}»"]
    bad = pr_rule_problems(pr)
    asked = [r for r, _, _ in requested_reviewers(pr) if r in others]
    if not asked:
        bad.append("상대를 Reviewer로 지정한 기록이 없다")
    ev += bad
    return result("R1", "pass" if not bad else ("partial" if len(bad) < 3 else "fail"), ev)


def check_profile(repo, login, members, template):
    f = members.get(f"{login.lower()}.md")
    if f is None:
        return result("F1", "fail", [f"`members/{login}.md`가 main에 없다 (파일 이름이 GitHub 아이디와 다를 수 있음)"], ai=True)
    text = f or ""
    ev = [f"`members/{login}.md` 내용:\n{short(text, 1200)}"]
    if text.strip() == template.strip() or "@아이디" in text:
        ev.append("양식 그대로이거나 «@아이디»가 남아 있다")
        return result("F1", "partial", ev, ai=True)
    return result("F1", "pass", ev, ai=True)


def check_review_given(repo, login, partner_prs):
    if not partner_prs:
        return result("V1", "fail", ["상대의 실습 1 PR이 없어 Review할 대상이 없다"], ai=True)
    best, best_ok = None, -1
    for pr in partner_prs:
        reviews = [r for r in nodes(pr, "reviews") if login_of(r["author"]) == login]
        cr = [r for r in reviews if r["state"] == "CHANGES_REQUESTED"]
        approved = [r for r in reviews if r["state"] == "APPROVED"
                    and (not cr or r["submittedAt"] > cr[0]["submittedAt"])]
        inline = [c["body"] for t in nodes(pr, "reviewThreads") for c in nodes(t, "comments")
                  if login_of(c["author"]) == login]
        ok = bool(cr) + bool(inline) + bool(approved)
        if ok > best_ok:
            best_ok = ok
            ev = [f"상대 PR #{pr['number']} {url(repo, 'pull', pr['number'])}"]
            ev.append("Request changes: " + ("있음" if cr else "없음"))
            ev.append("줄 의견: " + (" / ".join(f"«{short(b, 160)}»" for b in inline) if inline else "없음"))
            ev += [f"Review 본문({r['state']}): «{short(r['body'], 160)}»" for r in reviews if (r["body"] or "").strip()]
            ev.append("수정 요청 뒤 Approve: " + ("있음" if approved else "없음"))
            best = ev
    status = "pass" if best_ok == 3 else "partial" if best_ok > 0 else "fail"
    return result("V1", status, best, ai=True)


def check_review_applied(repo, login, pr, others):
    if not pr:
        return result("A1", "fail", ["실습 1 PR이 없다"])
    cr = sorted((r for r in nodes(pr, "reviews")
                 if r["state"] == "CHANGES_REQUESTED" and login_of(r["author"]) in others),
                key=lambda r: r["submittedAt"])
    if not cr:
        return result("A1", "na", ["상대가 Request changes를 하지 않아 확인할 수 없다 — 이 항목은 만점 처리, 상대의 V1에서 본다"])
    t = cr[0]["submittedAt"]
    later = [c for c in own_commits(pr, login) if c["committedDate"] > t]
    threads = nodes(pr, "reviewThreads")
    replied = any(login_of(c["author"]) == login and c["createdAt"] > t
                  for th in threads for c in nodes(th, "comments"))
    resolved = any(th["isResolved"] for th in threads)
    rerequest = any(r in others and at > t for r, at, _ in requested_reviewers(pr))
    ev = [f"수정 요청 시각 {t}",
          "그 뒤 Commit: " + (" / ".join(f"`{c['messageHeadline']}`" for c in later) if later else "없음"),
          f"의견에 답글: {'있음' if replied else '없음'} · Resolve: {'있음' if resolved else '없음'} · Re-request review: {'있음' if rerequest else '없음'}"]
    if later and (replied or resolved) and rerequest:
        return result("A1", "pass", ev)
    return result("A1", "partial" if later else "fail", ev)


def squash_ok(pr):
    mc = pr.get("mergeCommit")
    if not (pr["merged"] and mc):
        return False
    return mc["parents"]["totalCount"] == 1 and mc["messageHeadline"].endswith(f"(#{pr['number']})")


def check_merge(repo, login, pr, issues, branches):
    if not pr:
        return result("M1", "fail", ["실습 1 PR이 없다"])
    if not pr["merged"]:
        return result("M1", "fail", [f"PR #{pr['number']}이 아직 합쳐지지 않았다 (상태 {pr['state']})"])
    bad = []
    if login_of(pr["mergedBy"]) != login:
        bad.append(f"Merge를 본인이 아닌 {login_of(pr['mergedBy'])}가 눌렀다")
    if not squash_ok(pr):
        mc = pr.get("mergeCommit") or {}
        bad.append(f"Squash and merge가 아니다 (main에 남은 줄: `{mc.get('messageHeadline')}`)")
    deleted = any(e["__typename"] == "HeadRefDeletedEvent" for e in nodes(pr, "timelineItems"))
    if not deleted and pr["headRefName"] in branches:
        bad.append(f"Branch `{pr['headRefName']}`를 지우지 않았다")
    n = linked_issue(pr)
    issue = issues.get(n)
    if not issue or issue["state"] != "CLOSED" or pr["number"] not in [x["number"] for x in nodes(issue, "closedByPullRequestsReferences")]:
        bad.append(f"Issue #{n}이 이 PR로 닫히지 않았다")
    ev = [f"main에 남은 줄: `{(pr.get('mergeCommit') or {}).get('messageHeadline')}`"] + bad
    return result("M1", "pass" if not bad else "partial", ev)


def check_p2_pr(repo, login, pr):
    if not pr:
        return result("K1", "fail", ["`team.md`를 고친 실습 2 PR이 없다"])
    n = linked_issue(pr)
    bad = pr_rule_problems(pr)
    m = RE_BRANCH.match(pr["headRefName"])
    if not m or int(m.group(2)) != n:
        bad.append(f"Branch `{pr['headRefName']}` 규칙 위반")
    bad += commit_rule_problems(own_commits(pr, login, merges=True), n)  # Conflict 해결 Commit 포함
    if not pr["merged"]:
        bad.append("아직 합쳐지지 않았다")
    ev = [f"PR #{pr['number']} {url(repo, 'pull', pr['number'])} «{pr['title']}»"] + bad
    return result("K1", "pass" if not bad else "partial", ev)


def check_conflict(repo, p2_prs, team_text):
    resolutions = []
    for pr in p2_prs:
        for node in nodes(pr, "commits"):
            c = node["commit"]
            if c["parents"]["totalCount"] >= 2:
                resolutions.append((pr, c))
    ev = []
    clean = team_text is not None and not RE_MARKER.search(team_text)
    named = team_text is not None and DEFAULT_TEAM not in team_text
    line = next((l for l in (team_text or "").splitlines() if l.startswith("팀 이름")), "(없음)")
    ev.append(f"main의 team.md: `{line}`")
    if not clean:
        ev.append("team.md에 Conflict 표시(<<<<<<< · >>>>>>>)가 남아 있다")
    if not named:
        ev.append("팀 이름이 처음 그대로다")
    for pr, c in resolutions:
        who = commit_login(c) or c["author"]["name"]
        rule = "" if RE_COMMIT.match(c["messageHeadline"]) else " — 메시지 규칙 위반"
        ev.append(f"해결 Commit({who}) PR #{pr['number']}: `{c['messageHeadline']}`{rule}")
    if not p2_prs:
        return result("K2", "fail", ["실습 2 PR이 없다"])
    if resolutions and clean and named:
        return result("K2", "pass", ev)
    if not resolutions:
        ev.append("Conflict를 푼 merge Commit이 없다 — 두 PR이 다른 줄을 고쳤거나 다른 방법으로 합쳤는지 확인")
    return result("K2", "partial" if clean else "fail", ev, ai=not resolutions)


# ───────────────────────── 조 단위 채점 ─────────────────────────

def grade(repo_data):
    repo = repo_data["nameWithOwner"]
    prs = nodes(repo_data, "pullRequests")
    issues = {i["number"]: i for i in nodes(repo_data, "issues")}
    branches = {r["name"] for r in nodes(repo_data, "refs")}
    members = {}
    tree = repo_data.get("members") or {}
    template = ""
    for e in tree.get("entries") or []:
        text = (e.get("object") or {}).get("text") or ""
        if e["name"] == "_template.md":
            template = text
        else:
            members[e["name"].lower()] = text
    team_text = (repo_data.get("team") or {}).get("text")

    people = []
    for x in prs + list(issues.values()):
        who = login_of(x["author"])
        if not is_bot(who) and who not in people:
            people.append(who)

    by_kind = {"p1": [], "p2": [], "other": []}
    for pr in prs:
        by_kind[pr_kind(pr)].append(pr)
    p2_prs = by_kind["p2"]
    conflict = check_conflict(repo, p2_prs, team_text)

    # main에 PR 없이 들어간 Commit (가장 오래된 템플릿 Commit은 제외)
    history = (((repo_data.get("defaultBranchRef") or {}).get("target") or {}).get("history") or {}).get("nodes") or []
    direct = [c for c in history[:-1] if not nodes(c, "associatedPullRequests")]

    results = []
    for login in people:
        others = [p for p in people if p != login]
        mine1 = pick([p for p in by_kind["p1"] if login_of(p["author"]) == login])
        partner1 = [p for p in by_kind["p1"] if login_of(p["author"]) in others]
        mine2 = pick([p for p in p2_prs if login_of(p["author"]) == login])
        items = [
            check_issue(repo, login, mine1, issues),
            check_branch(repo, login, mine1),
            check_commits(repo, login, mine1),
            check_pr(repo, login, mine1, others),
            check_profile(repo, login, members, template),
            check_review_given(repo, login, partner1),
            check_review_applied(repo, login, mine1, others),
            check_merge(repo, login, mine1, issues, branches),
            check_p2_pr(repo, login, mine2),
            dict(conflict),
        ]
        pushed = [c for c in direct if commit_login(c) == login]
        penalty = DIRECT_PUSH_PENALTY if pushed else 0
        total = max(0, sum(i["score"] for i in items) - penalty)
        results.append({
            "login": login,
            "items": items,
            "penalty": {"points": penalty, "evidence": [f"`{c['messageHeadline']}` ({c['oid'][:7]})" for c in pushed]},
            "total": total,
            "verdict": "완료" if total >= PASS_SCORE and not any(i["status"] == "fail" for i in items) else "보완",
        })

    other_direct = [c for c in direct if commit_login(c) not in people]
    return {
        "repo": repo,
        "people": people,
        "results": results,
        "repo_flags": {
            "direct_push_to_main": [f"`{c['messageHeadline']}` ({c['oid'][:7]}, {commit_login(c) or c['author']['name']})" for c in direct],
            "unattributed_direct_push": [c["oid"][:7] for c in other_direct],
            "other_prs": [f"#{p['number']} «{p['title']}»" for p in by_kind["other"]],
        },
    }


# ───────────────────────── 출력 ─────────────────────────

MARK = {"pass": "충족", "partial": "부분", "fail": "미충족", "na": "해당 없음"}


def to_markdown(graded):
    out = []
    for g in graded:
        out.append(f"# {g['repo']}\n")
        out.append(f"참여자: {', '.join('@' + p for p in g['people']) or '(없음)'}\n")
        for r in g["results"]:
            out.append(f"## @{r['login']} — {r['total']} / 100 · {r['verdict']}\n")
            out.append("| 항목 | 배점 | 판정 | 점수 | 근거 |\n|---|---|---|---|---|")
            for i in r["items"]:
                ev = "<br>".join(e.replace("\n", "<br>").replace("|", "\\|") for e in i["evidence"])
                ai = " · AI 확인" if i["ai_check"] else ""
                out.append(f"| {i['id']} {i['title']} | {i['points']} | {MARK[i['status']]}{ai} | {i['score']} | {ev} |")
            if r["penalty"]["points"]:
                out.append(f"| 감점 · main 직접 Push | −{r['penalty']['points']} | | | {'<br>'.join(r['penalty']['evidence'])} |")
            out.append("")
        flags = g["repo_flags"]
        if flags["direct_push_to_main"] or flags["other_prs"]:
            out.append("### 저장소 메모\n")
            if flags["direct_push_to_main"]:
                out.append("- PR 없이 main에 들어간 Commit: " + ", ".join(flags["direct_push_to_main"]))
            if flags["other_prs"]:
                out.append("- 실습 1 · 2 어디에도 속하지 않는 PR: " + ", ".join(flags["other_prs"]))
            out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="onboarding-git 실습 채점")
    ap.add_argument("repos", nargs="*", help="주인아이디/onboarding-git 또는 GitHub URL")
    ap.add_argument("--list", help="저장소를 한 줄에 하나씩 적은 파일")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--raw-out", help="GitHub에서 받은 원자료를 이 파일에 저장")
    ap.add_argument("--from-json", help="--raw-out으로 저장한 원자료로 채점 (GitHub에 묻지 않음)")
    a = ap.parse_args()

    if a.from_json:
        with open(a.from_json, encoding="utf-8") as f:
            raw = json.load(f)
    else:
        repos = list(a.repos)
        if a.list:
            with open(a.list, encoding="utf-8") as f:
                repos += [l.strip() for l in f if l.strip() and not l.startswith("#")]
        if not repos:
            ap.error("저장소를 하나 이상 주세요")
        raw = [fetch(r) for r in repos]
        if a.raw_out:
            with open(a.raw_out, "w", encoding="utf-8") as f:
                json.dump(raw, f, ensure_ascii=False, indent=1)

    graded = [grade(r) for r in raw]
    sys.stdout.reconfigure(encoding="utf-8")
    if a.format == "json":
        print(json.dumps(graded, ensure_ascii=False, indent=1))
    else:
        print(to_markdown(graded))


if __name__ == "__main__":
    main()

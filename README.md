# onboarding-git

SSCCOps Maintainer Onboarding **1회차 · Git & Collaboration** 실습용 Repository입니다.

코드는 없습니다. Markdown 파일 두 개를 고치면서 Git으로 함께 일하는 흐름 하나를 끝까지 돌아 봅니다.

```text
Issue → Branch → Commit → Push → Pull Request → Review → Squash Merge
```

## 파일 구성

| 파일 | 쓰는 곳 |
|---|---|
| `members/_template.md` | 실습 1 — 이 파일을 복사해 자기소개를 쓴다 |
| `team.md` | 실습 2 — 두 사람이 같은 줄을 고쳐 Conflict를 만든다 |
| `.github/ISSUE_TEMPLATE/task.md` | Issue를 만들 때 나오는 양식 |
| `.github/pull_request_template.md` | Pull Request를 만들 때 나오는 양식 |
| `grading/` | 평가표(`rubric.md`)와 채점 도구 — 실습을 마친 뒤 스스로 점검할 때도 쓴다 |
| `.claude/skills/grade-git-practice/` | Claude Code에서 «Git 실습 채점해 줘»로 부르는 채점 Skill |

## 0. 준비

2인 1조로 진행합니다. **한 사람만** Repository를 만들고, 두 사람이 그 Repository에 함께 작업합니다.

1. **(주인)** 이 페이지 오른쪽 위의 **Use this template → Create a new repository**를 누릅니다.
   Owner는 **내 계정**, 이름은 `onboarding-git`, 공개 범위는 Public으로 만듭니다.
2. **(주인)** 만든 Repository의 **Settings → Collaborators → Add people**에서 Pair를 초대합니다.
   **(Pair)** 메일이나 GitHub 알림에서 초대를 수락합니다.
3. **(둘 다)** 주인의 Repository를 각자 컴퓨터로 내려받습니다.

   ```bash
   git clone https://github.com/<주인의 GitHub 아이디>/onboarding-git.git
   cd onboarding-git
   ```

처음 Git을 쓰는 컴퓨터라면 이름과 이메일을 한 번 알려 줍니다.

```bash
git config --global user.name "내 이름"
git config --global user.email "GitHub에 가입한 이메일"
```

> Windows에서는 Git을 설치할 때 함께 들어오는 **Git Bash**에서 아래 명령을 입력하세요.

## 역할

두 사람 모두 **작업자이자 Reviewer**입니다. 각자 자기 PR을 올리고, 상대의 PR을 Review합니다.

| 역할 | 하는 일 |
|---|---|
| 작업자 (두 사람 모두) | 자기 Issue · Branch · Commit · Push · Pull Request · 수정 반영 |
| Reviewer (상대의 PR에서) | 바뀐 줄 읽기 · 의견 · Request changes 또는 Approve |
| PR 작성자 | Approve를 받으면 자기 PR을 Squash and merge |

> Issue와 Pull Request는 번호를 함께 씁니다. 둘이 동시에 만들면 번호가 섞이므로, 아래 예의 `#1`은 **화면에서 받은 내 번호**로 바꿔 쓰세요.

## 1. 실습 1 — 각자 자기소개 추가하기

두 사람이 **동시에** `members/`에 자기 파일을 하나씩 더합니다. 서로 다른 파일이라 Conflict는 나지 않습니다.

**① Issue 만들기** — **Issues → New issue**에서 «작업» 양식을 고르고, 제목을 `자기소개 추가`로 적습니다.
Assignees에 나를 지정하고, 만들어진 번호(예: `#1`)를 기억합니다.

**② Branch 만들기** — Issue 번호를 넣어 이름을 짓습니다.

```bash
git switch -c feat/#1-intro
```

**③ 파일 만들고 첫 Commit** — 양식을 복사해 내 GitHub 아이디로 이름을 바꾸고, 이름과 한 줄 소개만 먼저 채웁니다.

```bash
cp members/_template.md members/<내 GitHub 아이디>.md
# 파일을 열어 «이름»과 «한 줄 소개»를 채운다
git add members/<내 GitHub 아이디>.md
git commit -m "#1 feat: 자기소개 추가"
```

**④ 두 번째 Commit** — 나머지 칸을 채우고 한 번 더 기록합니다. Commit은 작게, 여러 번 남겨도 괜찮습니다.

```bash
git add members/<내 GitHub 아이디>.md
git commit -m "#1 feat: 관심 분야와 기대하는 것 추가"
```

**⑤ Push하고 Pull Request 만들기**

```bash
git push -u origin feat/#1-intro
```

GitHub에 뜨는 **Compare & pull request**를 누릅니다. 제목은 `[#1] 자기소개 추가`(Commit 메시지와 달리 type을 쓰지 않습니다),
본문의 «관련 Issue»에는 `Closes #1`을 적습니다. **Reviewers에는 상대를** 지정합니다.

**⑥ 상대의 PR을 Review** — 상대 PR의 **Files changed** 탭에서 바뀐 줄을 읽고, 줄 옆의 `+`를 눌러 의견을 남긴 뒤
**Review changes → Request changes**로 한 가지 이상 고쳐 달라고 요청합니다.

**⑦ 받은 수정 요청 반영** — 내 Branch에서 고치고 다시 Push하면 내 PR에 Commit이 더해집니다.
의견에 답하고 **Resolve conversation**을 누른 뒤 **Re-request review**로 다시 봐 달라고 합니다.

```bash
git add members/<내 GitHub 아이디>.md
git commit -m "#1 fix: 리뷰 반영"
git push
```

**⑧ Approve와 Squash Merge** — Reviewer는 다시 읽고 **Review changes → Approve**로 승인합니다.
Approve를 받은 **작성자**가 Merge 버튼의 화살표에서 **Squash and merge**를 골라 합치고, **Delete branch**를 누릅니다.
`Closes #1`을 적었다면 Issue가 함께 닫힙니다.

**⑨ 마무리** — 내 컴퓨터의 `main`을 최신으로 맞추고, 합쳐진 Branch를 지웁니다.

```bash
git switch main
git pull
git branch -d feat/#1-intro
```

## 2. 실습 2 — Conflict 만들고 풀기

두 사람이 `team.md`의 **같은 줄**을 동시에 고칩니다.

1. 각자 Issue를 만들고 Branch를 엽니다. 예: `feat/#5-team-name` · `feat/#6-team-name`
2. 각자 `team.md`의 `팀 이름:` 줄을 **서로 다른 이름**으로 고쳐 Commit하고 Push한 뒤 PR을 만들어 상대에게 Review를 요청합니다.
3. 먼저 Approve를 받은 PR을 Squash Merge합니다.
4. 나중 PR에는 «This branch has conflicts» 표시가 뜹니다. 그 PR의 작성자가 내 컴퓨터에서 풉니다.

   ```bash
   git switch main
   git pull                       # 먼저 합쳐진 내용을 받는다
   git switch feat/#6-team-name
   git merge main                 # 여기서 Conflict가 난다
   ```

5. `team.md`를 열면 이런 표시가 보입니다.

   ```text
   <<<<<<< HEAD
   팀 이름: 내가 정한 이름
   =======
   팀 이름: 먼저 합쳐진 이름
   >>>>>>> main
   ```

   두 사람이 이야기해 남길 이름을 정하고 한 줄로 고친 뒤, `<<<<<<<` · `=======` · `>>>>>>>` 줄을 모두 지웁니다.

6. 해결을 기록하고 다시 올립니다. PR의 Conflict 표시가 사라지고 Approve를 받으면 Squash Merge합니다.

   ```bash
   git add team.md
   git commit -m "#6 fix: team.md Conflict 해결"
   git push
   ```

## 규칙

SSCCOps 실제 Repository와 같은 모양으로 연습합니다.

| 항목 | 규칙 | 예 |
|---|---|---|
| Branch 이름 | `{type}/#{Issue 번호}-{설명}` | `feat/#1-intro` |
| Commit 메시지 | `#{Issue 번호} {type}: 무엇을 했는가` | `#1 feat: 자기소개 추가` |
| PR 제목 | `[#{Issue 번호}] 무엇을 했는가` | `[#1] 자기소개 추가` |
| 합치기 | Squash and merge — PR 제목이 `main`에 남는 한 줄이 된다 | `[#1] 자기소개 추가 (#4)` |
| `main` | 직접 Push하지 않는다 | 언제나 PR로만 바뀐다 |

Commit 메시지 맨 앞의 `type`은 «무슨 종류의 변경인가»를 한 단어로 밝힙니다.

| type | 언제 |
|---|---|
| `feat` | 새 내용·기능을 더할 때 |
| `fix` | 틀린 것을 고칠 때 (리뷰 반영 포함) |
| `docs` | 설명 문서(README 등)만 바꿀 때 |
| `refactor` | 뜻은 그대로 두고 구조만 바꿀 때 |
| `chore` | 설정·정리처럼 내용과 무관한 일 |
| `init` | Repository를 처음 만들 때 |

> SSCCOps 실제 Repository는 여기에 범위를 더해 `#694 feat(academicprogram): …`처럼 씁니다. 오늘은 범위를 빼고 씁니다.

### 왜 `#번호`를 붙이나

GitHub는 Commit 메시지 · PR에 적힌 `#1`을 읽어서 기록을 자동으로 잇습니다.

- `#1`이 적힌 곳은 모두 Issue #1로 가는 링크가 됩니다.
- Issue #1 화면에 그 번호를 언급한 Commit과 PR이 자동으로 쌓입니다.
- PR 본문에 `Closes #1`(또는 `Fixes #1` · `Resolves #1`)을 쓰면 그 PR이 Merge될 때 Issue #1이 닫힙니다.

> Jira로 일을 관리하는 팀은 같은 자리에 Ticket 키를 씁니다 — `feat/SSCC-123-intro` · `SSCC-123 feat: 자기소개 추가`.
> Jira와 GitHub를 연동하면 Ticket 화면에 Branch · Commit · PR이 모입니다.

### 이미 `main`에 들어간 것을 고칠 때

**공유된 Branch(`main`)에 올라간 이력은 고쳐 쓰지 않습니다.** `reset`이나 `rebase`로 이력을 바꾼 뒤 `git push --force`로 덮어쓰면,
같은 Repository를 Clone한 상대의 이력과 어긋나 Commit이 사라지거나 엉뚱한 Conflict가 납니다. 대신 **새 Commit을 더해서** 바로잡습니다.

| 상황 | 방법 | 예 |
|---|---|---|
| 변경 자체가 잘못됐다 — 통째로 빼야 한다 | fix Branch에서 `git revert` | `git switch -c fix/#12-revert` → `git revert <해시>` |
| 방향은 맞고 일부만 틀렸다 | fix Branch에서 고치는 Commit | `git switch -c fix/#12-typo` → 고치고 `#12 fix: 오타 수정` |

어느 쪽이든 평소처럼 **새 Issue → fix Branch → PR → Review → Squash Merge**를 거칩니다. `main`에 직접 Push하지 않습니다.

> 아직 Push하지 않은 **내 Branch**는 `git commit --amend` 등으로 다듬어도 됩니다 — 아직 아무와도 공유하지 않았기 때문입니다.

## 완료 체크리스트

- [ ] Issue를 만들었다
- [ ] Issue 번호로 Branch를 만들었다
- [ ] Commit을 두 번 이상 남겼다
- [ ] Pull Request를 만들고 상대를 Reviewer로 지정했다
- [ ] 상대의 PR을 Review하고 수정을 요청했다
- [ ] 받은 수정 요청을 반영했다
- [ ] Squash Merge로 합쳤다
- [ ] Conflict를 만들고 직접 풀었다

## 명령어 모음

| 명령 | 하는 일 |
|---|---|
| `git clone <주소>` | Remote Repository를 내려받는다 |
| `git status` | 지금 무엇이 바뀌었고 무엇이 담겼는지 본다 |
| `git switch -c <Branch>` | Branch를 만들고 그리로 옮긴다 |
| `git switch <Branch>` | 다른 Branch로 옮긴다 |
| `git add <파일>` | 이번 Commit에 담을 변경을 고른다 |
| `git commit -m "<메시지>"` | 고른 변경을 이력에 한 줄 남긴다 |
| `git push` | 내 Commit을 GitHub에 올린다 |
| `git pull` | GitHub의 새 Commit을 받아 합친다 |
| `git merge <Branch>` | 다른 Branch를 지금 Branch에 합친다 |
| `git log --oneline` | 지난 이력을 한 줄씩 본다 |

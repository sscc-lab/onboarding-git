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

## 0. 준비

2인 1조로 진행합니다. 각자 Repository를 하나씩 만들고, 상대의 Repository에서 작업합니다.

1. 이 페이지 오른쪽 위의 **Use this template → Create a new repository**를 누릅니다.
   Owner는 **내 계정**, 이름은 `onboarding-git`, 공개 범위는 Public으로 만듭니다.
2. 내가 만든 Repository의 **Settings → Collaborators → Add people**에서 Pair를 초대합니다.
   Pair가 보낸 초대는 메일이나 GitHub 알림에서 수락합니다.
3. **Pair의 Repository**를 내 컴퓨터로 내려받습니다.

   ```bash
   git clone https://github.com/<Pair의 GitHub 아이디>/onboarding-git.git
   cd onboarding-git
   ```

처음 Git을 쓰는 컴퓨터라면 이름과 이메일을 한 번 알려 줍니다.

```bash
git config --global user.name "내 이름"
git config --global user.email "GitHub에 가입한 이메일"
```

> Windows에서는 Git을 설치할 때 함께 들어오는 **Git Bash**에서 아래 명령을 입력하세요.

## 역할

한 Repository 안에서 역할이 둘로 나뉩니다. 한 바퀴를 돌면 서로 바꿔서 상대 Repository에서 한 번 더 돕니다. 모두 **두 바퀴**입니다.

| 역할 | 누구 | 하는 일 |
|---|---|---|
| Repository 주인 | 그 Repository를 만든 사람 | Review · 수정 요청 · Approve · Squash Merge |
| 작업자 | Pair | Issue · Branch · Commit · Push · Pull Request · 수정 반영 |

## 1. 실습 1 — 자기소개 추가하기

작업자가 주인의 Repository에 자기소개 파일을 하나 더합니다.

**① Issue 만들기 (작업자)** — Repository의 **Issues → New issue**에서 «작업» 양식을 고르고,
제목을 `자기소개 추가`로 적습니다. 만들어진 Issue 번호(예: `#1`)를 기억합니다.

**② Branch 만들기 (작업자)** — Issue 번호를 넣어 이름을 짓습니다.

```bash
git switch -c feat/#1-intro
```

**③ 파일 만들고 첫 Commit (작업자)** — 양식을 복사해 내 GitHub 아이디로 이름을 바꾸고, 이름과 한 줄 소개만 먼저 채웁니다.

```bash
cp members/_template.md members/<내 GitHub 아이디>.md
# 파일을 열어 «이름»과 «한 줄 소개»를 채운다
git add members/<내 GitHub 아이디>.md
git commit -m "#1 feat: 자기소개 추가"
```

**④ 두 번째 Commit (작업자)** — 나머지 칸을 채우고 한 번 더 기록합니다. Commit은 작게, 여러 번 남겨도 괜찮습니다.

```bash
git add members/<내 GitHub 아이디>.md
git commit -m "#1 feat: 관심 분야와 기대하는 것 추가"
```

**⑤ Push하고 Pull Request 만들기 (작업자)**

```bash
git push -u origin feat/#1-intro
```

GitHub에 뜨는 **Compare & pull request**를 누릅니다. 제목은 `[#1] 자기소개 추가`(Commit 메시지와 달리 type을 쓰지 않습니다),
본문의 «관련 Issue»에는 `Closes #1`을 적습니다. Reviewers에는 Repository 주인을 지정합니다.

**⑥ Review (주인)** — **Files changed** 탭에서 바뀐 줄을 읽고, 줄 옆의 `+`를 눌러 의견을 남긴 뒤
**Review changes → Request changes**로 한 가지 이상 고쳐 달라고 요청합니다.

**⑦ 수정 반영 (작업자)** — 같은 Branch에서 고치고 다시 Push하면 PR에 Commit이 더해집니다.

```bash
git add members/<내 GitHub 아이디>.md
git commit -m "#1 fix: 리뷰 반영"
git push
```

**⑧ Approve와 Squash Merge (주인)** — **Review changes → Approve**로 승인하고,
PR 아래 Merge 버튼의 화살표에서 **Squash and merge**를 골라 합칩니다.
`Closes #1`을 적었다면 Issue가 함께 닫힙니다.

**⑨ 마무리 (작업자)** — 내 컴퓨터의 `main`을 최신으로 맞춥니다.

```bash
git switch main
git pull
```

## 2. 실습 2 — Conflict 만들고 풀기

이번에는 한 Repository에서 **두 사람이 모두 작업자**가 됩니다. 둘 다 `team.md`의 **같은 줄**을 고칩니다.

1. 각자 Issue를 만들고 Branch를 엽니다. 예: `feat/#2-team-name` · `feat/#3-team-name`
2. 각자 `team.md`의 `팀 이름:` 줄을 **서로 다른 이름**으로 고쳐 Commit하고 Push한 뒤 PR을 만듭니다.
3. 먼저 올라온 PR을 주인이 Squash Merge합니다.
4. 나중 PR에는 «This branch has conflicts» 표시가 뜹니다. 그 PR의 작업자가 내 컴퓨터에서 풉니다.

   ```bash
   git switch main
   git pull                       # 먼저 합쳐진 내용을 받는다
   git switch feat/#3-team-name
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

   남길 내용을 정해 한 줄로 고치고, `<<<<<<<` · `=======` · `>>>>>>>` 줄을 모두 지웁니다.

6. 해결을 기록하고 다시 올립니다. PR의 Conflict 표시가 사라지면 Squash Merge합니다.

   ```bash
   git add team.md
   git commit -m "#3 fix: team.md Conflict 해결"
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

## 완료 체크리스트

- [ ] Issue를 만들었다
- [ ] Issue 번호로 Branch를 만들었다
- [ ] Commit을 두 번 이상 남겼다
- [ ] Pull Request를 만들고 Reviewer를 지정했다
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

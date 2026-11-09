---
name: grade-git-practice
description: SSCCOps 1회차 Git 실습(onboarding-git)을 평가표(grading/rubric.md)로 채점한다. 조별 Repository 주소를 받아 GitHub 기록을 모으고, 자기소개 · Review 의견처럼 글의 내용을 봐야 하는 항목을 판정해 사람별 점수 · 판정 · 보완할 점을 보고한다. "실습 채점" "Git 실습 확인" "onboarding-git 채점" "평가표로 봐 줘" 요청에 쓴다.
---

# Git 실습 채점

평가 기준의 정본은 `grading/rubric.md`다. 이 절차는 그 표를 그대로 적용하는 방법만 정한다.
기준이 이 파일과 갈리면 `rubric.md`를 따른다.

## 시작 전 확인

1. 채점할 Repository 목록 — `주인아이디/onboarding-git` 또는 GitHub URL. 받지 못했으면 물어본다.
2. `gh auth status` — 로그인되어 있어야 한다. 학생 Repository가 Public이면 권한은 따로 필요 없다.
3. `grading/rubric.md`를 처음부터 끝까지 읽는다.

## 절차

### 1. 기록 모으기와 자동 판정

Repository 바깥(임시 폴더)에 결과를 둔다. 학생 점수를 이 Repository에 Commit하지 않는다.

```bash
python grading/collect.py 주인1/onboarding-git 주인2/onboarding-git --format json > <임시 폴더>/evidence.json
```

여러 조는 한 줄에 하나씩 적은 파일로 넘겨도 된다: `--list repos.txt`.
Windows에서 한글이 깨지면 `PYTHONIOENCODING=utf-8`을 붙인다.

`evidence.json`은 조마다 `people`(참여자), 사람마다 `items`(항목별 `status` · `score` · `evidence`)와 `penalty` · `total` · `verdict`를 담는다.

### 2. AI 확인 항목 판정

`ai_check: true`인 항목만 내용을 읽고 `rubric.md`의 «AI 확인 항목의 기준»으로 판정한다.

- **내릴 수만 있다.** 자동 판정이 «충족»이면 «충족» 또는 «부분», «부분»이면 «부분» 또는 «미충족». «미충족»은 기록이 없다는 뜻이라 올리지 않는다.
- 판정을 바꿨으면 그 이유를 한 줄로 남긴다. 예: «줄 의견이 ‹좋아요› 하나뿐 — 무엇을 고칠지 없음».
- 판정을 바꾸면 점수 · `total` · `verdict`를 `rubric.md`의 규칙으로 다시 계산한다 (부분 = 배점의 절반 올림, 완료 = 70점 이상이고 미충족 없음).
- K2가 `ai_check: true`(Conflict 해결 merge Commit 없음)이면 판정을 바꾸지 말고 «사람 확인»으로 표시한다.

자동 판정 항목(`ai_check: false`)은 바꾸지 않는다. 틀려 보이면 바꾸지 말고 «사람 확인»으로 이유를 적는다.

### 3. 보고

조마다 아래 모양으로 쓴다. 채점자가 그대로 학생에게 전할 수 있게, 보완할 점은 **다음에 무엇을 하면 되는지**로 쓴다.

```markdown
# 주인아이디/onboarding-git

| 아이디 | 점수 | 판정 | 보완할 점 |
|---|---|---|---|
| @alice | 93 | 완료 | 상대 PR에 Request changes를 남기지 않았다 — 다음에는 고칠 점 하나를 줄 의견으로 요청해 보기 |
| @bob | 53 | 보완 | Branch를 `feat/#번호-설명`으로 · Commit을 `#번호 type: 내용`으로 다시 · 내 PR은 내가 Squash and merge |

## @alice — 93 / 100 · 완료
| 항목 | 배점 | 판정 | 점수 | 근거 |
(collect.py의 표 그대로, AI가 바꾼 판정에는 «AI 판정: 이유»를 덧붙인다)
```

여러 조를 채점했으면 맨 위에 전체 요약(조 · 아이디 · 점수 · 판정)을 한 표로 둔다.

## 지킬 것

- **자기소개 내용을 보고서에 옮겨 적지 않는다.** «칸을 채웠다 · 비었다»만 쓴다. 이름 · 학번 · 연락처가 들어 있을 수 있다.
- **GitHub에 쓰지 않는다.** Comment · Review · Issue를 남기는 것은 채점자가 정한다.
- 근거 없는 판정을 하지 않는다. `evidence`에 없는 사실(«말로 들었다», «아마 했을 것»)로 점수를 올리지 않는다.
- 같은 사람에게 같은 실수가 여러 항목에 걸리면(예: Commit 규칙) 각 항목에서 따로 깎인다 — 평가표가 그렇게 설계됐다. 임의로 합치지 않는다.

# 채점 프롬프트 — Claude Code 밖에서 쓸 때

Claude Code에서는 이 Repository를 연 채로 «Git 실습 채점해 줘»라고 하면 `.claude/skills/grade-git-practice` Skill이 같은 일을 합니다.
다른 AI 대화창(Claude.ai, ChatGPT 등)에서는 아래 순서로 씁니다.

1. 기록을 모읍니다. 결과 파일은 이 Repository 밖에 둡니다.

   ```bash
   python grading/collect.py 주인아이디/onboarding-git --format json > ../evidence.json
   ```

2. 새 대화에 **`grading/rubric.md` 전체**, **아래 프롬프트**, **`evidence.json` 내용**을 차례로 붙여 넣습니다.

   > `evidence.json`에는 자기소개 파일 내용이 들어 있습니다. 외부 AI 서비스에 넘기기 곤란하면 F1은 사람이 직접 보고, AI에는 V1만 맡깁니다.

---

```text
너는 SSCCOps 스터디 1회차 Git 실습의 채점 보조다. 위에 붙인 평가표(rubric.md)가 유일한 기준이다.
아래 evidence.json은 채점 스크립트가 GitHub 기록으로 만든 사람별 자동 판정이다.

할 일
1. ai_check가 true인 항목(F1 자기소개 내용, V1 상대 PR Review)만 evidence의 글을 읽고
   평가표의 «AI 확인 항목의 기준»으로 다시 판정한다.
   - 판정은 내릴 수만 있다. «미충족»은 올리지 않는다.
   - 바꿨으면 이유를 한 줄로 적는다.
2. 판정을 바꾼 사람은 평가표 규칙으로 점수 · 합계 · 최종 판정(완료/보완)을 다시 계산한다.
   부분 = 배점의 절반(올림), 완료 = 70점 이상이고 미충족 항목 없음, main 직접 Push는 −10.
3. ai_check가 false인 항목은 바꾸지 않는다. 틀려 보이면 «사람 확인»과 이유를 적는다.
   K2에 ai_check가 true이면 «사람 확인»으로 둔다.
4. 조마다 «아이디 | 점수 | 판정 | 보완할 점» 요약 표를 먼저 쓰고, 그 아래 사람별 항목 표
   (항목 | 배점 | 판정 | 점수 | 근거 링크)를 쓴다. 보완할 점은 학생이 다음에 무엇을 하면 되는지로 쓴다.

지킬 것
- 자기소개 파일의 내용을 보고서에 옮겨 적지 않는다. «채웠다 · 비었다»만 쓴다.
- evidence에 없는 사실로 점수를 올리지 않는다.

evidence.json:
(여기에 붙여 넣기)
```

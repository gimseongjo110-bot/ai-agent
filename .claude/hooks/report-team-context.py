import json
import sys

context = """[report-team 자동 인식]
이 프로젝트 세션에는 리포트-팀 에이전트 3종이 구성되어 있습니다.

팀 구성원 (subagent_type 값):
  - market-research-analyst : 웹검색 기반 시장조사 전문 에이전트
  - report-writer           : 구조화된 보고서 작성 전문 에이전트
  - report-reviewer         : 5단계 품질 검수 전문 에이전트

에이전트 파일 경로: C:\\Users\\SBS\\Desktop\\agetn_sj\\.claude\\agents\\

팀 활성화 워크플로우:
  1. TeamCreate(team_name="리포트-팀") 으로 팀 생성
  2. Agent tool 에 subagent_type 지정하여 병렬 또는 순차 실행
  3. 권장 작업 순서: market-research-analyst -> report-writer -> report-reviewer
  4. 완료 후 TeamDelete() 로 팀 해산

환경: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 활성화됨"""

output = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context
    }
}

sys.stdout.reconfigure(encoding="utf-8")
print(json.dumps(output, ensure_ascii=False, indent=2))

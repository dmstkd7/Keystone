import os
import json
import sys
from google import genai
from google.genai import types

# 1. 환경 변수 확인
api_key = os.environ.get("GEMINI_API_KEY")
issue_body = os.environ.get("ISSUE_BODY", "")
issue_title = os.environ.get("ISSUE_TITLE", "경영진단 정보 추가")
issue_number = os.environ.get("ISSUE_NUMBER", "0")

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY가 Secrets에 설정되어 있지 않습니다.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# 2. 기존 마스터 DB 읽기
db_filepath = "_data/diagnostics.json"
existing_data = []

if os.path.exists(db_filepath):
    try:
        with open(db_filepath, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except Exception as e:
        print(f"⚠️ 기존 DB 읽기 실패: {e}")

# 3. Gemini 프롬프트 작성
prompt = f"""
당신은 최고 경영컨설팅 지식관리(KM) 수석 파트너입니다.
제공된 기존 DB와 새로 들어온 이슈 데이터를 비교 및 분석하여 중복을 제거하고 통합된 마스터 DB를 생성하세요.

[기존 경영진단 DB]
{json.dumps(existing_data, ensure_ascii=False, indent=2)}

[신규 입력 데이터 - Issue #{issue_number}]
제목: {issue_title}
내용: {issue_body}

[수행 규칙]
1. 기존 DB와 신규 데이터를 비교하여 중복 내용은 통합하고, 덧붙일 제언이나 체크리스트는 추가하세요.
2. 표준 카테고리 4가지 중 하나로 분류하세요:
   - "경영전략 (Strategy)"
   - "운영/프로세스 (Operations)"
   - "조직/리더십 (Organization & Style)"
   - "재무/자본배분 (Finance & Capital)"
3. 반드시 아래의 JSON 구조로만 출력하세요.

JSON 예시:
[
  {{
    "category": "경영전략 (Strategy)",
    "items": [
      {{
        "title": "진단 항목 명칭",
        "priority": "HIGH",
        "description": "진단 개요 및 보완 내용",
        "checklists": [
          "점검 체크리스트 1"
        ]
      }}
    ]
  }}
]
"""

# 4. API 호출 및 파일 저장
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )

    updated_db = json.loads(response.text)
    os.makedirs("_data", exist_ok=True)
    with open(db_filepath, "w", encoding="utf-8") as f:
        json.dump(updated_db, f, ensure_ascii=False, indent=2)

    print("✅ 성공적으로 마스터 DB가 업데이트되었습니다!")

except Exception as e:
    print(f"❌ API 실행 에러: {e}")
    sys.exit(1)

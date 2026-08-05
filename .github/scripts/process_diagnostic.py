import os
import json
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
issue_body = os.environ.get("ISSUE_BODY", "")
issue_title = os.environ.get("ISSUE_TITLE", "경영진단 정보 추가")
issue_number = os.environ.get("ISSUE_NUMBER", "0")

client = genai.Client(api_key=api_key)

# 1. 기존 누적 데이터(Master DB) 읽어오기
db_filepath = "_data/diagnostics.json"
existing_data = []

if os.path.exists(db_filepath):
    try:
        with open(db_filepath, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except Exception as e:
        print(f"기존 DB 읽기 실패 (새 데이터로 시작합니다): {e}")

# 2. Gemini에게 기존 DB + 신규 데이터 병합 요청
prompt = f"""
당신은 맥킨지(McKinsey) 및 BCG 출신의 최고 경영컨설팅 지식관리(KM) 수석 파트너입니다.
우리 시스템은 경영진단 지식을 누적/통합 관리하는 마스터 DB를 운용하고 있습니다.

[기존 누적 경영진단 DB (JSON)]
{json.dumps(existing_data, ensure_ascii=False, indent=2)}

[새로 입력된 전문가 데이터 (Issue #{issue_number})]
제목: {issue_title}
내용: {issue_body}

[수행 지침]
1. 새로 들어온 데이터를 기존 DB와 비교 분석하세요.
2. **중복 제거 및 통합 (De-duplication & Merge)**: 
   - 기존 DB에 이미 존재하는 아이템이나 체크리스트는 중복 생성하지 마세요.
   - 신규 내용이 기존 항목을 보완하는 경우, 기존 항목의 설명(description)이나 체크리스트(checklists)에 통합하여 덧붙이세요.
3. **카테고리 표준화**: 모든 아이템은 아래 4개 표준 카테고리 중 하나에 분류하세요:
   - "경영전략 (Strategy)"
   - "운영/프로세스 (Operations)"
   - "조직/리더십 (Organization & Style)"
   - "재무/자본배분 (Finance & Capital)"
4. **결과 출력 형식**: 반드시 아래 구조를 가진 JSON 배열 형태로만 응답하세요.

JSON 구조 예시:
[
  {{
    "category": "경영전략 (Strategy)",
    "items": [
      {{
        "title": "진단 아이템 이름",
        "priority": "HIGH", 
        "description": "상세 진단 개요 및 보완된 설명",
        "checklists": [
          "체크리스트 항목 1",
          "체크리스트 항목 2"
        ]
      }}
    ]
  }}
]
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction="당신은 데이터 통합 시스템입니다. 기존 데이터와 신규 데이터를 병합하여 중복 없는 최신 JSON 마스터 DB를 출력하세요."
    ),
)

# 3. 정제된 최신 데이터를 _data/diagnostics.json에 저장
try:
    updated_db = json.loads(response.text)
    os.makedirs("_data", exist_ok=True)
    with open(db_filepath, "w", encoding="utf-8") as f:
        json.dump(updated_db, f, ensure_ascii=False, indent=2)
    print(f"성공적으로 마스터 DB({db_filepath})를 업데이트했습니다!")
except Exception as e:
    print(f"JSON 파싱 오류 발생: {e}")
    print(f"Gemini 원본 응답:\n{response.text}")
    raise e

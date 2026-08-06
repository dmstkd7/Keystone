import os
import json
import sys
import time
from google import genai
from google.genai import types

# 1. 환경 변수 로드
api_key = os.environ.get("GEMINI_API_KEY")
issue_body = os.environ.get("ISSUE_BODY", "")
issue_title = os.environ.get("ISSUE_TITLE", "경영진단 정보 추가")
issue_number = os.environ.get("ISSUE_NUMBER", "0")

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY가 Secrets에 설정되어 있지 않습니다.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# 2. 기존 마스터 DB 안전하게 읽기
db_filepath = "_data/diagnostics.json"
existing_data = []

if os.path.exists(db_filepath) and os.path.getsize(db_filepath) > 0:
    try:
        with open(db_filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                existing_data = json.loads(content)
    except Exception as e:
        print(f"⚠️ 기존 DB 읽기 예외, 빈 데이터로 시작: {e}")

# 3. 경영진단 마스터 DB 병합 프롬프트
prompt = f"""
당신은 최고 경영컨설팅 지식관리(KM) 수석 파트너입니다.
기존 DB와 신규 입력 데이터를 비교해 중복은 통합하고, 신규 체크리스트/제언을 반영한 마스터 DB(JSON)를 반환하세요.

[기존 DB]
{json.dumps(existing_data, ensure_ascii=False)}

[신규 입력 데이터 (Issue #{issue_number})]
제목: {issue_title}
내용: {issue_body}

[규칙]
1. 중복 제거 및 통합
2. 4대 카테고리 중 분류: "경영전략 (Strategy)", "운영/프로세스 (Operations)", "조직/리더십 (Organization & Style)", "재무/자본배분 (Finance & Capital)"
3. JSON 형식만 출력

[JSON 예시]
[
  {{
    "category": "운영/프로세스 (Operations)",
    "items": [
      {{
        "title": "진단 항목 명칭",
        "priority": "HIGH",
        "description": "진단 개요 및 보완 내용",
        "checklists": ["점검 체크리스트 1"]
      }}
    ]
  }}
]
"""

# 4. 최신 지원 모델인 gemini-2.5-flash 호출
candidate_models = ['gemini-2.5-flash', 'gemini-2.5-flash-lite']
success = False

for model_name in candidate_models:
    print(f"🔄 최신 모델 [{model_name}] 호출 시도 중...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        
        res_text = response.text.strip()
        updated_db = json.loads(res_text)
        
        os.makedirs("_data", exist_ok=True)
        with open(db_filepath, "w", encoding="utf-8") as f:
            json.dump(updated_db, f, ensure_ascii=False, indent=2)

        print(f"✅ 성공적으로 마스터 DB가 업데이트되었습니다! (사용 모델: {model_name})")
        success = True
        break

    except Exception as e:
        print(f"❌ 호출 실패 [{model_name}]: {e}")

if not success:
    print("❌ API 호출에 실패했습니다. 에러 로그를 확인해 주세요.")
    sys.exit(1)

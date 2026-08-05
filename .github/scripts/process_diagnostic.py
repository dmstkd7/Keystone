import os
import json
import sys
import time
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

# 2. 기존 마스터 DB 안전하게 읽기
db_filepath = "_data/diagnostics.json"
existing_data = []

if os.path.exists(db_filepath) and os.path.getsize(db_filepath) > 0:
    try:
        with open(db_filepath, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except Exception as e:
        print(f"⚠️ 기존 DB 읽기 실패 (새 DB로 초기화합니다): {e}")

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

# 4. 429 할당량 초과에 대비한 재시도 및 백업 모델 호출 로직
candidate_models = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-1.5-flash']
success = False

for model_name in candidate_models:
    print(f"🔄 모델 [{model_name}] 호출 시도 중...")
    
    # 모델별 최대 3회 대기 후 재시도
    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            
            updated_db = json.loads(response.text)
            os.makedirs("_data", exist_ok=True)
            with open(db_filepath, "w", encoding="utf-8") as f:
                json.dump(updated_db, f, ensure_ascii=False, indent=2)

            print(f"✅ 성공적으로 마스터 DB가 업데이트되었습니다! (사용 모델: {model_name})")
            success = True
            break

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                wait_time = attempt * 20  # 429 에러 발생 시 20초, 40초 대기 후 재시도
                print(f"⚠️ 429 Rate Limit 발생. {wait_time}초 대기 후 재시도합니다... ({attempt}/3)")
                time.sleep(wait_time)
            else:
                print(f"❌ 호출 실패 [{model_name}]: {e}")
                break
                
    if success:
        break

if not success:
    print("❌ 모든 모델 호출 시도가 할당량 초과 또는 에러로 실패했습니다. 잠시 후 이슈를 다시 열어주세요.")
    sys.exit(1)

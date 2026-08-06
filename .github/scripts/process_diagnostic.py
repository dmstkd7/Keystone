import os
import json
import sys
import time
from google import genai
from google.genai import types

# 1. 환경 변수 로드
api_key = os.environ.get("GEMINI_API_KEY")
issue_body = os.environ.get("ISSUE_BODY", "")
issue_title = os.environ.get("ISSUE_TITLE", "IP 경영진단 정보 추가")
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

# 3. 특허 및 경영진단 전용 맞춤형 프롬프트
prompt = f"""
당신은 특허 전략 및 IP 경영컨설팅 지식관리(KM) 수석 파트너입니다.
기존 DB와 새로 들어온 이슈 데이터를 정밀 비교 분석하여 중복된 데이터는 통합/제거하고, 신규 및 보완 포인트를 정제한 최신 마스터 DB(JSON)를 생성하세요.

[기존 마스터 DB]
{json.dumps(existing_data, ensure_ascii=False)}

[신규 입력 데이터 (Issue #{issue_number})]
제목: {issue_title}
내용: {issue_body}

[분류 및 정제 지침]
1. 입력된 모든 데이터는 반드시 다음 **4가지 지정 카테고리**로 분류하세요:
   - "1. 특허 분쟁" (침해, FTO, 경고장, 모니터링, 분쟁 리스크 등)
   - "2. 특허 매입" (외부 특허 매수, 기술 이전, 라이선스 인, 매각/포기 등)
   - "3. 특허 출원" (직무발명, IP-R&D, 명세서 품질, 심의 프로세스, 대리인 관리 등)
   - "4. 경영컨설팅 핵심 체크포인트" (위 내용 기반 경영진단 시 시급히 점검해야 할 전략/조직/예산/실행 가이드라인)

2. 기존 DB와 내용이 중복되거나 유사하면 통합하고, 기존 항목의 description 또는 checklists 항목에 덧붙여 강화하세요.
3. 데이터가 깔끔하게 읽히도록 핵심 문장 위주로 가독성 있게 정리하세요.

[출력 규격 - 반드시 이 JSON 표준 형식만 출력할 것]
[
  {{
    "category": "1. 특허 분쟁",
    "icon": "fa-shield-halved",
    "items": [
      {{
        "title": "진단/관리 항목 명칭",
        "priority": "HIGH",
        "description": "핵심 내용 요약 및 중복 제거된 정제 데이터",
        "checklists": ["체크리스트 1", "체크리스트 2"]
      }}
    ]
  }},
  {{
    "category": "2. 특허 매입",
    "icon": "fa-cart-shopping",
    "items": []
  }},
  {{
    "category": "3. 특허 출원",
    "icon": "fa-file-signature",
    "items": []
  }},
  {{
    "category": "4. 경영컨설팅 핵심 체크포인트",
    "icon": "fa-user-tie",
    "items": []
  }}
]
"""

# 4. 사용 가능한 최신 Gemini 모델 탐색 및 호출
candidate_models = []
try:
    for m in client.models.list():
        m_name = getattr(m, 'name', str(m)).replace("models/", "")
        if any(k in m_name for k in ["flash", "pro"]) and not any(s in m_name for s in ["image", "tts", "live", "audio", "veo"]):
            candidate_models.append(m_name)
except Exception:
    pass

if not candidate_models:
    candidate_models = ['gemini-2.5-flash', 'gemini-2.0-flash']

success = False
for model_name in candidate_models:
    print(f"🔄 모델 [{model_name}] 호출 시도 중...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        
        updated_db = json.loads(response.text.strip())
        os.makedirs("_data", exist_ok=True)
        with open(db_filepath, "w", encoding="utf-8") as f:
            json.dump(updated_db, f, ensure_ascii=False, indent=2)

        print(f"✅ 성공적으로 IP 경영진단 마스터 DB가 업데이트되었습니다! (사용 모델: {model_name})")
        success = True
        break
    except Exception as e:
        print(f"⚠️ [{model_name}] 호출 실패: {e}")

if not success:
    print("❌ API 호출 실패. 에러 로그를 확인하세요.")
    sys.exit(1)

import os
import json
import sys
import time
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
issue_body = os.environ.get("ISSUE_BODY", "")
issue_title = os.environ.get("ISSUE_TITLE", "IP 경영진단 정보 추가")
issue_number = os.environ.get("ISSUE_NUMBER", "0")

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY가 Secrets에 설정되어 있지 않습니다.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

db_filepath = "_data/diagnostics.json"
existing_data = []

if os.path.exists(db_filepath) and os.path.getsize(db_filepath) > 0:
    try:
        with open(db_filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                existing_data = json.loads(content)
    except Exception as e:
        print(f"⚠️ 기존 DB 읽기 예외: {e}")

prompt = f"""
당신은 최고 IP 경영컨설팅 수석 파트너입니다.
기존 마스터 DB와 새로 입력된 이슈 데이터를 비교하여 중복 내용은 통합하고 신규 체크리스트/제언을 반영한 마스터 DB(JSON)를 반환하세요.

[기존 마스터 DB]
{json.dumps(existing_data, ensure_ascii=False)}

[신규 입력 데이터 (Issue #{issue_number})]
제목: {issue_title}
내용: {issue_body}

[수행 지침]
1. 반드시 아래 **4개 지정 카테고리**에 맞추어 통합 분류하세요:
   - "1. 특허 분쟁" (icon: "fa-shield-halved")
   - "2. 특허 매입" (icon: "fa-cart-shopping")
   - "3. 특허 출원" (icon: "fa-file-signature")
   - "4. 경영컨설팅 핵심 체크포인트" (icon: "fa-user-tie")
2. 중복되는 항목은 통합하여 description이나 checklists에 덧붙이고, 새로운 진단 항목은 추가하세요.
3. 표준 JSON 배열 형태로만 정확히 출력하세요.
"""

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

        print(f"✅ 마스터 DB 업데이트 성공! (사용 모델: {model_name})")
        success = True
        break
    except Exception as e:
        print(f"⚠️ [{model_name}] 호출 에러: {e}")

if not success:
    print("❌ API 실행 실패")
    sys.exit(1)

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
당신은 McKinsey, BCG 출신의 IP 조직 및 운영 프로세스 진단 수석 파트너입니다.
기존 마스터 DB와 새로 입력된 이슈 데이터를 분석하여 중복 데이터를 통합하고, 5대 표준 카테고리로 재분류한 최신 마스터 DB(JSON)를 생성하세요.

[기존 마스터 DB]
{json.dumps(existing_data, ensure_ascii=False)}

[신규 입력 데이터 (Issue #{issue_number})]
제목: {issue_title}
내용: {issue_body}

[분류 및 정제 규칙]
1. 입력 데이터를 아래 5개 카테고리로 정밀 분류하세요:
   - "1. 특허 분쟁" (icon: "fa-shield-halved"): 분쟁, FTO, 경고장, 모니터링 관련 현황/정보
   - "2. 특허 매입" (icon: "fa-cart-shopping"): 외부 특허 매수, 기술이전, 라이선스 인/아웃, 포기 관련 현황/정보
   - "3. 특허 출원" (icon: "fa-file-signature"): R&D 연계, IP-Mining, 발명 심의, 출원 관련 현황/정보
   - "4. 특허 관련 정보" (icon: "fa-circle-info"): 기타 IP 일반 현황, 예산, 외부 대리인 평가, 비용 추이 등 일반 정보
   - "5. 경영컨설팅 핵심 체크포인트" (icon: "fa-user-tie"): **모든 핵심 체크리스트 집중 배치**

2. **정보와 체크리스트 분리 규칙**:
   - 1, 2, 3, 4번 카테고리: 체크리스트를 포함하지 말고, 핵심 요약 정보 및 데이터 내용만 `description` 중심으로 서술하세요.
   - 5번 카테고리: 입력된 데이터 전반을 바탕으로 경영진단 관점의 **"전문가 점검 체크리스트(checklists)"**를 몰아서 정리하세요.

3. **5번 카테고리(경영컨설팅) 평가 관점 (McKinsey / BCG Style)**:
   - 개별 특허의 적정 단가나 전문 소송 비용 등 도메인 세부 수치는 평가하지 마세요.
   - 오직 **"IP 전담 조직이 효율적으로 작동하기 위한 프로세스 표준화, 규정 정립, 시스템화, 거버넌스 및 성과 관리 체계가 구축되어 있는가"**의 조직/시스템 운용 관점으로 체크리스트를 도출하세요.

[출력 규격 - JSON 표준 형식만 출력]
[
  {{
    "category": "1. 특허 분쟁",
    "icon": "fa-shield-halved",
    "items": []
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
    "category": "4. 특허 관련 정보",
    "icon": "fa-circle-info",
    "items": []
  }},
  {{
    "category": "5. 경영컨설팅 핵심 체크포인트",
    "icon": "fa-user-tie",
    "items": []
  }}
]
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

        print(f"✅ 5대 카테고리 마스터 DB 업데이트 성공! (사용 모델: {model_name})")
        success = True
        break
    except Exception as e:
        print(f"⚠️ [{model_name}] 호출 에러: {e}")

if not success:
    print("❌ API 실행 실패")
    sys.exit(1)

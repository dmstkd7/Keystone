import os
import json
from datetime import datetime
from google import genai
from google.genai import types

# 환경 변수 로드
api_key = os.environ.get("GEMINI_API_KEY")
issue_body = os.environ.get("ISSUE_BODY", "")
issue_title = os.environ.get("ISSUE_TITLE", "경영진단 리포트")
issue_number = os.environ.get("ISSUE_NUMBER", "0")

client = genai.Client(api_key=api_key)

prompt = f"""
당신은 맥킨지(McKinsey) 및 BCG 출신의 최고 경영진단 컨설팅 전문가입니다.
다음 전문가가 제출한 이슈 데이터를 분석하여 정밀한 경영진단 보고서를 작성해 주세요.

[제출된 데이터]
{issue_body}

다음 3가지 영역을 반드시 포함하여 HTML/Markdown 스타일로 정교하게 작성해 주세요:
1. **기존 자료 대비 중복 내용 및 추가/보완 제언**:
   - 중복된 데이터가 있다면 언급하고, 덧붙이면 좋을 인사이트나 추가 데이터 제언.
2. **카테고리별 분류 정보**:
   - 제출된 정보를 경영학적 프레임워크(예: 전략, 운영, 조직, 재무 등)로 깔끔하게 분류.
3. **[핵심] 전문가용 경영진단 아이템 및 체크리스트**:
   - 맥킨지/BCG 관점에서 시급히 진단해야 할 항목(Item)과 체크리스트(Checklist)를 리스트업.
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction="당신은 전문 경영 컨설턴트입니다. 읽기 쉽고 수석 경영진이 한눈에 파악할 수 있도록 시각적으로 깔끔한 Markdown 보고서를 작성합니다.",
    ),
)

report_content = response.text

# Jekyll 포스트 문서 헤더 생성 (Front Matter)
today = datetime.now().strftime("%Y-%m-%d")
filename_title = issue_title.replace(" ", "-").replace("[진단-요청]", "").strip()
filename = f"_posts/{today}-diagnostic-issue-{issue_number}.md"

front_matter = f"""---
layout: post
title: "{issue_title}"
date: {today}
categories: [경영진단, 리포트]
tags: [Gemini, 맥킨지프레임워크, 이슈-{issue_number}]
---

> 💡 **본 리포트는 Issue #{issue_number}를 기반으로 Gemini 2.5에 의해 자동 생성된 경영진단 보고서입니다.**

---

{report_content}
"""

os.makedirs("_posts", exist_ok=True)
with open(filename, "w", encoding="utf-8") as f:
    f.write(front_matter)

print(f"Successfully generated {filename}")

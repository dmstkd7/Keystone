import os
import json
from datetime import datetime
from google import genai
from google.genai import types

# 환경 변수 로드
api_key = os.environ.get("GEMINI_API_KEY")
issue_body = os.environ.get("ISSUE_BODY", "")
issue_title = os.environ.get("ISSUE_TITLE", "경영진단 요청")
issue_number = os.environ.get("ISSUE_NUMBER", "0")

client = genai.Client(api_key=api_key)

# 단일 텍스트(Raw Data)를 기반으로 맥킨지/BCG 프레임워크 보고서 자동 생성 프롬프트
prompt = f"""
당신은 맥킨지(McKinsey) 및 BCG 출신의 최고 경영컨설팅 수석 파트너입니다.
아래에 경영진단 전문가가 입력한 자유 형식의 데이터(Raw Data)가 있습니다.

[입력된 원본 데이터]
{issue_body}

위 데이터를 바탕으로 다음 3가지 핵심 내용이 포함된 정교한 경영진단 보고서를 작성해 주세요:

1. 🔄 **기존/입력 자료 분석 및 보완 제언**
   - 입력된 자료 내의 중복되거나 대립되는 내용 정리
   - 경영 진단을 완성하기 위해 추가로 수집하거나 덧붙이면 좋을 핵심 정보/지표 제언

2. 📊 **경영학적 프레임워크 분류 (전략/운영/조직/재무 등)**
   - 입력된 무작위 정보들을 보기 쉽게 카테고리별로 구조화하여 정리

3. 🎯 **[핵심] 경영진단 아이템 및 체크리스트 (맥킨지/BCG 관점)**
   - 컨설턴트가 현장에서 바로 점검해야 할 **핵심 진단 아이템** 추출
   - 각 아이템별 **세부 체크리스트(Checklist)** 리스트업 (우선순위 High/Medium 표기)

* 작성 규칙: 
- 웹사이트(Jekyll)에 예쁘게 표기되도록 깔끔한 Markdown 문법과 이모지, 강조 박스(Quote block) 등을 적극 활용하세요.
- 경영진단 아이템 및 체크리스트 섹션은 한눈에 들어오도록 별도의 강조 디자인 느낌으로 작성해 주세요.
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction="당신은 전문 경영 컨설턴트입니다. 읽기 쉽고 가독성이 뛰어난 프리미엄 경영진단 보고서를 생성합니다.",
    ),
)

report_content = response.text

# 웹사이트 게시용 Jekyll 포스트 작성
today = datetime.now().strftime("%Y-%m-%d")
clean_title = issue_title.replace("[진단]", "").strip() or f"경영진단 리포트 #{issue_number}"
filename = f"_posts/{today}-diagnostic-issue-{issue_number}.md"

front_matter = f"""---
layout: post
title: "{clean_title}"
date: {today}
categories: [경영진단]
tags: [Gemini, 맥킨지프레임워크, 이슈-{issue_number}]
---

> 💡 **본 리포트는 Issue #{issue_number}의 입력 데이터를 기반으로 Gemini AI가 분석하여 자동 생성한 경영진단 리포트입니다.**

---

{report_content}
"""

os.makedirs("_posts", exist_ok=True)
with open(filename, "w", encoding="utf-8") as f:
    f.write(front_matter)

print(f"성공적으로 리포트를 생성했습니다: {filename}")

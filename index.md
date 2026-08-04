---
layout: default
title: 경영진단 리포트 목록
---

# 📊 경영진단 전문가 지식보관소

경영진단 전문가들이 입력한 정보를 바탕으로 Gemini AI가 자동 분석한 리포트 목록입니다.

---

## 📝 최신 경영진단 리포트

{% for post in site.posts %}
* **[{{ post.title }}]({{ post.url | relative_url }})** - *{{ post.date | date: "%Y-%m-%d" }}*
{% else %}
 아직 등록된 경영진단 리포트가 없습니다. Issue를 통해 새 진단을 요청해 보세요!
{% endfor %}

---
layout: default
title: "Keystone 경영진단 포털"
---

<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 60px 20px; text-align: center; color: white; border-radius: 0 0 20px 20px; margin-bottom: 40px;">
  <h1 style="font-family: 'Merriweather', serif; font-size: 42px; margin-bottom: 15px; color: #ffffff;">Keystone 경영진단 플랫폼</h1>
  <p style="font-size: 18px; color: #cbd5e1; max-width: 700px; margin: 0 auto 30px auto;">전문가의 데이터와 Gemini AI의 분석이 결합된 맥킨지/BCG 수준의 수석 컨설팅 지식보관소입니다.</p>
  <a href="./categories" style="background: #38bdf8; color: #0f172a; padding: 12px 28px; border-radius: 8px; font-weight: bold; text-decoration: none; display: inline-block;">카테고리별 리포트 탐색하기 ➔</a>
</div>

<div style="max-width: 900px; margin: 0 auto; padding: 0 20px;">
  <h2 style="font-family: 'Merriweather', serif; color: #0f172a; font-size: 26px; border-bottom: 2px solid #0f172a; padding-bottom: 10px;">📋 최신 자동 생성 경영진단 리포트</h2>

  {% for post in site.posts limit:5 %}
    <div class="category-card" style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
      <div>
        <span class="category-badge">{{ post.categories | first | default: "경영진단" }}</span>
        <a href="{{ post.url | relative_url }}" style="font-size: 18px; font-weight: 700; color: #0f172a; text-decoration: none;">{{ post.title }}</a>
      </div>
      <span style="color: #64748b; font-size: 14px;">{{ post.date | date: "%Y-%m-%d" }}</span>
    </div>
  {% else %}
    <p style="color: #64748b; margin-top: 20px;">아직 생성된 리포트가 없습니다. Issue 생성을 통해 새 진단을 시작해 보세요!</p>
  {% endfor %}
</div>

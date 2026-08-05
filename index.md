---
layout: default
title: "Keystone 경영진단 통합 지식보관소"
---

<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 50px 20px; text-align: center; color: white; border-radius: 0 0 20px 20px; margin-bottom: 40px;">
  <h1 style="font-family: 'Merriweather', serif; font-size: 38px; margin-bottom: 15px; color: #ffffff;">Keystone 경영진단 통합 지식보관소</h1>
  <p style="font-size: 17px; color: #cbd5e1; max-width: 750px; margin: 0 auto;">경영진단 전문가들의 노하우를 Gemini AI가 실시간으로 중복 제거 및 재분류하여 유지하는 마스터 진단 프레임워크입니다.</p>
</div>

<div style="max-width: 1000px; margin: 0 auto; padding: 0 20px;">
  
  {% if site.data.diagnostics %}
    {% for cat in site.data.diagnostics %}
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 30px; margin-bottom: 35px; box-shadow: 0 4px 6px rgba(0,0,0,0.03);">
        <h2 style="font-family: 'Merriweather', serif; color: #0f172a; border-bottom: 3px solid #0284c7; padding-bottom: 12px; font-size: 26px; margin-top: 0;">
          {{ cat.category }}
        </h2>

        <div style="display: grid; gap: 20px; margin-top: 20px;">
          {% for item in cat.items %}
            <div style="background: #f8fafc; border-left: 5px solid {% if item.priority == 'HIGH' %}#ef4444{% elsif item.priority == 'MEDIUM' %}#f59e0b{% else %}#10b981{% endif %}; border-radius: 4px 8px 8px 4px; padding: 20px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; color: #0f172a; font-size: 20px; font-weight: 700;">{{ item.title }}</h3>
                <span style="background: {% if item.priority == 'HIGH' %}#fee2e2; color:#991b1b{% elsif item.priority == 'MEDIUM' %}#fef3c7; color:#92400e{% else %}#d1fae5; color:#065f46{% endif %}; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                  우선순위: {{ item.priority }}
                </span>
              </div>
              
              <p style="color: #475569; font-size: 15px; margin-bottom: 15px; line-height: 1.6;">{{ item.description }}</p>

              <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px;">
                <strong style="color: #0369a1; font-size: 14px; display: block; margin-bottom: 8px;">☑️ 전문가 핵심 체크리스트:</strong>
                <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px; line-height: 1.8;">
                  {% for chk in item.checklists %}
                    <li>{{ chk }}</li>
                  {% endfor %}
                </ul>
              </div>
            </div>
          {% endfor %}
        </div>
      </div>
    {% endfor %}
  {% else %}
    <div style="text-align: center; padding: 60px; background: #ffffff; border-radius: 12px; color: #64748b;">
      <h3>아직 수집된 경영진단 지식이 없습니다.</h3>
      <p>GitHub Issue에 경영진단 데이터를 등록하면 Gemini가 첫 마스터 DB를 구축합니다!</p>
    </div>
  {% endif %}

</div>

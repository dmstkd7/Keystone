---
layout: default
title: "Keystone IP 경영진단 통합 대시보드"
---

<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 50px 20px; text-align: center; color: white; border-radius: 0 0 20px 20px; margin-bottom: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
  <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 5px 14px; border-radius: 20px; font-size: 13px; font-weight: bold; border: 1px solid rgba(56, 189, 248, 0.4);">IP & PATENT CONSULTING PORTAL</span>
  <h1 style="font-family: 'Merriweather', serif; font-size: 38px; margin: 15px 0 10px 0; color: #ffffff;">Keystone IP 경영진단 보관소</h1>
  <p style="font-size: 16px; color: #cbd5e1; max-width: 750px; margin: 0 auto; line-height: 1.6;">전문가의 지식을 Gemini AI가 중복 제거하여 4대 핵심 분야(분쟁·매입·출원·컨설팅)로 상시 정제·통합하는 지식 대시보드입니다.</p>
</div>

<div style="max-width: 1050px; margin: 0 auto; padding: 0 20px;">

  {% if site.data.diagnostics %}
    {% for cat in site.data.diagnostics %}
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 32px; margin-bottom: 35px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
        
        <!-- Category Header -->
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 24px;">
          <h2 style="font-family: 'Merriweather', serif; color: #0f172a; font-size: 24px; margin: 0; display: flex; align-items: center; gap: 10px;">
            <i class="fa-solid {{ cat.icon | default: 'fa-folder-open' }}" style="color: #0284c7;"></i>
            {{ cat.category }}
          </h2>
          <span style="background: #f1f5f9; color: #475569; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600;">
            진단 항목: {{ cat.items | size }}개
          </span>
        </div>

        <!-- Items Grid -->
        {% if cat.items and cat.items.size > 0 %}
          <div style="display: grid; gap: 20px;">
            {% for item in cat.items %}
              <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-left: 6px solid {% if item.priority == 'HIGH' %}#ef4444{% elsif item.priority == 'MEDIUM' %}#f59e0b{% else %}#10b981{% endif %}; border-radius: 8px; padding: 22px;">
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                  <h3 style="margin: 0; color: #0f172a; font-size: 19px; font-weight: 700;">{{ item.title }}</h3>
                  <span style="background: {% if item.priority == 'HIGH' %}#fee2e2; color:#991b1b{% elsif item.priority == 'MEDIUM' %}#fef3c7; color:#92400e{% else %}#d1fae5; color:#065f46{% endif %}; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                    중요도: {{ item.priority }}
                  </span>
                </div>

                <p style="color: #334155; font-size: 15px; margin-bottom: 16px; line-height: 1.6; white-space: pre-line;">{{ item.description }}</p>

                {% if item.checklists and item.checklists.size > 0 %}
                  <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px 18px;">
                    <strong style="color: #0284c7; font-size: 14px; display: block; margin-bottom: 8px;">☑️ 전문가 점검 체크리스트:</strong>
                    <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px; line-height: 1.8;">
                      {% for chk in item.checklists %}
                        <li>{{ chk }}</li>
                      {% endfor %}
                    </ul>
                  </div>
                {% endif %}

              </div>
            {% endfor %}
          </div>
        {% else %}
          <p style="color: #94a3b8; font-size: 15px; margin: 0; text-align: center; padding: 20px 0;">이 영역에 등록된 진단 항목이 아직 없습니다.</p>
        {% endif %}

      </div>
    {% endfor %}
  {% else %}
    <div style="text-align: center; padding: 60px; background: #ffffff; border-radius: 12px; color: #64748b; border: 1px solid #e2e8f0;">
      <h3>등록된 IP 경영진단 데이터가 없습니다.</h3>
      <p>GitHub Issue에 데이터를 입력하시면 Gemini가 4대 영역으로 자동 분류하여 구축합니다.</p>
    </div>
  {% endif %}

</div>

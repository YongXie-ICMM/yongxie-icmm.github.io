---
permalink: /
title: "Home"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

Welcome! I am **Yong Xie**, Visiting Professor at **ICMM-CSIC (Madrid, Spain)** and Associate Professor at **Xidian University (China)**.

My research focuses on **low-dimensional materials and devices**, with emphasis on the optical, mechanical, and electronic properties of **2D semiconductors**, and their applications in **optoelectronics, sensing, and AI-enabled scientific instrumentation**.

With 17+ years of research experience across academia and industry, I work at the intersection of **materials science**, **device engineering**, and **AI for Science**.

## Research Interests

- Optical and electronic properties of low-dimensional semiconductors
- 2D materials for optoelectronics and sensing
- AI agents and autonomous workflows for scientific experiments

## Quick Links

- 📄 [Publications](/publications/)
- 🎤 [Talks](/talks/)
- 📰 [Group News](/group-news/)
- 👨‍🏫 [Teaching](/teaching/)
- 📘 [Learning Resources](/learning/)
- 🧾 [Curriculum Vitae](/cv/)

## Latest Highlights

- 🏆 **AgentX-AgentBeats 2026 (UC Berkeley):** our team *MateFin* won **1st place (tie)** in the Web Agent track. [Read more](/group-news/)
- 🧪 **Recent publications (2026):** LED-based reconstructive spectroscopy in *Applied Physics Letters*, submicron microdevice patterning in *Nanoscale Advances*, and a News & Views article on sliding ferroelectricity in *Nature Nanotechnology*. [Publications](/publications/)
- 🎓 **Student & group updates:** invited talks, thesis defenses, and academic activities. [Group News](/group-news/)

## Selected Publications

{% assign selected_pubs = site.publications | where: 'selected', true | sort: 'date' | reverse %}
{% for post in selected_pubs %}
- **{{ post.title }}** ({{ post.date | date: "%Y" }})  
  {% if post.venue %}<em>{{ post.venue }}</em>{% endif %}{% if post.link %} · [Link]({{ post.link }}){% endif %}{% if post.paperurl %} · [PDF]({{ post.paperurl }}){% endif %}
{% endfor %}

➡️ [View full publications list](/publications/)

## Recent Talks

{% assign recent_talks = site.talks | sort: 'date' | reverse %}
{% for post in recent_talks limit:3 %}
- **{{ post.title }}** ({{ post.date | date: "%Y-%m" }}){% if post.venue %} — {{ post.venue }}{% endif %}{% if post.location %}, {{ post.location }}{% endif %}
{% endfor %}

➡️ [View all talks](/talks/)

## Contact

- Email: [xieyong.nwpu@gmail.com](mailto:xieyong.nwpu@gmail.com)
- Google Scholar: [Profile](https://scholar.google.com/citations?user=bX_QzCQAAAAJ&hl)
- LinkedIn: [Yong Xie](https://www.linkedin.com/in/yong-xie-2694a315)

---

## Visitor Statistics

<p style="font-size: 0.95em; color: #666;">
  <span id="busuanzi_container_page_pv">👀 Page views: <span id="busuanzi_value_page_pv">--</span></span>
  &nbsp;|&nbsp;
  <span id="busuanzi_container_page_uv">🧑‍🤝‍🧑 Unique visitors: <span id="busuanzi_value_page_uv">--</span></span>
</p>

<script async src="https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>







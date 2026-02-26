import os, re, shutil, subprocess, sys
from datetime import datetime

REPO = r"D:\Git\yongxie-icmm.github.io"
PAGES_DIR = os.path.join(REPO, "_pages")
DATA_DIR  = os.path.join(REPO, "_data")
IMAGES_DIR= os.path.join(REPO, "images")
NAV = os.path.join(DATA_DIR, "navigation.yml")
PAGE = os.path.join(PAGES_DIR, "group-news.md")

SRC_DIR = r"D:\Git\Source"
SRC_IMAGE_FLATLANDS = os.path.join(SRC_DIR, "Flatlands_Invited_talk.png")
TARGET_IMAGE_FLATLANDS = "2025-flatlands-invited-talk.png"

FRONT_MATTER = """---
layout: archive
title: "Group NEWs"
permalink: /group-news/
author_profile: true
---
"""

def force_breaks(s: str) -> str:
    # 1) 把行内的 \n 强制变成 <br>  2) 把全角竖线“｜”前面加换行
    s = s.replace("\r\n", "\n")
    s = s.replace("｜", "<br>｜")
    s = re.sub(r"\n+", lambda m: "<br>\n"*len(m.group(0)), s)
    return s

# 你的英文新闻（可继续增减）
NEWS = [
    ("2025.09",
     "• [2025.09] Our manuscript was accepted by **APL Machine Learning** 🎉 — first time receiving an acceptance notice over a weekend! "
     "Many thanks to **Yang Liu**, **Qianjie Lei**, **Xiaolong He**, and all teammates for the hard work. "
     "Although a fully *human-out-of-the-loop* autonomous lab is still ahead, we have validated in class that this teaching experiment design works very well."),
    ("2025.09",
     "• [2025.09] We thank the organizers of **Flatlands Beyond Graphene 2025**. "
     "Prof. Yong Xie delivered an **invited talk** and chaired the Tuesday evening **Shotgun Session** (Milan, Italy).\n"
     f"![Flatlands Beyond Graphene 2025](/images/{TARGET_IMAGE_FLATLANDS})"),
    ("2025.08",
     "• [2025.08] Delighted to host **Prof. Eduardo R. Hernández** and **Prof. Andres Castellanos-Gomez** during the hot summer. "
     "They shared deep theoretical insights and practical guidance with our students. "
     "Special thanks to graduate students **Qianjie Lei** and **Yang Liu** for their dedicated support. "
     "*Seeds of research often sprout quietly during conversations.*"),
    ("2025.07",
     "• [2025.07] Our paper on AI agents for instrument control was selected as a **back cover** in *Small Structures*. "
     "The paper is online and has been featured by **Nanowerk Spotlight**.\n"
     "｜Paper DOI: https://doi.org/10.1002/sstr.202500173\n"
     "｜Back cover: https://onlinelibrary.wiley.com/doi/abs/10.1002/sstr.70047\n"
     "｜Media: https://www.nanowerk.com/spotlight/spotid=67169.php"),
    ("2025.07",
     "• [2025.07] At the quantum meeting organized by **Prof. Xi Chen (ICMM-CSIC)**, "
     "**Prof. Yu Shi (Fudan University)** highly commended our work. "
     "Many thanks to Prof. Chen for organizing a top-tier meeting!"),
    ("2025.06",
     "• [2025.06] Our manuscript on **AI agents for scientific instrument control** was accepted by *Small Structures*. "
     "The work uses LLM tools to control instruments and, to our knowledge, provides the **first systematic report** of such an AI agent."),
    ("2025.06",
     "• [2025.06] Congratulations to master’s students **Kexin He**, **Yizhe Xue**, and **Xiaolong He** on successfully defending their theses!"),
    ("2024.05",
     "• [2024.05] Congratulations to master’s students **Haoran Li**, **Ziwei Dang**, and **Haitao Yang** on successful thesis defenses!"),
    ("2024.05",
     "• [2024.05] Congratulations to two collaborative papers (advised by **Dr. Nan Zhou**) accepted in **Small** and **Small Structures**.\n"
     "Small Structures: https://onlinelibrary.wiley.com/doi/full/10.1002/sstr.202400062 (Nan Zhou, Haoran Li)\n"
     "Small: https://onlinelibrary.wiley.com/doi/10.1002/smll.202400311 (Nan Zhou, Ziwei Dang)"),
    ("2024.02",
     "• [2024.02.20] Our *Nano Letters* paper was accepted: https://pubs.acs.org/doi/10.1021/acs.nanolett.3c04815. "
     "Congratulations to **Haitao Yang**, **Ruiqi Hu**, **Heng Wu**, **Xiaolong He**, **Yizhe Xue**, **Kexin He**, **Wenshuai Hu**, and all collaborators. "
     "Equal first authors: **Haitao Yang**, **Ruiqi Hu**, **Heng Wu**, **Xiaolong He**; "
     "Corresponding authors: **Yong Xie**, **Ping-Heng Tan**, **Eduardo R. Hernández**, **Yan Zhou**."),
    ("2023.10",
     "• [2023.10.29] Our team won **First Prize** in the 2nd China Graduate *Dual-Carbon* Innovation & Creativity Competition (finals). "
     "Prof. Yong Xie received the **Outstanding Advisor** award."),
    ("2023.10",
     "• [2023.10.23] Our *Small Methods* paper was selected as a **cover**. Congratulations!"),
    ("2023.06",
     "• [2023.06.27] Our work was highlighted in **News & Views**: https://www.oejournal.org/article/doi/10.29026/oea.2023.230077"),
    ("2023.03",
     "• [2023.03.29] Our study received a **cover highlight**: https://www.oejournal.org/oea/article/2023/3"),
    ("2023.02",
     "• [2023.02.20] Media coverage by **Nanowerk**: https://www.nanowerk.com/spotlight/spotid=62406.php"),
    ("2023.02",
     "• [2023.02] Prof. Yong Xie presented a poster at **GEFES 2023**."),
    ("2023.01",
     "• [2023.01] Prof. Yong Xie presented a poster at **MEMS 2023**."),
    ("2023.01",
     "• [2023.01] Prof. Yong Xie served on the **Organizers & Advisory Committee** of **#NanoSeries2023**. "
     "Conference link: https://nanoseriesiac.com/"),
    ("2023.01",
     "• [2023.01.10] Our work was selected as a **back cover**: https://onlinelibrary.wiley.com/doi/abs/10.1002/admt.202370005"),
    ("2023.01",
     "• [2023.01.06] Media coverage: https://www.eurekalert.org/news-releases/975945  "
     "https://www.alphagalileo.org/en-gb/Item-Display/ItemId/229134"),
    ("2022.12",
     "• [2022.12.16] Media coverage: https://www.nanowerk.com/spotlight/spotid=62040.php"),
    ("2022.11",
     "• [2022.11.01] Our paper in **Opto-Electronic Advances** (**CAS Tier-1 (Top)**) was selected as a **cover**."),
    ("2022.10",
     "• [2022.10.25] Two good news in one day! "
     "A paper with **Wenshuai Hu** et al. was accepted by **Nano Research** (**CAS Tier-1 (Top)**); "
     "our collaborative paper with **Prof. Guoqiang Wu (Wuhan University)** was accepted by **MEMS 2023**. Congratulations!"),
    ("2022.09",
     "• [2022.09.26] A paper (corresponding author: **Yong Xie**) was accepted by **Opto-Electronic Advances** (**CAS Tier-1**)."),
    ("2022.09",
     "• [2022.09.07] Congratulations to **Wenliang Zhang** on his successful PhD defense (co-supervised by Andres Castellanos-Gomez and Yong Xie)! "
     "He will join **Shaanxi University of Science & Technology** as an Associate Professor, and received the highest thesis honor **Cum laude**."),
    ("2022.09",
     "• [2022.09.07] A collaborative paper was accepted by **Nano Letters**. Congratulations!"),
    ("2022.09",
     "• [2022.09.06] Our work is highlighted on **Kudos**: https://www.growkudos.com/publications/10.1063%25252F5.0096190/reader"),
    ("2022.08",
     "• [2022.08.08] A collaborative paper was accepted by **Advanced Materials Technologies**: "
     "https://onlinelibrary.wiley.com/doi/10.1002/admt.202201091"),
    ("2022.08",
     "• [2022.08.05] Our paper (first author: **Wenshuai Hu**; co-authors: **Kexin He**, **Xiaolong He**, **Yan Bai**, **Chenyang Liu**, etc.; "
     "corresponding author: **Yong Xie**) was accepted by **Journal of Applied Physics** "
     "(https://aip.scitation.org/doi/full/10.1063/5.0096190). Congratulations!")
]

def update_navigation():
    nav = os.path.join(DATA_DIR, "navigation.yml")
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(nav):
        with open(nav, "w", encoding="utf-8") as f:
            f.write('- title: "Group NEWs"\n  url: /group-news/\n')
        return
    with open(nav, "r", encoding="utf-8") as f: content = f.read()
    orig = content
    content = re.sub(r'title:\s*["\']?Portfolio["\']?', 'title: "Group NEWs"', content, flags=re.I)
    content = re.sub(r'url:\s*/portfolio/?', 'url: /group-news/', content, flags=re.I)
    if 'url: /group-news/' not in content:
        if not content.endswith("\n"): content += "\n"
        content += '- title: "Group NEWs"\n  url: /group-news/\n'
    if content != orig:
        with open(nav, "w", encoding="utf-8") as f: f.write(content)

def ensure_page():
    os.makedirs(PAGES_DIR, exist_ok=True)
    if not os.path.exists(PAGE):
        with open(PAGE, "w", encoding="utf-8") as f: f.write(FRONT_MATTER+"\n")
    else:
        with open(PAGE, "r", encoding="utf-8") as f: txt = f.read()
        if not txt.strip().startswith("---") or "permalink: /group-news/" not in txt:
            body = re.sub(r"^---.*?---\s*", "", txt, flags=re.DOTALL)
            with open(PAGE, "w", encoding="utf-8") as f:
                f.write(FRONT_MATTER + "\n" + body)

def copy_flatlands_image():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    if os.path.exists(SRC_IMAGE_FLATLANDS):
        dst = os.path.join(IMAGES_DIR, TARGET_IMAGE_FLATLANDS)
        shutil.copy2(SRC_IMAGE_FLATLANDS, dst)

def render_news_grouped():
    parsed = []
    for ym, md in NEWS:
        y, m = ym.split(".")
        parsed.append((int(y), int(m), force_breaks(md)))
    parsed.sort(key=lambda t: (t[0], t[1]), reverse=True)
    out = []
    curr = None
    for y, m, md in parsed:
        if curr != y:
            out.append(f"\n## {y}\n")
            curr = y
        out.append(md + "\n")
    return "\n".join(out).strip() + "\n"

def rebuild_page():
    with open(PAGE, "r", encoding="utf-8") as f: txt = f.read()
    m = re.match(r"^---.*?---\s*", txt, flags=re.DOTALL)
    fm = m.group(0) if m else FRONT_MATTER
    body = render_news_grouped()
    with open(PAGE, "w", encoding="utf-8") as f: f.write(fm + "\n" + body)

def git_push():
    subprocess.run(["git", "add", "_data/navigation.yml", "_pages/group-news.md", "images/"], cwd=REPO, check=True)
    subprocess.run(["git", "commit", "-m", "Group NEWs: enforce line breaks with <br>, update entries"], cwd=REPO, check=True)
    subprocess.run(["git", "push", "origin", "master"], cwd=REPO, check=True)

def main():
    os.chdir(REPO)
    update_navigation()
    ensure_page()
    copy_flatlands_image()
    rebuild_page()
    git_push()
    print("✅ Done. Check /group-news/")

if __name__ == "__main__":
    main()

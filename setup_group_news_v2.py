import os, re, shutil, subprocess, sys
from datetime import datetime

# ================= CONFIG =================
REPO = r"D:\Git\yongxie-icmm.github.io"
PAGES_DIR = os.path.join(REPO, "_pages")
DATA_DIR  = os.path.join(REPO, "_data")
IMAGES_DIR= os.path.join(REPO, "images")
NAV = os.path.join(DATA_DIR, "navigation.yml")
PAGE = os.path.join(PAGES_DIR, "group-news.md")

SRC_DIR = r"D:\Git\Source"
SRC_IMAGE_FLATLANDS = os.path.join(SRC_DIR, "Flatlands_Invited_talk.png")
TARGET_IMAGE_FLATLANDS = "2025-flatlands-invited-talk.png"  # copied into /images/

FRONT_MATTER = """---
layout: archive
title: "Group NEWs"
permalink: /group-news/
author_profile: true
---
"""

# --------------- ENGLISH NEWS ITEMS ---------------
# Each item: (date "YYYY.MM", Markdown string)
NEWS = [
    ("2025.09",
     "• [2025.09] Our manuscript was accepted by **APL Machine Learning** 🎉 — first time receiving an acceptance notice over a weekend! "
     "Many thanks to **Yang Liu**, **Qianjie Lei**, **Xiaolong He**, and all teammates for the hard work. "
     "Although a fully *human-out-of-the-loop* autonomous lab is still ahead, we have validated in class that this teaching experiment design works very well."),
    ("2025.09",
     "• [2025.09] We thank the organizers of **Flatlands Beyond Graphene 2025**. "
     "Prof. Yong Xie delivered an **invited talk** and chaired the Tuesday evening **Shotgun Session** (Milan, Italy).\n\n"
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
     "• [2022.11.01] Our paper in **Opto-Electronic Advances** (CAS Zone 1 Top) was selected as a **cover**."),
    ("2022.10",
     "• [2022.10.25] Two good news in one day! "
     "A paper with **Wenshuai Hu** et al. was accepted by **Nano Research** (CAS Zone 1 Top); "
     "our collaborative paper with **Prof. Guoqiang Wu (Wuhan University)** was accepted by **MEMS 2023**. Congratulations!"),
    ("2022.09",
     "• [2022.09.26] A paper (corresponding author: **Yong Xie**) was accepted by **Opto-Electronic Advances** (CAS Zone 1)."),
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
     "• [2022.08.05] Our paper (first author: **Wenshuai Hu**; co-authors: **Kexin He**, **Xiaolong He**, **Yan Bai**, **Chenyang Liu**, **Chenyang Liu**, etc.; "
     "corresponding author: **Yong Xie**) was accepted by **Journal of Applied Physics** "
     "(https://aip.scitation.org/doi/full/10.1063/5.0096190). Congratulations!")
]

# --------------- HELPERS ---------------
def ensure_dirs():
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

def update_navigation():
    """Rename 'Portfolio' to 'Group NEWs' (url -> /group-news/). Create if missing."""
    if not os.path.exists(NAV):
        with open(NAV, "w", encoding="utf-8") as f:
            f.write('- title: "Group NEWs"\n  url: /group-news/\n')
        print("✅ Created navigation.yml with Group NEWs.")
        return
    with open(NAV, "r", encoding="utf-8") as f:
        content = f.read()
    orig = content
    content = re.sub(r'title:\s*["\']?Portfolio["\']?', 'title: "Group NEWs"', content, flags=re.I)
    content = re.sub(r'url:\s*/portfolio/?', 'url: /group-news/', content, flags=re.I)
    if 'url: /group-news/' not in content:
        if not content.endswith("\n"): content += "\n"
        content += '- title: "Group NEWs"\n  url: /group-news/\n'
    if content != orig:
        with open(NAV, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ navigation.yml updated.")
    else:
        print("ℹ️ navigation.yml already OK.")

def ensure_page_and_front_matter():
    """Ensure group-news.md exists and has proper front matter."""
    if not os.path.exists(PAGE):
        with open(PAGE, "w", encoding="utf-8") as f:
            f.write(FRONT_MATTER + "\n")
        print("✅ Created group-news.md")
    else:
        with open(PAGE, "r", encoding="utf-8") as f:
            txt = f.read()
        if not txt.strip().startswith("---") or "permalink: /group-news/" not in txt:
            # replace any front matter with ours
            body = re.sub(r"^---.*?---\s*", "", txt, flags=re.DOTALL)
            with open(PAGE, "w", encoding="utf-8") as f:
                f.write(FRONT_MATTER + "\n" + body)
            print("✅ Fixed front matter.")

def copy_flatlands_image():
    """Copy Flatlands image if present."""
    if not os.path.exists(SRC_IMAGE_FLATLANDS):
        print(f"⚠️ Image not found: {SRC_IMAGE_FLATLANDS} (skip copy)")
        return
    dst = os.path.join(IMAGES_DIR, TARGET_IMAGE_FLATLANDS)
    shutil.copy2(SRC_IMAGE_FLATLANDS, dst)
    print(f"✅ Copied image -> {dst}")

def render_news_grouped_by_year():
    """Return Markdown body grouped by year, newest first."""
    # Parse to tuples (year, ym, md)
    parsed = []
    for ym, md in NEWS:
        year = ym.split(".")[0]
        # For sorting: convert "YYYY.MM" -> (YYYY, MM)
        parts = ym.split(".")
        y = int(parts[0]); m = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 12
        parsed.append((year, y, m, md))
    # sort by year desc, month desc
    parsed.sort(key=lambda t: (t[1], t[2]), reverse=True)
    # group
    out = []
    current_year = None
    for year, y, m, md in parsed:
        if year != current_year:
            out.append(f"\n## {year}\n")
            current_year = year
        out.append(md + "\n")
    return "\n".join(out).strip() + "\n"

def rebuild_page_body():
    with open(PAGE, "r", encoding="utf-8") as f:
        txt = f.read()
    # keep front matter, replace body
    if txt.strip().startswith("---"):
        m = re.match(r"^---.*?---\s*", txt, flags=re.DOTALL)
        fm = m.group(0) if m else FRONT_MATTER
        body = render_news_grouped_by_year()
        new_txt = fm + "\n" + body
    else:
        new_txt = FRONT_MATTER + "\n" + render_news_grouped_by_year()
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(new_txt)
    print("✅ Rebuilt Group NEWs page (English, grouped by year).")

def git_push():
    try:
        subprocess.run(["git", "add", "_data/navigation.yml", "_pages/group-news.md", "images/"], cwd=REPO, check=True)
        subprocess.run(["git", "commit", "-m", "Update Group NEWs: English version, grouped by year; add Flatlands image"], cwd=REPO, check=True)
        subprocess.run(["git", "push", "origin", "master"], cwd=REPO, check=True)
        print("🚀 Pushed to GitHub. Check /group-news/ after build.")
    except subprocess.CalledProcessError:
        print("⚠️ Git failed. Please check repo status manually.")

def main():
    if not os.path.isdir(REPO):
        print(f"❌ Repo not found: {REPO}")
        sys.exit(1)
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    update_navigation()
    ensure_page_and_front_matter()
    copy_flatlands_image()
    rebuild_page_body()
    git_push()

if __name__ == "__main__":
    main()

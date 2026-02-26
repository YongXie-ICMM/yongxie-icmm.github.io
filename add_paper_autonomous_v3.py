import os, shutil, subprocess, re

# =========================
# CONFIG
# =========================
REPO = r"D:\Git\yongxie-icmm.github.io"
PUBLICATIONS_DIR = os.path.join(REPO, "_publications")
FILES_DIR = os.path.join(REPO, "files")

# 如果你有本地 PDF，放到这个路径（文件名可改）
SOURCE_PDF = r"D:\Git\Source\2022-oea-ws2.pdf"
TARGET_PDF_NAME = "2022-oea-ws2.pdf"  # 放到站点 /files/ 的文件名

# =========================
# METADATA（已填好）
# =========================
TITLE    = "Solvent-free fabrication of broadband WS<sub>2</sub> photodetectors on paper"
DATE     = "2022-12-09"  # YYYY-MM-DD
VENUE    = "Opto-Electronic Advances, 6(3), 220101-1–220101-11"
EXCERPT  = ("A solvent-free approach to fabricate broadband WS₂ photodetectors on paper, "
            "enabling flexible, low-cost optoelectronics.")
CITATION = ('Wenliang Zhang, Onur Çakıroğlu, Abdullah Al-Enizi, Ayman Nafady, Xuetao Gan, '
            'Xiaohua Ma, Sruthi Kuriakose, Yong Xie, Andres Castellanos-Gomez. (2022). '
            '&quot;Solvent-free fabrication of broadband WS<sub>2</sub> photodetectors on paper.&quot; '
            '<i>Opto-Electronic Advances</i>, 6(3), 220101-1–220101-11.')
# 外部期刊链接（你提供的）
LINK     = "https://www.oejournal.org/oea/article/doi/10.29026/oea.2023.220101"

# =========================
# HELPERS
# =========================
def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s)
    return s[:80].strip("-")

def ensure_dirs():
    os.makedirs(PUBLICATIONS_DIR, exist_ok=True)
    os.makedirs(FILES_DIR, exist_ok=True)

def run_git(cmd):
    subprocess.run(cmd, cwd=REPO, check=True)

# =========================
# MAIN
# =========================
def main():
    ensure_dirs()

    # 生成站内 permalink slug：/publication/YYYY-MM-DD-ws2-photodetectors-on-paper
    slug = f"{DATE}-" + slugify("ws2-photodetectors-on-paper")
    md_name = f"{slug}.md"
    md_path = os.path.join(PUBLICATIONS_DIR, md_name)

    # 1) 删除同标题旧条目（防重复）
    duplicates = []
    for fn in os.listdir(PUBLICATIONS_DIR):
        if not fn.endswith(".md"): 
            continue
        p = os.path.join(PUBLICATIONS_DIR, fn)
        try:
            with open(p, "r", encoding="utf-8") as f:
                if f'title: "{TITLE}"' in f.read():
                    duplicates.append(p)
        except Exception:
            pass
    if duplicates:
        print("⚠️ Found existing publication(s) with same title, deleting...")
        for d in duplicates:
            os.remove(d)
            print("   🗑️", d)

    # 2) 复制 PDF（如存在）；决定 paperurl 指向站内PDF还是外链
    paperurl = ""
    if os.path.exists(SOURCE_PDF):
        target_pdf = os.path.join(FILES_DIR, TARGET_PDF_NAME)
        shutil.copy2(SOURCE_PDF, target_pdf)
        paperurl = f"/files/{TARGET_PDF_NAME}"
        print(f"✅ Copied PDF -> {target_pdf}")
    else:
        # 没有本地 PDF 时，先让“Download Paper”跳到期刊外链（也可留空）
        paperurl = LINK
        print(f"ℹ️ PDF not found at {SOURCE_PDF}. Will use external link as paperurl.")

    # 3) 写入 Markdown
    fm = f"""---
title: "{TITLE}"
collection: publications
category: manuscripts
permalink: /publication/{slug}
excerpt: '{EXCERPT}'
date: {DATE}
venue: '{VENUE}'
paperurl: '{paperurl}'
citation: '{CITATION}'
link: '{LINK}'
---
"""
    body = (
        "We demonstrate a solvent-free route to build broadband WS₂ photodetectors directly on paper substrates, "
        "offering a practical pathway toward flexible and low-cost optoelectronic devices."
    )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(fm + "\n" + body + "\n")

    print(f"✅ Markdown created: {md_path}")

    # 4) Git 提交&推送
    try:
        run_git(["git", "add", "_publications/", "files/"])
        clean_title = re.sub("<.*?>", "", TITLE)  # 去掉 <sub> 避免日志里含HTML
        run_git(["git", "commit", "-m", f"Add publication: {clean_title}"])
        run_git(["git", "push", "origin", "master"])
        print("🚀 Changes pushed to GitHub.")
    except subprocess.CalledProcessError:
        print("⚠️ Git failed. Please check repository status (e.g., remote, auth).")

if __name__ == "__main__":
    main()

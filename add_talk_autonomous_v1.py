import os, shutil, subprocess, sys, re

# =======================
# CONFIG – adjust if needed
# =======================
REPO = r"D:\Git\yongxie-icmm.github.io"
SRC = r"D:\Git\Source"  # where your local files live

# Talk metadata for Flatlands 2025 invited talk
TITLE     = "Towards Full Autonomous Synthesis and Characterization of 2D Materials"
DATE      = "2025-09-04"  # YYYY-MM-DD
VENUE     = "Flatlands Beyond Graphene 2025"
LOCATION  = "Milan, Italy"
TYPE      = "Invited Talk"
EXCERPT   = "Invited talk on using LLMs and AI to achieve fully autonomous synthesis and characterization of 2D materials."

# Real filenames you provided
SRC_SLIDES = os.path.join(SRC, "Flatlands2025_YXie_v2.pdf")
SRC_IMAGE  = os.path.join(SRC, "Flatlands_Invited_talk.png")

# Target names inside the repo
FILES_DIR  = os.path.join(REPO, "files")
IMAGES_DIR = os.path.join(REPO, "images")
TALKS_DIR  = os.path.join(REPO, "_talks")

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s)
    return s[:80].strip("-")

def ensure_dirs():
    os.makedirs(FILES_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(TALKS_DIR, exist_ok=True)

def copy_or_die(src, dst):
    if not os.path.exists(src):
        print(f"❌ Missing file: {src}")
        sys.exit(1)
    shutil.copy2(src, dst)
    print(f"✅ Copied -> {dst}")

def run_git(cmd):
    subprocess.run(cmd, cwd=REPO, check=True)

def main():
    ensure_dirs()

    slug = f"{DATE}-" + slugify(TITLE)
    md_name = f"{slug}.md"
    md_path = os.path.join(TALKS_DIR, md_name)

    # Detect duplicates
    duplicates = []
    for fn in os.listdir(TALKS_DIR):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(TALKS_DIR, fn)
        try:
            with open(p, "r", encoding="utf-8") as f:
                if f'title: "{TITLE}"' in f.read():
                    duplicates.append(p)
        except Exception:
            pass
    if duplicates:
        print("⚠️ Found existing talk(s) with the same title, deleting them first...")
        for d in duplicates:
            os.remove(d)
            print(f"🗑️ Deleted duplicate: {d}")

    # Copy assets
    tgt_pdf   = os.path.join(FILES_DIR, os.path.basename(SRC_SLIDES))
    tgt_image = os.path.join(IMAGES_DIR, os.path.basename(SRC_IMAGE))
    copy_or_die(SRC_SLIDES, tgt_pdf)
    copy_or_die(SRC_IMAGE,  tgt_image)

    slides_url = f"/files/{os.path.basename(tgt_pdf)}"
    teaser_url = f"/images/{os.path.basename(tgt_image)}"

    # Create markdown file
    md = f"""---
title: "{TITLE}"
collection: talks
type: "{TYPE}"
permalink: /talks/{slug}
venue: "{VENUE}"
date: {DATE}
location: "{LOCATION}"
excerpt: "{EXCERPT}"
slidesurl: "{slides_url}"
header:
  teaser: {teaser_url}
---

{EXCERPT}

[Download Slides]({slides_url})
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ Talk markdown created: {md_path}")

    # Git add/commit/push
    try:
        run_git(["git", "add", "_talks/", "files/", "images/"])
        run_git(["git", "commit", "-m", f"Add invited talk: {TITLE} ({VENUE}, {LOCATION})"])
        run_git(["git", "push", "origin", "master"])
        print("🚀 Pushed to GitHub. Your site will update shortly.")
    except subprocess.CalledProcessError:
        print("⚠️ Git push failed. Please check your repo manually.")

if __name__ == "__main__":
    main()

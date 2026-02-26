import os, shutil, subprocess, sys, re

# =======================
# CONFIG – adjust if needed
# =======================
REPO = r"D:\Git\yongxie-icmm.github.io"
SRC  = r"D:\Git\Source"  # where your local files live

# ---- Talk metadata for Graphene 2025 oral presentation ----
TITLE    = "Synthetic Data–Driven AI for 2D Materials and Optoelectronic Devices"
DATE     = "2025-06-26"  # YYYY-MM-DD
VENUE    = "Graphene 2025 Conference"
LOCATION = "Donostia–San Sebastián, Spain"
TYPE     = "Oral Presentation"
EXCERPT  = ("Oral presentation at Graphene 2025 on synthetic data–driven AI for 2D materials "
            "and optoelectronic devices.")

# ---- Optional assets in D:\Git\Source\ (provide if available) ----
SRC_SLIDES = os.path.join(SRC, "Graphene2025_Xie_slides.pdf")   # 如果有幻灯片，改成你的文件名；没有就留着不管
SRC_IMAGE  = os.path.join(SRC, "Graphene2025_talk.png")          # 如果有配图；没有就留着不管
# Certificate (already provided)
SRC_CERT   = os.path.join(SRC, "Certificate02.pdf")              # 你刚放在 D:\Git\Source\ 的证书

# ---- Target names inside the repo ----
FILES_DIR   = os.path.join(REPO, "files")
IMAGES_DIR  = os.path.join(REPO, "images")
TALKS_DIR   = os.path.join(REPO, "_talks")

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s)
    return s[:80].strip("-")

def ensure_dirs():
    os.makedirs(FILES_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(TALKS_DIR, exist_ok=True)

def try_copy(src_path, dst_dir):
    """Copy file if exists; return site-relative url or ''."""
    if not src_path or not os.path.exists(src_path):
        return ""
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, os.path.basename(src_path))
    shutil.copy2(src_path, dst)
    print(f"✅ Copied -> {dst}")
    # site-relative
    if dst_dir.endswith("files"):
        return f"/files/{os.path.basename(dst)}"
    if dst_dir.endswith("images"):
        return f"/images/{os.path.basename(dst)}"
    return ""

def run_git(cmd):
    subprocess.run(cmd, cwd=REPO, check=True)

def main():
    ensure_dirs()

    slug = f"{DATE}-" + slugify(TITLE)
    md_name = f"{slug}.md"
    md_path = os.path.join(TALKS_DIR, md_name)

    # Remove duplicates by title
    duplicates = []
    for fn in os.listdir(TALKS_DIR):
        if not fn.endswith(".md"): continue
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

    # Copy optional assets
    slides_url = try_copy(SRC_SLIDES, FILES_DIR)   # '' if missing
    teaser_url = try_copy(SRC_IMAGE,  IMAGES_DIR)  # '' if missing
    cert_url   = try_copy(SRC_CERT,   FILES_DIR)   # '' if missing (should exist)

    # Build markdown blocks conditionally
    links_block = []
    if slides_url: links_block.append(f"[Download Slides]({slides_url})")
    if cert_url:   links_block.append(f"[Download Certificate]({cert_url})")
    links_md = "\n\n" + " | ".join(links_block) if links_block else ""

    header_teaser_block = ""
    if teaser_url:
        header_teaser_block = f"\nheader:\n  teaser: {teaser_url}"

    md = f"""---
title: "{TITLE}"
collection: talks
type: "{TYPE}"
permalink: /talks/{slug}
venue: "{VENUE}"
date: {DATE}
location: "{LOCATION}"
excerpt: "{EXCERPT}"{header_teaser_block}
{"slidesurl: \"" + slides_url + "\"" if slides_url else ""}
---

{EXCERPT}{links_md}
"""

    # Clean up potential blank line created by empty slidesurl:
    md = re.sub(r'\n{2,}', '\n\n', md).strip() + "\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ Talk markdown created: {md_path}")

    # Git add/commit/push
    try:
        run_git(["git", "add", "_talks/", "files/", "images/"])
        run_git(["git", "commit", "-m", f"Add talk: {TITLE} ({TYPE}, {VENUE}, {LOCATION})"])
        run_git(["git", "push", "origin", "master"])
        print("🚀 Pushed to GitHub. Your site will update shortly.")
    except subprocess.CalledProcessError:
        print("⚠️ Git push failed. Please check your repo manually.")

if __name__ == "__main__":
    main()

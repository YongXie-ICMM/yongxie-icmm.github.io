import os, re, shutil, subprocess, sys
from datetime import datetime

# ====== PATHS (按需修改) ======
REPO = r"D:\Git\yongxie-icmm.github.io"
PAGES = os.path.join(REPO, "_pages")
DATA  = os.path.join(REPO, "_data")
NAV   = os.path.join(DATA, "navigation.yml")

old_page = os.path.join(PAGES, "portfolio.md")
new_page = os.path.join(PAGES, "group-news.md")

# ====== 要追加的英文新闻 ======
NEWS_BLOCK = """
• [2025.09] We sincerely thank the organizers of *Flatlands Beyond Graphene 2025* for their kind invitation. Prof. Yong Xie was invited to deliver a plenary talk and chaired the Tuesday evening Shotgun Session.  

• [2025.08] We were delighted to host Prof. Eduardo R. Hernández and Prof. Andres Castellanos-Gomez during this hot summer. They shared deep theoretical insights and practical guidance through lectures and lab discussions with our students.  

Special thanks to graduate students Qianjie Lei and Yang Liu for their dedicated support.  
Scientific inspiration often sprouts quietly during such conversations.
""".strip() + "\n"

# ====== 新页面的 Front Matter 模板 ======
FRONT_MATTER = """---
layout: archive
title: "Group NEWs"
permalink: /group-news/
author_profile: true
---
"""

def ensure_dirs():
    os.makedirs(PAGES, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)

def backup(path):
    if not os.path.exists(path): return None
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = f"{path}.bak.{ts}"
    shutil.copy2(path, bak)
    print(f"🗂  Backup -> {bak}")
    return bak

def update_navigation():
    """把导航里的 Portfolio 改成 Group NEWs；如无则追加"""
    if not os.path.exists(NAV):
        print(f"⚠️  {NAV} not found, creating a minimal navigation.yml")
        os.makedirs(DATA, exist_ok=True)
        with open(NAV, "w", encoding="utf-8") as f:
            f.write(f'- title: "Group NEWs"\n  url: /group-news/\n')
        return

    backup(NAV)
    with open(NAV, "r", encoding="utf-8") as f:
        content = f.read()

    changed = False

    # 先尝试把 title 为 Portfolio 的项改名并改 URL
    # 兼容两种写法的顺序
    pattern = r'(-\s*title:\s*["\']?Portfolio["\']?\s*\n\s*url:\s*/portfolio/)|(-\s*url:\s*/portfolio/\s*\n\s*title:\s*["\']?Portfolio["\']?)'
    if re.search(pattern, content, flags=re.IGNORECASE):
        content = re.sub(r'title:\s*["\']?Portfolio["\']?', 'title: "Group NEWs"', content, flags=re.IGNORECASE)
        content = re.sub(r'url:\s*/portfolio/?', 'url: /group-news/', content, flags=re.IGNORECASE)
        changed = True

    # 如果原来没有 Portfolio，这里检查是否已有 group-news，没有就追加一项
    if not changed and 'url: /group-news/' not in content:
        if not content.endswith("\n"):
            content += "\n"
        content += '- title: "Group NEWs"\n  url: /group-news/\n'
        changed = True

    if changed:
        with open(NAV, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ navigation.yml updated.")
    else:
        print("ℹ️  navigation.yml already points to Group NEWs. No change needed.")

def setup_group_news_page():
    """重命名/创建页面，并添加新闻"""
    if os.path.exists(old_page) and not os.path.exists(new_page):
        backup(old_page)
        os.rename(old_page, new_page)
        print(f"✅ Renamed: {old_page} -> {new_page}")

    if not os.path.exists(new_page):
        with open(new_page, "w", encoding="utf-8") as f:
            f.write(FRONT_MATTER + "\n")
        print(f"✅ Created page: {new_page}")

    # 确保 front matter 存在且正确
    with open(new_page, "r", encoding="utf-8") as f:
        body = f.read()

    if 'permalink: /group-news/' not in body:
        body = re.sub(r'^---.*?---\s*', FRONT_MATTER, body, flags=re.DOTALL) if body.strip().startswith('---') \
               else FRONT_MATTER + "\n" + body
        with open(new_page, "w", encoding="utf-8") as f:
            f.write(body)
        print("✅ Updated front matter for group-news.md")

    # 追加新闻（避免重复追加同一段）
    with open(new_page, "r", encoding="utf-8") as f:
        page_now = f.read()
    if "Flatlands Beyond Graphene 2025" not in page_now:
        with open(new_page, "a", encoding="utf-8") as f:
            f.write("\n" + NEWS_BLOCK)
        print("✅ Appended latest news to group-news.md")
    else:
        print("ℹ️  News appears to be already present. Skipped appending.")

def git_commit_push():
    try:
        subprocess.run(["git", "add", "_data/navigation.yml", "_pages/group-news.md"], cwd=REPO, check=True)
        subprocess.run(["git", "commit", "-m", "Rename Portfolio to Group NEWs and add latest group news"], cwd=REPO, check=True)
        subprocess.run(["git", "push", "origin", "master"], cwd=REPO, check=True)
        print("🚀 Changes pushed to GitHub.")
    except subprocess.CalledProcessError:
        print("⚠️  Git failed. Please check your repository status.")

def main():
    if not os.path.isdir(REPO):
        print(f"❌ Repo path not found: {REPO}")
        sys.exit(1)
    os.chdir(REPO)
    ensure_dirs()
    update_navigation()
    setup_group_news_page()
    git_commit_push()

if __name__ == "__main__":
    main()

import os, re, shutil, subprocess
from datetime import datetime

REPO = r"D:\Git\yongxie-icmm.github.io"
NAV_PATH = os.path.join(REPO, "_data", "navigation.yml")

REMOVE_TITLES = {"blog posts", "guide"}  # 不区分大小写
REMOVE_URLS = {"/year-archive/", "/markdown/"}  # 以 URL 也能识别

def backup(path: str) -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = f"{path}.bak.{ts}"
    shutil.copy2(path, bak)
    print(f"🗂  Backup created -> {bak}")
    return bak

def strip_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

def process_navigation(nav_text: str) -> str:
    """
    仅处理 main: 部分，删除 title 为 Blog Posts / Guide 的条目（不区分大小写），
    或者 url 是 /year-archive/ /markdown/ 的条目。
    """
    lines = nav_text.splitlines(True)  # 保留换行
    out = []
    i = 0
    in_main = False
    main_indent = None
    removed_blocks = 0

    while i < len(lines):
        line = lines[i]

        # 进入 main: 区块
        if not in_main and re.match(r"^\s*main\s*:\s*$", line):
            in_main = True
            # 记录 main: 的缩进（用于判断层级）
            main_indent = len(re.match(r"^(\s*)", line).group(1))
            out.append(line)
            i += 1
            continue

        if in_main:
            # 遇到下一个顶层键，认为 main: 结束（行缩进 <= main_indent）
            if re.match(rf"^\s{{0,{main_indent}}}[a-zA-Z0-9_]+\s*:\s*$", line):
                in_main = False
                out.append(line)
                i += 1
                continue

            # 检测到一个 menu item 的开始：形如 '  - title: "xxx"' 或 '  - url: ...'
            if re.match(r"^\s*-\s", line):
                # 收集该块直到下一个同级的 '-' 开头或 main 结束
                block_lines = [line]
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    # 下一个同级的 list item 开始（同缩进的 '-'）
                    if re.match(r"^\s*-\s", nxt) or re.match(rf"^\s{{0,{main_indent}}}[a-zA-Z0-9_]+\s*:\s*$", nxt):
                        break
                    block_lines.append(nxt)
                    i += 1

                block_text = "".join(block_lines)

                # 提取 title 和 url（若存在）
                m_title = re.search(r"title\s*:\s*(.+)", block_text)
                m_url   = re.search(r"url\s*:\s*(.+)", block_text)

                title_norm = ""
                url_norm = ""

                if m_title:
                    title_norm = strip_quotes(m_title.group(1)).strip().lower()
                if m_url:
                    url_norm = strip_quotes(m_url.group(1)).strip().lower()

                should_remove = False
                if title_norm in REMOVE_TITLES:
                    should_remove = True
                if url_norm in REMOVE_URLS:
                    should_remove = True

                if should_remove:
                    removed_blocks += 1
                    print(f"🗑️  Removing menu item: title='{title_norm or 'N/A'}', url='{url_norm or 'N/A'}'")
                else:
                    out.append(block_text)

                continue

            # 其它 main 内的行，原样保留
            out.append(line)
            i += 1
            continue

        # 不在 main: 内，原样保留
        out.append(line)
        i += 1

    if removed_blocks == 0:
        print("ℹ️  No 'Blog Posts' or 'Guide' items found in navigation.yml (nothing removed).")
    else:
        print(f"✅ Removed {removed_blocks} item(s) from main navigation.")

    return "".join(out)

def git_commit_push():
    subprocess.run(["git", "add", "_data/navigation.yml"], cwd=REPO, check=True)
    subprocess.run(["git", "commit", "-m", "Remove Blog Posts and Guide from navigation menu"], cwd=REPO, check=True)
    subprocess.run(["git", "push", "origin", "master"], cwd=REPO, check=True)
    print("🚀 Pushed to GitHub.")

def main():
    nav_file = NAV_PATH
    if not os.path.exists(nav_file):
        raise SystemExit(f"❌ navigation.yml not found: {nav_file}")

    backup(nav_file)

    with open(nav_file, "r", encoding="utf-8") as f:
        src = f.read()

    new_text = process_navigation(src)

    if new_text != src:
        with open(nav_file, "w", encoding="utf-8") as f:
            f.write(new_text)
        print("💾 navigation.yml updated.")
        git_commit_push()
    else:
        print("✳️  No changes written (file already clean).")

if __name__ == "__main__":
    main()

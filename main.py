#!/usr/bin/env python3
"""
Unified site manager for this Jekyll repository.

Quick examples:
  python main.py quick-add-learning --title "MISSING Semester 2026 (MIT CSAIL)" --url "https://missing.csail.mit.edu/2026/" --preview
  python main.py quick-add-paper --title "A Paper" --date 2026-02-26 --venue "Journal Name" --citation "Author. (2026)." --paper-file D:\\Git\\Source\\paper.pdf
  python main.py quick-add-talk --title "An Invited Talk" --date 2026-02-26 --venue "Conference" --location "Madrid, Spain"
  python main.py quick-add-news --date 2026.02 --text "Added a new resource."
  python main.py quick-add-all --manifest batch_manifest.json --preview
  python main.py audit-publications --fix-venue-year
  python main.py preview --host 127.0.0.1 --port 4000 --incremental
  python main.py publish --message "Update website content"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
NAV_FILE = REPO_ROOT / "_data" / "navigation.yml"
LEARNING_FILE = REPO_ROOT / "_pages" / "learning.md"
NEWS_FILE = REPO_ROOT / "_pages" / "group-news.md"
PUBLICATIONS_DIR = REPO_ROOT / "_publications"
TALKS_DIR = REPO_ROOT / "_talks"
FILES_DIR = REPO_ROOT / "files"
IMAGES_DIR = REPO_ROOT / "images"


@dataclass
class NavItem:
    title: str
    url: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def normalize_url(url: str) -> str:
    if re.match(r"^https?://", url):
        return url
    if not url.startswith("/"):
        url = "/" + url
    if not url.endswith("/"):
        url += "/"
    return url


def normalize_iso_date(raw: str) -> str:
    s = raw.strip()
    for pattern in (r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$", r"^(\d{4})(\d{2})(\d{2})$"):
        m = re.match(pattern, s)
        if m:
            year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return f"{year:04d}-{month:02d}-{day:02d}"
    raise ValueError(f"Unsupported date format: {raw}. Use YYYY-MM-DD.")


def _publication_year_from_date(date_iso: str) -> str:
    return date_iso[:4]


def venue_contains_publication_year(venue: str, date_iso: str) -> bool:
    year = _publication_year_from_date(date_iso)
    return year in venue


def normalize_publication_venue(venue: str, date_iso: str) -> tuple[str, bool]:
    year = _publication_year_from_date(date_iso)
    v = venue.strip()
    original = v
    patterns = [
        rf"[\s,;]*\(\s*{year}\s*\)\s*$",
        rf"[\s,;]*\[\s*{year}\s*\]\s*$",
        rf"[\s,;]+{year}\s*$",
    ]
    for pattern in patterns:
        v = re.sub(pattern, "", v).strip()
    v = re.sub(r"[\s,;]+$", "", v)
    return v or original, (v != original)


def check_publication_metadata(title: str, date_iso: str, venue: str, citation: str) -> list[str]:
    warnings: list[str] = []
    year = _publication_year_from_date(date_iso)
    if venue_contains_publication_year(venue, date_iso):
        warnings.append(
            f"Venue already contains publication year {year}; rendering is dedupe-aware, but keep venue format consistent."
        )
    if title and citation and title.lower() not in citation.lower():
        warnings.append("Citation does not contain the exact publication title.")
    return warnings


def yaml_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return ascii_text or "item"


def parse_nav_items(content: str) -> list[tuple[NavItem, int, int]]:
    lines = content.splitlines()
    items: list[tuple[NavItem, int, int]] = []
    i = 0
    while i < len(lines):
        m = re.match(r'^\s*-\s*title:\s*"?(.*?)"?\s*$', lines[i])
        if not m:
            i += 1
            continue
        title = m.group(1).strip()
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines):
            u = re.match(r"^\s*url:\s*(\S+)\s*$", lines[j])
            if u:
                items.append((NavItem(title=title, url=u.group(1).strip()), i, j))
        i = j + 1
    return items


def add_nav_item(title: str, url: str, after: str | None) -> None:
    content = read_text(NAV_FILE)
    items = parse_nav_items(content)

    for item, _, _ in items:
        if item.url == url or item.title.lower() == title.lower():
            print(f"Navigation item already exists: {item.title} -> {item.url}")
            return

    lines = content.splitlines()
    insert_at = len(lines)
    if after:
        for item, _, end_idx in items:
            if item.title.lower() == after.lower():
                insert_at = end_idx + 1
                break

    block = [
        "",
        f'  - title: "{title}"',
        f"    url: {url}",
    ]
    lines[insert_at:insert_at] = block
    write_text(NAV_FILE, "\n".join(lines).rstrip() + "\n")
    print(f"Added nav item: {title} -> {url}")


def ensure_learning_page() -> None:
    if LEARNING_FILE.exists():
        return
    initial = """---
layout: archive
title: "Learning"
permalink: /learning/
author_profile: true
---

## Recommended Resources
"""
    write_text(LEARNING_FILE, initial + "\n")


def add_learning_resource(title: str, url: str, note: str | None) -> None:
    ensure_learning_page()
    content = read_text(LEARNING_FILE)
    if url in content:
        print(f"Learning resource already exists: {url}")
        return

    if "## Recommended Resources" not in content:
        content = content.rstrip() + "\n\n## Recommended Resources\n"

    entry = f"- [{title}]({url})"
    if note:
        entry += f"\n  {note.strip()}"

    content = content.rstrip() + "\n\n" + entry + "\n"
    write_text(LEARNING_FILE, content)
    print(f"Added learning resource: {title}")


def _normalize_news_date_label(raw: str) -> tuple[int, str]:
    s = raw.strip()
    ymd = re.match(r"^(\d{4})[-/.](\d{1,2})(?:[-/.](\d{1,2}))?$", s)
    if ymd:
        year = int(ymd.group(1))
        month = int(ymd.group(2))
        return year, f"{year:04d}.{month:02d}"
    ym = re.match(r"^(\d{4})(\d{2})$", s)
    if ym:
        year = int(ym.group(1))
        month = int(ym.group(2))
        return year, f"{year:04d}.{month:02d}"
    y = re.match(r"^(\d{4})$", s)
    if y:
        year = int(y.group(1))
        return year, str(year)
    raise ValueError(f"Unsupported date format: {raw}")


def _front_matter_end_line(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        return 0
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return idx + 1
    return 0


def add_group_news(date_raw: str, text: str) -> None:
    if not NEWS_FILE.exists():
        raise FileNotFoundError(f"Missing file: {NEWS_FILE}")

    year, label = _normalize_news_date_label(date_raw)
    entry = f"- [{label}] {text.strip()}"
    content = read_text(NEWS_FILE)
    if entry in content:
        print("News entry already exists.")
        return

    lines = content.splitlines()
    heading_pattern = re.compile(r"^##\s+(\d{4})\s*$")
    year_heading = f"## {year}"
    heading_indexes = [i for i, line in enumerate(lines) if heading_pattern.match(line.strip())]

    target_idx = None
    for i in heading_indexes:
        if lines[i].strip() == year_heading:
            target_idx = i
            break

    if target_idx is not None:
        insert_at = target_idx + 1
        while insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        lines[insert_at:insert_at] = ["", entry, ""]
    else:
        fm_end = _front_matter_end_line(lines)
        insert_at = fm_end
        for i in heading_indexes:
            y = int(heading_pattern.match(lines[i].strip()).group(1))
            if y < year:
                insert_at = i
                break
            insert_at = i + 1
        lines[insert_at:insert_at] = ["", year_heading, "", entry, ""]

    write_text(NEWS_FILE, "\n".join(lines).rstrip() + "\n")
    print(f"Added group news entry under {year_heading}")


def find_entries_by_title(collection_dir: Path, title: str) -> list[Path]:
    result: list[Path] = []
    title_pattern = re.compile(r'^title:\s*["\']?(.*?)["\']?\s*$', re.MULTILINE)
    for md in collection_dir.glob("*.md"):
        text = read_text(md)
        m = title_pattern.search(text)
        if m and m.group(1).strip() == title.strip():
            result.append(md)
    return result


def copy_asset(src_path: str | None, target_dir: Path, target_name: str | None) -> str:
    if not src_path:
        return ""
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = target_name.strip() if target_name else src.name
    dst = target_dir / filename
    dst.write_bytes(src.read_bytes())
    if target_dir == FILES_DIR:
        return f"/files/{filename}"
    if target_dir == IMAGES_DIR:
        return f"/images/{filename}"
    return ""


def compose_news_text(
    base_text: str,
    cert_url: str = "",
    cert_label: str = "Certificate",
    image_url: str = "",
    image_alt: str = "News image",
) -> str:
    text = base_text.strip()
    parts = [text] if text else []
    if cert_url:
        label = cert_label.strip() if cert_label else "Certificate"
        parts.append(f"[{label}]({cert_url})")
    if image_url:
        alt = image_alt.strip() if image_alt else "News image"
        parts.append(f"![{alt}]({image_url})")
    return "<br>\n".join(parts)


def add_group_news_with_assets(
    date_raw: str,
    text: str,
    image_file: str | None = None,
    image_name: str | None = None,
    cert_file: str | None = None,
    cert_name: str | None = None,
    cert_label: str | None = None,
    image_alt: str | None = None,
) -> None:
    image_url = copy_asset(image_file, IMAGES_DIR, image_name)
    cert_url = copy_asset(cert_file, FILES_DIR, cert_name)
    final_text = compose_news_text(
        text,
        cert_url=cert_url,
        cert_label=cert_label or "Certificate",
        image_url=image_url,
        image_alt=image_alt or "News image",
    )
    add_group_news(date_raw, final_text)


def add_publication(
    title: str,
    date_raw: str,
    venue: str,
    citation: str,
    excerpt: str | None,
    body: str | None,
    category: str,
    link: str | None,
    paper_file: str | None,
    paper_name: str | None,
    paper_url: str | None,
    slug_hint: str | None,
    replace_existing: bool,
    normalize_venue_year: bool = True,
) -> tuple[Path, str]:
    PUBLICATIONS_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)

    date_iso = normalize_iso_date(date_raw)
    slug = f"{date_iso}-{slugify(slug_hint or title)}"
    md_path = PUBLICATIONS_DIR / f"{slug}.md"

    existing = find_entries_by_title(PUBLICATIONS_DIR, title)
    if existing and not replace_existing:
        raise FileExistsError(f"Publication with same title already exists: {existing[0].name}. Use --replace-existing.")
    for old in existing:
        old.unlink()
        print(f"Removed duplicate publication: {old.name}")

    copied_paper_url = copy_asset(paper_file, FILES_DIR, paper_name)
    final_paper_url = paper_url or copied_paper_url or (link or "")

    resolved_excerpt = (excerpt or "").strip()
    resolved_body = (body or "").strip()
    if not resolved_excerpt:
        resolved_excerpt = resolved_body or title
    if not resolved_body:
        resolved_body = resolved_excerpt

    venue_to_write = venue.strip()
    if normalize_venue_year:
        venue_to_write, changed = normalize_publication_venue(venue_to_write, date_iso)
        if changed:
            print(f"Normalized venue year suffix: '{venue}' -> '{venue_to_write}'")

    for warning in check_publication_metadata(title, date_iso, venue_to_write, citation):
        print(f"Warning: {warning}")

    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        "collection: publications",
        f"category: {category}",
        f"permalink: /publication/{slug}",
        f"excerpt: {yaml_quote(resolved_excerpt)}",
        f"date: {date_iso}",
        f"venue: {yaml_quote(venue_to_write)}",
    ]
    if final_paper_url:
        lines.append(f"paperurl: {yaml_quote(final_paper_url)}")
    lines.append(f"citation: {yaml_quote(citation)}")
    if link:
        lines.append(f"link: {yaml_quote(link)}")
    lines.append("---")
    content = "\n".join(lines) + "\n\n" + resolved_body + "\n"
    write_text(md_path, content)
    print(f"Created publication: {md_path}")
    return md_path, final_paper_url


def add_talk(
    title: str,
    date_raw: str,
    venue: str,
    location: str,
    talk_type: str,
    excerpt: str | None,
    body: str | None,
    slides_file: str | None,
    slides_name: str | None,
    image_file: str | None,
    image_name: str | None,
    cert_file: str | None,
    cert_name: str | None,
    slug_hint: str | None,
    replace_existing: bool,
) -> tuple[Path, str, str, str]:
    TALKS_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    date_iso = normalize_iso_date(date_raw)
    slug = f"{date_iso}-{slugify(slug_hint or title)}"
    md_path = TALKS_DIR / f"{slug}.md"

    existing = find_entries_by_title(TALKS_DIR, title)
    if existing and not replace_existing:
        raise FileExistsError(f"Talk with same title already exists: {existing[0].name}. Use --replace-existing.")
    for old in existing:
        old.unlink()
        print(f"Removed duplicate talk: {old.name}")

    slides_url = copy_asset(slides_file, FILES_DIR, slides_name)
    teaser_url = copy_asset(image_file, IMAGES_DIR, image_name)
    cert_url = copy_asset(cert_file, FILES_DIR, cert_name)

    resolved_excerpt = (excerpt or "").strip()
    resolved_body = (body or "").strip()
    if not resolved_excerpt:
        resolved_excerpt = title
    if not resolved_body:
        links = []
        if slides_url:
            links.append(f"[Download Slides]({slides_url})")
        if cert_url:
            links.append(f"[Download Certificate]({cert_url})")
        resolved_body = resolved_excerpt
        if links:
            resolved_body += "\n\n" + " | ".join(links)

    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        "collection: talks",
        f"type: {yaml_quote(talk_type)}",
        f"permalink: /talks/{slug}",
        f"venue: {yaml_quote(venue)}",
        f"date: {date_iso}",
        f"location: {yaml_quote(location)}",
        f"excerpt: {yaml_quote(resolved_excerpt)}",
    ]
    if teaser_url:
        lines.extend(["header:", f"  teaser: {teaser_url}"])
    if slides_url:
        lines.append(f"slidesurl: {yaml_quote(slides_url)}")
    lines.append("---")

    content = "\n".join(lines) + "\n\n" + resolved_body + "\n"
    write_text(md_path, content)
    print(f"Created talk: {md_path}")
    return md_path, slides_url, cert_url, teaser_url


def run_command(cmd: list[str]) -> int:
    if os.name == "nt" and cmd:
        win_wrappers = {
            "bundle": "bundle.bat",
            "jekyll": "jekyll.bat",
            "gem": "gem.bat",
        }
        first = cmd[0].lower()
        if first in win_wrappers:
            cmd = [win_wrappers[first], *cmd[1:]]
    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    return proc.returncode


def run_preview(host: str, port: int, drafts: bool, incremental: bool) -> int:
    cmd = ["bundle", "exec", "jekyll", "serve", "--livereload", "--host", host, "--port", str(port)]
    if drafts:
        cmd.append("--drafts")
    if incremental:
        cmd.append("--incremental")
    return run_command(cmd)


def run_publish(message: str, branch: str, no_push: bool) -> int:
    rc = run_command(["git", "add", "-A"])
    if rc != 0:
        return rc
    rc = run_command(["git", "commit", "-m", message])
    if rc != 0:
        return rc
    if no_push:
        print("Committed locally. Push skipped by --no-push.")
        return 0
    return run_command(["git", "push", "origin", branch])


def quick_add_learning(
    nav_title: str,
    nav_url: str,
    after: str | None,
    title: str,
    url: str,
    note: str | None,
    date_raw: str | None,
    news_text: str | None,
    preview: bool,
    host: str,
    port: int,
) -> int:
    add_nav_item(nav_title, normalize_url(nav_url), after)
    add_learning_resource(title, url, note)
    date_label = date_raw or datetime.now().strftime("%Y.%m")
    auto_news = f"Added a new learning resource: [{title}]({url})."
    add_group_news(date_label, news_text.strip() if news_text else auto_news)
    if preview:
        return run_preview(host=host, port=port, drafts=False, incremental=True)
    return 0


def quick_add_news(
    date_raw: str,
    text: str,
    image_file: str | None,
    image_name: str | None,
    cert_file: str | None,
    cert_name: str | None,
    cert_label: str | None,
    image_alt: str | None,
    preview: bool,
    host: str,
    port: int,
) -> int:
    add_group_news_with_assets(
        date_raw=date_raw,
        text=text,
        image_file=image_file,
        image_name=image_name,
        cert_file=cert_file,
        cert_name=cert_name,
        cert_label=cert_label,
        image_alt=image_alt,
    )
    if preview:
        return run_preview(host=host, port=port, drafts=False, incremental=True)
    return 0


def quick_add_paper(
    title: str,
    date_raw: str,
    venue: str,
    citation: str,
    excerpt: str | None,
    body: str | None,
    category: str,
    link: str | None,
    paper_file: str | None,
    paper_name: str | None,
    paper_url: str | None,
    slug_hint: str | None,
    replace_existing: bool,
    keep_venue_year: bool,
    no_news: bool,
    news_date: str | None,
    news_text: str | None,
    preview: bool,
    host: str,
    port: int,
) -> int:
    _, final_paper_url = add_publication(
        title=title,
        date_raw=date_raw,
        venue=venue,
        citation=citation,
        excerpt=excerpt,
        body=body,
        category=category,
        link=link,
        paper_file=paper_file,
        paper_name=paper_name,
        paper_url=paper_url,
        slug_hint=slug_hint,
        replace_existing=replace_existing,
        normalize_venue_year=not keep_venue_year,
    )
    if not no_news:
        d = news_date or date_raw
        url = final_paper_url or link or ""
        auto_news = f"New publication: [{title}]({url})." if url else f"New publication: {title}."
        add_group_news(d, news_text or auto_news)
    if preview:
        return run_preview(host=host, port=port, drafts=False, incremental=True)
    return 0


def quick_add_talk(
    title: str,
    date_raw: str,
    venue: str,
    location: str,
    talk_type: str,
    excerpt: str | None,
    body: str | None,
    slides_file: str | None,
    slides_name: str | None,
    image_file: str | None,
    image_name: str | None,
    cert_file: str | None,
    cert_name: str | None,
    slug_hint: str | None,
    replace_existing: bool,
    no_news: bool,
    news_date: str | None,
    news_text: str | None,
    preview: bool,
    host: str,
    port: int,
) -> int:
    _, slides_url, cert_url, teaser_url = add_talk(
        title=title,
        date_raw=date_raw,
        venue=venue,
        location=location,
        talk_type=talk_type,
        excerpt=excerpt,
        body=body,
        slides_file=slides_file,
        slides_name=slides_name,
        image_file=image_file,
        image_name=image_name,
        cert_file=cert_file,
        cert_name=cert_name,
        slug_hint=slug_hint,
        replace_existing=replace_existing,
    )
    if not no_news:
        d = news_date or date_raw
        if news_text:
            add_group_news(d, news_text)
        else:
            auto_news = f"New talk: {title}."
            links: list[str] = []
            if slides_url:
                links.append(f"[Slides]({slides_url})")
            if cert_url:
                links.append(f"[Certificate]({cert_url})")
            if links:
                auto_news += " " + " | ".join(links)
            add_group_news(d, compose_news_text(auto_news, image_url=teaser_url, image_alt=title))
    if preview:
        return run_preview(host=host, port=port, drafts=False, incremental=True)
    return 0


def _as_bool(value: object, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        s = value.strip().lower()
        if s in ("1", "true", "yes", "y", "on"):
            return True
        if s in ("0", "false", "no", "n", "off"):
            return False
    raise ValueError(f"Invalid boolean value: {value}")


def _require_str(item: dict, key: str, context: str) -> str:
    value = item.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Missing required field '{key}' in {context}")
    return str(value).strip()


def _optional_str(item: dict, key: str) -> str | None:
    value = item.get(key)
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _resolve_source_path(raw_path: str | None, base_dir: Path) -> str | None:
    if not raw_path:
        return None
    p = Path(raw_path)
    if p.is_absolute():
        return str(p)
    return str((base_dir / p).resolve())


def _load_manifest(manifest_path: str) -> tuple[dict, Path]:
    raw = Path(manifest_path)
    if not raw.is_absolute():
        raw = (REPO_ROOT / raw).resolve()
    if not raw.exists():
        raise FileNotFoundError(f"Manifest not found: {raw}")
    data = json.loads(read_text(raw))
    if not isinstance(data, dict):
        raise ValueError("Manifest root must be a JSON object")
    return data, raw.parent


def _section_list(data: dict, key: str) -> list[dict]:
    value = data.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"Manifest field '{key}' must be a list")
    result: list[dict] = []
    for idx, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"Manifest field '{key}[{idx}]' must be an object")
        result.append(item)
    return result


def quick_add_all(manifest_path: str, preview: bool, host: str, port: int) -> int:
    data, manifest_dir = _load_manifest(manifest_path)
    defaults_raw = data.get("defaults", {})
    if defaults_raw is None:
        defaults_raw = {}
    if not isinstance(defaults_raw, dict):
        raise ValueError("Manifest field 'defaults' must be an object")

    default_add_news = _as_bool(defaults_raw.get("add_news"), True)
    default_replace = _as_bool(defaults_raw.get("replace_existing"), False)

    nav = data.get("nav")
    if nav:
        if not isinstance(nav, dict):
            raise ValueError("Manifest field 'nav' must be an object")
        add_nav_item(
            title=_require_str(nav, "title", "nav"),
            url=normalize_url(_require_str(nav, "url", "nav")),
            after=_optional_str(nav, "after"),
        )

    counts = {"learning": 0, "papers": 0, "talks": 0, "news": 0}

    for idx, item in enumerate(_section_list(data, "learning")):
        context = f"learning[{idx}]"
        title = _require_str(item, "title", context)
        url = _require_str(item, "url", context)
        note = _optional_str(item, "note")

        if _as_bool(item.get("add_nav"), False):
            add_nav_item(
                title=_optional_str(item, "nav_title") or "Learning",
                url=normalize_url(_optional_str(item, "nav_url") or "/learning/"),
                after=_optional_str(item, "after") or "Teaching",
            )

        add_learning_resource(title, url, note)
        counts["learning"] += 1

        if _as_bool(item.get("add_news"), default_add_news):
            date_raw = _optional_str(item, "date") or datetime.now().strftime("%Y.%m")
            news_text = _optional_str(item, "news_text") or f"Added a new learning resource: [{title}]({url})."
            add_group_news(date_raw, news_text)
            counts["news"] += 1

    for idx, item in enumerate(_section_list(data, "papers")):
        context = f"papers[{idx}]"
        title = _require_str(item, "title", context)
        date_raw = _require_str(item, "date", context)
        venue = _require_str(item, "venue", context)
        citation = _require_str(item, "citation", context)
        excerpt = _optional_str(item, "excerpt")
        body = _optional_str(item, "body")
        category = _optional_str(item, "category") or "manuscripts"
        link = _optional_str(item, "link")
        paper_file = _resolve_source_path(_optional_str(item, "paper_file"), manifest_dir)
        paper_name = _optional_str(item, "paper_name")
        paper_url = _optional_str(item, "paper_url")
        slug_hint = _optional_str(item, "slug")
        keep_venue_year = _as_bool(item.get("keep_venue_year"), False)
        replace_existing = _as_bool(item.get("replace_existing"), default_replace)

        _, final_paper_url = add_publication(
            title=title,
            date_raw=date_raw,
            venue=venue,
            citation=citation,
            excerpt=excerpt,
            body=body,
            category=category,
            link=link,
            paper_file=paper_file,
            paper_name=paper_name,
            paper_url=paper_url,
            slug_hint=slug_hint,
            replace_existing=replace_existing,
            normalize_venue_year=not keep_venue_year,
        )
        counts["papers"] += 1

        if _as_bool(item.get("add_news"), default_add_news):
            news_date = _optional_str(item, "news_date") or date_raw
            default_news = f"New publication: {title}."
            target = final_paper_url or link
            if target:
                default_news = f"New publication: [{title}]({target})."
            add_group_news(news_date, _optional_str(item, "news_text") or default_news)
            counts["news"] += 1

    for idx, item in enumerate(_section_list(data, "talks")):
        context = f"talks[{idx}]"
        title = _require_str(item, "title", context)
        date_raw = _require_str(item, "date", context)
        venue = _require_str(item, "venue", context)
        location = _require_str(item, "location", context)
        talk_type = _optional_str(item, "type") or "Talk"
        excerpt = _optional_str(item, "excerpt")
        body = _optional_str(item, "body")
        slides_file = _resolve_source_path(_optional_str(item, "slides_file"), manifest_dir)
        slides_name = _optional_str(item, "slides_name")
        image_file = _resolve_source_path(_optional_str(item, "image_file"), manifest_dir)
        image_name = _optional_str(item, "image_name")
        cert_file = _resolve_source_path(_optional_str(item, "cert_file"), manifest_dir)
        cert_name = _optional_str(item, "cert_name")
        slug_hint = _optional_str(item, "slug")
        replace_existing = _as_bool(item.get("replace_existing"), default_replace)

        _, slides_url, cert_url, teaser_url = add_talk(
            title=title,
            date_raw=date_raw,
            venue=venue,
            location=location,
            talk_type=talk_type,
            excerpt=excerpt,
            body=body,
            slides_file=slides_file,
            slides_name=slides_name,
            image_file=image_file,
            image_name=image_name,
            cert_file=cert_file,
            cert_name=cert_name,
            slug_hint=slug_hint,
            replace_existing=replace_existing,
        )
        counts["talks"] += 1

        if _as_bool(item.get("add_news"), default_add_news):
            news_date = _optional_str(item, "news_date") or date_raw
            explicit_news = _optional_str(item, "news_text")
            if explicit_news:
                add_group_news(news_date, explicit_news)
            else:
                default_news = f"New talk: {title}."
                links: list[str] = []
                if slides_url:
                    links.append(f"[Slides]({slides_url})")
                if cert_url:
                    links.append(f"[Certificate]({cert_url})")
                if links:
                    default_news += " " + " | ".join(links)
                add_group_news(news_date, compose_news_text(default_news, image_url=teaser_url, image_alt=title))
            counts["news"] += 1

    for idx, item in enumerate(_section_list(data, "news")):
        context = f"news[{idx}]"
        date_raw = _require_str(item, "date", context)
        text = _require_str(item, "text", context)
        image_file = _resolve_source_path(_optional_str(item, "image_file"), manifest_dir)
        image_name = _optional_str(item, "image_name")
        cert_file = _resolve_source_path(_optional_str(item, "cert_file"), manifest_dir)
        cert_name = _optional_str(item, "cert_name")
        cert_label = _optional_str(item, "cert_label")
        image_alt = _optional_str(item, "image_alt")
        add_group_news_with_assets(
            date_raw=date_raw,
            text=text,
            image_file=image_file,
            image_name=image_name,
            cert_file=cert_file,
            cert_name=cert_name,
            cert_label=cert_label,
            image_alt=image_alt,
        )
        counts["news"] += 1

    print(
        "quick-add-all completed: "
        f"learning={counts['learning']}, papers={counts['papers']}, talks={counts['talks']}, news={counts['news']}"
    )
    if preview:
        return run_preview(host=host, port=port, drafts=False, incremental=True)
    return 0


def audit_publications(fix_venue_year: bool) -> int:
    if not PUBLICATIONS_DIR.exists():
        print(f"Publication directory does not exist: {PUBLICATIONS_DIR}")
        return 1

    files = sorted(PUBLICATIONS_DIR.glob("*.md"))
    checked = 0
    warnings_count = 0
    fixed_count = 0

    for path in files:
        text = read_text(path)
        title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, flags=re.MULTILINE)
        date_match = re.search(r"^date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$", text, flags=re.MULTILINE)
        venue_match = re.search(r'^venue:\s*(["\']?)(.*?)\1\s*$', text, flags=re.MULTILINE)
        citation_match = re.search(r'^citation:\s*(["\']?)(.*?)\1\s*$', text, flags=re.MULTILINE)
        if not date_match or not venue_match:
            continue

        checked += 1
        title = title_match.group(1).strip() if title_match else path.stem
        date_iso = date_match.group(1).strip()
        venue = venue_match.group(2).strip()
        citation = citation_match.group(2).strip() if citation_match else ""

        warnings = check_publication_metadata(title, date_iso, venue, citation)
        for w in warnings:
            warnings_count += 1
            print(f"Warning [{path.name}]: {w}")

        if fix_venue_year:
            normalized_venue, changed = normalize_publication_venue(venue, date_iso)
            if changed:
                fixed_count += 1
                quote = venue_match.group(1)
                if quote:
                    replacement = f"venue: {quote}{normalized_venue}{quote}"
                else:
                    replacement = f"venue: {normalized_venue}"
                updated = re.sub(
                    r'^venue:\s*(["\']?).*?\1\s*$',
                    replacement,
                    text,
                    count=1,
                    flags=re.MULTILINE,
                )
                write_text(path, updated)
                print(f"Fixed [{path.name}]: venue '{venue}' -> '{normalized_venue}'")

    print(
        f"audit-publications completed: checked={checked}, warnings={warnings_count}, "
        f"fixed={fixed_count}"
    )
    return 0


def run_legacy(task: str) -> int:
    mapping = {
        "add-paper": REPO_ROOT / "add_paper_autonomous_v3.py",
        "add-talk": REPO_ROOT / "add_talk_autonomous_v3.py",
        "setup-news": REPO_ROOT / "setup_group_news_v3.py",
    }
    script = mapping.get(task)
    if not script or not script.exists():
        print(f"Legacy script not found for task: {task}")
        return 1
    return run_command([sys.executable, str(script)])


def add_preview_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--preview", action="store_true", help="Start local preview after adding")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4000)


def add_common_paper_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--title", required=True)
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--venue", required=True)
    parser.add_argument("--citation", required=True)
    parser.add_argument("--excerpt", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--category", default="manuscripts")
    parser.add_argument("--link", default="")
    parser.add_argument("--paper-file", default="")
    parser.add_argument("--paper-name", default="")
    parser.add_argument("--paper-url", default="")
    parser.add_argument("--slug", default="")
    parser.add_argument("--replace-existing", action="store_true")
    parser.add_argument("--keep-venue-year", action="store_true", help="Do not normalize trailing year in venue")


def add_common_talk_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--title", required=True)
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--venue", required=True)
    parser.add_argument("--location", required=True)
    parser.add_argument("--type", default="Talk")
    parser.add_argument("--excerpt", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--slides-file", default="")
    parser.add_argument("--slides-name", default="")
    parser.add_argument("--image-file", default="")
    parser.add_argument("--image-name", default="")
    parser.add_argument("--cert-file", default="")
    parser.add_argument("--cert-name", default="")
    parser.add_argument("--slug", default="")
    parser.add_argument("--replace-existing", action="store_true")


def add_common_news_asset_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--image-file", default="", help="Optional image file to copy into images/ and embed in news")
    parser.add_argument("--image-name", default="", help="Optional target filename in images/")
    parser.add_argument("--image-alt", default="News image", help="Alt text for embedded news image")
    parser.add_argument("--cert-file", default="", help="Optional certificate/pdf file to copy into files/ and link in news")
    parser.add_argument("--cert-name", default="", help="Optional target filename in files/")
    parser.add_argument("--cert-label", default="Certificate", help="Link label for certificate")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified manager for yongxie-icmm.github.io")
    sub = parser.add_subparsers(dest="command", required=True)

    p_nav = sub.add_parser("add-nav", help="Add an item to top navigation")
    p_nav.add_argument("--title", required=True)
    p_nav.add_argument("--url", required=True)
    p_nav.add_argument("--after", default="Teaching", help='Insert after this nav title (default: "Teaching")')

    p_learning = sub.add_parser("add-learning", help="Add a Learning resource")
    p_learning.add_argument("--title", required=True)
    p_learning.add_argument("--url", required=True)
    p_learning.add_argument("--note", default="")

    p_news = sub.add_parser("add-news", help="Add an entry to Group News")
    p_news.add_argument("--date", required=True, help="YYYY.MM or YYYY-MM or YYYY-MM-DD")
    p_news.add_argument("--text", required=True)
    add_common_news_asset_args(p_news)

    p_paper = sub.add_parser("add-paper", help="Add publication markdown (+ optional pdf copy)")
    add_common_paper_args(p_paper)

    p_talk = sub.add_parser("add-talk", help="Add talk markdown (+ optional assets copy)")
    add_common_talk_args(p_talk)

    p_audit = sub.add_parser("audit-publications", help="Check publication metadata consistency")
    p_audit.add_argument("--fix-venue-year", action="store_true", help="Normalize trailing year in venue for all publications")

    p_legacy = sub.add_parser("legacy", help="Run existing legacy automation script")
    p_legacy.add_argument("--task", required=True, choices=["add-paper", "add-talk", "setup-news"])

    sub.add_parser("build", help="Run Jekyll build")

    p_preview = sub.add_parser("preview", help="Run local preview with Jekyll serve")
    p_preview.add_argument("--host", default="127.0.0.1")
    p_preview.add_argument("--port", type=int, default=4000)
    p_preview.add_argument("--drafts", action="store_true", help="Include draft posts")
    p_preview.add_argument("--incremental", action="store_true", help="Enable incremental builds")

    p_serve = sub.add_parser("serve", help="Alias of preview")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=4000)
    p_serve.add_argument("--drafts", action="store_true", help="Include draft posts")
    p_serve.add_argument("--incremental", action="store_true", help="Enable incremental builds")

    p_publish = sub.add_parser("publish", help="Git add/commit/push in one command")
    p_publish.add_argument("--message", required=True)
    p_publish.add_argument("--branch", default="master")
    p_publish.add_argument("--no-push", action="store_true")

    p_quick_learning = sub.add_parser("quick-add-learning", help="One command: nav + learning + group news")
    p_quick_learning.add_argument("--title", required=True)
    p_quick_learning.add_argument("--url", required=True)
    p_quick_learning.add_argument("--note", default="")
    p_quick_learning.add_argument("--date", default="", help="News date, e.g. 2026.02 (default: current month)")
    p_quick_learning.add_argument("--news-text", default="")
    p_quick_learning.add_argument("--nav-title", default="Learning")
    p_quick_learning.add_argument("--nav-url", default="/learning/")
    p_quick_learning.add_argument("--after", default="Teaching")
    add_preview_args(p_quick_learning)

    p_quick_news = sub.add_parser("quick-add-news", help="One command: add group news (+ optional preview)")
    p_quick_news.add_argument("--date", required=True, help="YYYY.MM or YYYY-MM or YYYY-MM-DD")
    p_quick_news.add_argument("--text", required=True)
    add_common_news_asset_args(p_quick_news)
    add_preview_args(p_quick_news)

    p_quick_paper = sub.add_parser("quick-add-paper", help="One command: add paper + optional group news + optional preview")
    add_common_paper_args(p_quick_paper)
    p_quick_paper.add_argument("--no-news", action="store_true")
    p_quick_paper.add_argument("--news-date", default="")
    p_quick_paper.add_argument("--news-text", default="")
    add_preview_args(p_quick_paper)

    p_quick_talk = sub.add_parser("quick-add-talk", help="One command: add talk + optional group news + optional preview")
    add_common_talk_args(p_quick_talk)
    p_quick_talk.add_argument("--no-news", action="store_true")
    p_quick_talk.add_argument("--news-date", default="")
    p_quick_talk.add_argument("--news-text", default="")
    add_preview_args(p_quick_talk)

    p_quick_all = sub.add_parser("quick-add-all", help="Batch add learning/papers/talks/news from a JSON manifest")
    p_quick_all.add_argument("--manifest", required=True, help="Path to JSON manifest file")
    add_preview_args(p_quick_all)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "add-nav":
            add_nav_item(args.title.strip(), normalize_url(args.url.strip()), args.after.strip() if args.after else None)
            return 0
        if args.command == "add-learning":
            add_learning_resource(args.title.strip(), args.url.strip(), args.note.strip() or None)
            return 0
        if args.command == "add-news":
            add_group_news_with_assets(
                date_raw=args.date.strip(),
                text=args.text.strip(),
                image_file=args.image_file.strip() or None,
                image_name=args.image_name.strip() or None,
                cert_file=args.cert_file.strip() or None,
                cert_name=args.cert_name.strip() or None,
                cert_label=args.cert_label.strip() or None,
                image_alt=args.image_alt.strip() or None,
            )
            return 0
        if args.command == "add-paper":
            add_publication(
                title=args.title.strip(),
                date_raw=args.date.strip(),
                venue=args.venue.strip(),
                citation=args.citation.strip(),
                excerpt=args.excerpt.strip() or None,
                body=args.body.strip() or None,
                category=args.category.strip(),
                link=args.link.strip() or None,
                paper_file=args.paper_file.strip() or None,
                paper_name=args.paper_name.strip() or None,
                paper_url=args.paper_url.strip() or None,
                slug_hint=args.slug.strip() or None,
                replace_existing=args.replace_existing,
                normalize_venue_year=not args.keep_venue_year,
            )
            return 0
        if args.command == "add-talk":
            add_talk(
                title=args.title.strip(),
                date_raw=args.date.strip(),
                venue=args.venue.strip(),
                location=args.location.strip(),
                talk_type=args.type.strip(),
                excerpt=args.excerpt.strip() or None,
                body=args.body.strip() or None,
                slides_file=args.slides_file.strip() or None,
                slides_name=args.slides_name.strip() or None,
                image_file=args.image_file.strip() or None,
                image_name=args.image_name.strip() or None,
                cert_file=args.cert_file.strip() or None,
                cert_name=args.cert_name.strip() or None,
                slug_hint=args.slug.strip() or None,
                replace_existing=args.replace_existing,
            )
            return 0
        if args.command == "audit-publications":
            return audit_publications(fix_venue_year=args.fix_venue_year)
        if args.command == "legacy":
            return run_legacy(args.task)
        if args.command == "build":
            return run_command(["bundle", "exec", "jekyll", "build"])
        if args.command in ("preview", "serve"):
            return run_preview(args.host, args.port, args.drafts, args.incremental)
        if args.command == "publish":
            return run_publish(args.message.strip(), args.branch.strip(), args.no_push)
        if args.command == "quick-add-learning":
            return quick_add_learning(
                nav_title=args.nav_title.strip(),
                nav_url=args.nav_url.strip(),
                after=args.after.strip() if args.after else None,
                title=args.title.strip(),
                url=args.url.strip(),
                note=args.note.strip() or None,
                date_raw=args.date.strip() or None,
                news_text=args.news_text.strip() or None,
                preview=args.preview,
                host=args.host,
                port=args.port,
            )
        if args.command == "quick-add-news":
            return quick_add_news(
                date_raw=args.date.strip(),
                text=args.text.strip(),
                image_file=args.image_file.strip() or None,
                image_name=args.image_name.strip() or None,
                cert_file=args.cert_file.strip() or None,
                cert_name=args.cert_name.strip() or None,
                cert_label=args.cert_label.strip() or None,
                image_alt=args.image_alt.strip() or None,
                preview=args.preview,
                host=args.host,
                port=args.port,
            )
        if args.command == "quick-add-paper":
            return quick_add_paper(
                title=args.title.strip(),
                date_raw=args.date.strip(),
                venue=args.venue.strip(),
                citation=args.citation.strip(),
                excerpt=args.excerpt.strip() or None,
                body=args.body.strip() or None,
                category=args.category.strip(),
                link=args.link.strip() or None,
                paper_file=args.paper_file.strip() or None,
                paper_name=args.paper_name.strip() or None,
                paper_url=args.paper_url.strip() or None,
                slug_hint=args.slug.strip() or None,
                replace_existing=args.replace_existing,
                keep_venue_year=args.keep_venue_year,
                no_news=args.no_news,
                news_date=args.news_date.strip() or None,
                news_text=args.news_text.strip() or None,
                preview=args.preview,
                host=args.host,
                port=args.port,
            )
        if args.command == "quick-add-talk":
            return quick_add_talk(
                title=args.title.strip(),
                date_raw=args.date.strip(),
                venue=args.venue.strip(),
                location=args.location.strip(),
                talk_type=args.type.strip(),
                excerpt=args.excerpt.strip() or None,
                body=args.body.strip() or None,
                slides_file=args.slides_file.strip() or None,
                slides_name=args.slides_name.strip() or None,
                image_file=args.image_file.strip() or None,
                image_name=args.image_name.strip() or None,
                cert_file=args.cert_file.strip() or None,
                cert_name=args.cert_name.strip() or None,
                slug_hint=args.slug.strip() or None,
                replace_existing=args.replace_existing,
                no_news=args.no_news,
                news_date=args.news_date.strip() or None,
                news_text=args.news_text.strip() or None,
                preview=args.preview,
                host=args.host,
                port=args.port,
            )
        if args.command == "quick-add-all":
            return quick_add_all(
                manifest_path=args.manifest.strip(),
                preview=args.preview,
                host=args.host,
                port=args.port,
            )

        parser.print_help()
        return 1
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

# Yong Xie Website Manager

Unified automation tooling for `yongxie-icmm.github.io` (Jekyll + Academic Pages).

This repository uses `main.py` as the single CLI entry point for:
- content creation (news, talks, publications, learning)
- asset copying (PDF/images/certificates)
- local preview/build
- git publish
- post-publish online verification (including optional Kimi-based semantic checks)

## Overview

### Core capabilities
- One-command workflows (`quick-add-*`) for common updates
- Deterministic file generation under `_pages`, `_talks`, `_publications`, `files/`, `images/`
- Batch import via JSON manifest
- Publish verification by crawling live pages (`verify-publish`)

### Main entrypoint
```bash
python main.py -h
```

## Quick Start

### 1. Add a Group News item (with optional certificate/image)
```bash
python main.py quick-add-news ^
  --date 2026.02 ^
  --text "Received invited talk certificate at Conference 2026." ^
  --cert-file "C:\Users\Administrator\Desktop\Certificate_Yongxie.pdf" ^
  --image-file "D:\Git\Source\talk-photo.png"
```

### 2. Add a publication (+ optional auto news)
```bash
python main.py quick-add-paper ^
  --title "Paper Title" ^
  --date 2026-02-26 ^
  --venue "Journal Name" ^
  --citation "Author A, Author B. (2026)." ^
  --paper-file "D:\Git\Source\paper.pdf" ^
  --link "https://doi.org/xxx"
```

### 3. Add a talk (+ slides/certificate/image + optional auto news)
```bash
python main.py quick-add-talk ^
  --title "Talk Title" ^
  --date 2026-02-26 ^
  --venue "Conference 2026" ^
  --location "Madrid, Spain" ^
  --type "Invited Talk" ^
  --slides-file "D:\Git\Source\slides.pdf" ^
  --cert-file "D:\Git\Source\certificate.pdf" ^
  --image-file "D:\Git\Source\talk.png"
```

### 4. Local preview
```bash
python main.py preview --host 127.0.0.1 --port 4000 --incremental
```

### 5. Publish
```bash
python main.py publish --message "Update website content"
```

### 6. Verify live publish result
```bash
python main.py verify-publish ^
  --contains "MateFin" ^
  --expect-image "/images/2026-agentbeats-phase1-winners.jpg" ^
  --max-wait-seconds 180
```

If `--contains` / `--expect-image` are omitted, the command auto-derives checks from the latest local Group News entry.

## Batch Workflow

Use the manifest file to import multiple entries in one run:
```bash
python main.py quick-add-all --manifest batch_manifest.example.json --preview
```

Manifest supports:
- `learning[]`
- `papers[]`
- `talks[]`
- `news[]`

For `news[]`, optional asset fields are supported:
- `image_file`, `image_name`, `image_alt`
- `cert_file`, `cert_name`, `cert_label`

## Publish Verification (Crawler + Kimi)

### Deterministic crawler check
```bash
python main.py verify-publish --max-wait-seconds 300 --interval-seconds 10
```

### Add Kimi semantic validation
```bash
python main.py verify-publish --use-kimi --kimi-key-file moonshot_api_key.txt
```

Notes:
- `verify-publish` checks response status, required text snippets, and expected image sources.
- With `--use-kimi`, it additionally asks `kimi_interface_minimal.py` to judge whether the page reflects the intended update.

## Command Reference

```bash
python main.py add-nav -h
python main.py add-learning -h
python main.py add-news -h
python main.py add-paper -h
python main.py add-talk -h
python main.py quick-add-learning -h
python main.py quick-add-news -h
python main.py quick-add-paper -h
python main.py quick-add-talk -h
python main.py quick-add-all -h
python main.py audit-publications -h
python main.py verify-publish -h
python main.py publish -h
```

## Repository Structure

- `main.py`: unified CLI
- `_pages/group-news.md`: Group News source
- `_publications/`: publication entries
- `_talks/`: talk entries
- `files/`: PDFs and downloadable assets
- `images/`: image assets
- `batch_manifest.example.json`: batch import template
- `kimi_interface_minimal.py`: optional Kimi API client

## Security and Operations

- API key files (for example `moonshot_api_key.txt`) are ignored by git.
- Do not hardcode API keys in source files.
- Prefer `verify-publish` after each push to confirm public deployment.

## Legacy Compatibility

Older scripts are still callable:
```bash
python main.py legacy --task add-paper
python main.py legacy --task add-talk
python main.py legacy --task setup-news
```

## Upstream Attribution

This site is based on [Academic Pages](https://academicpages.github.io/), itself built on the Minimal Mistakes Jekyll theme.  
License: [MIT](LICENSE).

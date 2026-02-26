import os
import shutil
import subprocess

# === CONFIG ===
# Your local repo folder
repo_folder = r"D:\Git\yongxie-icmm.github.io"
# Source PDF file
source_pdf = r"D:\Git\Source\2025-autonomous-lab.pdf"


# Target paths
files_folder = os.path.join(repo_folder, "files")
publications_folder = os.path.join(repo_folder, "_publications")
target_pdf = os.path.join(files_folder, "2025-autonomous-lab.pdf")
markdown_file = os.path.join(publications_folder, "2025-07-03-autonomous-lab.md")

# === STEP 1: COPY PDF ===
os.makedirs(files_folder, exist_ok=True)
shutil.copy(source_pdf, target_pdf)
print(f"✅ Copied PDF to {target_pdf}")

# === STEP 2: CREATE MARKDOWN FILE ===
markdown_content = """---
title: "Toward Full Autonomous Laboratory Instrumentation Control with Large Language Models"
collection: publications
category: manuscripts
permalink: /publication/2025-07-03-autonomous-lab
excerpt: 'This paper explores how large language models can autonomously control laboratory instrumentation, paving the way for fully automated research workflows.'
date: 2025-07-03
venue: 'Small Structures, 6, 2500173'
paperurl: '/files/2025-autonomous-lab.pdf'
link: 'https://doi.org/10.1002/sstr.202500173'
citation: 'Yong Xie, Kexin He, Andres Castellanos-Gomez. (2025). &quot;Toward Full Autonomous Laboratory Instrumentation Control with Large Language Models.&quot; <i>Small Structures</i>, 6, 2500173.'
---

This study introduces a novel framework for autonomous laboratory instrumentation control using large language models (LLMs). By integrating LLMs with experimental hardware, this work demonstrates the feasibility of fully automated research pipelines, reducing human intervention and accelerating scientific discovery.
"""
with open(markdown_file, "w", encoding="utf-8") as f:
    f.write(markdown_content)
print(f"✅ Created markdown file: {markdown_file}")

# === STEP 3: GIT ADD + COMMIT + PUSH ===
try:
    subprocess.run(["git", "add", "_publications/", "files/"], cwd=repo_folder, check=True)
    subprocess.run(["git", "commit", "-m", "Added new publication: Toward Full Autonomous Laboratory Instrumentation Control"], cwd=repo_folder, check=True)
    subprocess.run(["git", "push", "origin", "master"], cwd=repo_folder, check=True)
    print("🚀 Changes pushed to GitHub successfully!")
except subprocess.CalledProcessError as e:
    print("⚠️ Git command failed. Please check your Git setup and try manually.")

import os
import shutil

# === CONFIGURATION ===
repo_path = r"D:\Git\yongxie-icmm.github.io"
publications_path = os.path.join(repo_path, "_publications")
files_path = os.path.join(repo_path, "files")

os.makedirs(publications_path, exist_ok=True)
os.makedirs(files_path, exist_ok=True)

# === PAPER INFORMATION (PRE-FILLED) ===
title = "Toward Full Autonomous Laboratory Instrumentation Control with Large Language Models"
authors = "Yong Xie, Kexin He, Andres Castellanos-Gomez"
date_for_file = "2025-07-03"
venue = "Small Structures, 6, 2500173"
excerpt = ("This paper discusses using large language models to autonomously control "
           "laboratory instruments, bridging AI with experimental research automation.")

# === SOURCE PDF PATH ===
source_pdf = r"D:\Git\Source\2025-autonomous-lab.pdf"
target_pdf = os.path.join(files_path, "2025-autonomous-lab.pdf")

# === COPY PDF TO FILES FOLDER ===
if os.path.exists(source_pdf):
    shutil.copy2(source_pdf, target_pdf)
    print(f"✅ Copied PDF to: {target_pdf}")
else:
    print(f"⚠️ WARNING: Source PDF not found at {source_pdf}. Please check the filename!")

# === AUTO-GENERATED FIELDS ===
paperurl = f"/files/2025-autonomous-lab.pdf"
safe_title = "-".join(title.lower().split()[:5])
filename = f"{date_for_file}-{safe_title}.md"
file_path = os.path.join(publications_path, filename)
citation = f'{authors}. (2025). "{title}." <i>{venue}</i>.'

# === MARKDOWN CONTENT ===
content = f"""---
title: "{title}"
collection: publications
category: manuscripts
permalink: /publication/{date_for_file}-{safe_title}
excerpt: '{excerpt}'
date: {date_for_file}
venue: '{venue}'
paperurl: '{paperurl}'
citation: '{citation}'
link: '{paperurl}'
---

{excerpt}
"""

# === WRITE FILE ===
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ New publication file created: {file_path}")
print(f"🔗 This will link to your PDF at {paperurl}")
print("\n➡️  Next steps:")
print("   git add _publications/ files/")
print('   git commit -m "Added new publication: Toward Full Autonomous Laboratory Instrumentation Control"')
print("   git push origin master")

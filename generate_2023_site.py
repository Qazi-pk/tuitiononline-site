import os
import shutil
from datetime import datetime
from pathlib import Path

# === CONFIG ===
base_dir = Path(r"C:\Users\qmhan\OneDrive\Documents\GitHub\tuitiononline-site\2023")
repo_root = base_dir.parent
backup_dir = repo_root / "html_backup"

# === STEP 1: BACKUP EXISTING HTML FILES ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_target = backup_dir / f"2023_backup_{timestamp}"
backup_target.mkdir(parents=True, exist_ok=True)

for html_file in base_dir.rglob("*.html"):
    rel_path = html_file.relative_to(base_dir)
    dest_path = backup_target / rel_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(html_file, dest_path)

print(f"✅ Backup completed: {backup_target}")

# === STEP 2: TEMPLATES ===
subpage_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{
    font-family: 'Segoe UI', Roboto, Arial, sans-serif;
    background: #f7f9fc;
    margin: 0;
    padding: 2rem;
    color: #222;
  }}
  h1 {{
    text-align: center;
    color: #2c3e50;
  }}
  .gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 2rem;
  }}
  .gallery img {{
    width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  }}
  .back-link {{
    display: block;
    text-align: center;
    margin-top: 2rem;
    font-weight: bold;
    color: #2c3e50;
  }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="gallery">
{images}
</div>
<a class="back-link" href="../index.html">⬅ Back to 2023 Home</a>
</body>
</html>
"""

main_index_header = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2023</title>
<style>
  body {
    font-family: 'Segoe UI', Roboto, Arial, sans-serif;
    background: #f7f9fc;
    margin: 0;
    padding: 0;
    color: #222;
  }
  header {
    background: #2c3e50;
    color: #fff;
    padding: 2rem;
    text-align: center;
    font-size: 2rem;
  }
  main {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.5rem;
    padding: 2rem;
    max-width: 1100px;
    margin: auto;
  }
  .card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    padding: 1.5rem;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  }
  a {
    text-decoration: none;
    color: #2c3e50;
    font-weight: 600;
    display: block;
    margin-top: 0.5rem;
  }
  footer {
    text-align: center;
    padding: 1rem;
    background: #ecf0f1;
    font-size: 0.9rem;
    color: #555;
  }
  .year-links {
    text-align: center;
    margin-top: 2rem;
  }
  .year-links a {
    margin: 0 1rem;
    font-weight: bold;
    color: #2253cb;
  }
</style>
</head>
<body>
<header>2023 — Numerical Solutions</header>
<main>
"""

# === STEP 3: GENERATE PAGES ===
sections = []
for folder in sorted(base_dir.iterdir()):
    if folder.is_dir():
        title = f"2023 — {folder.name}"
        image_tags = []

        for img in folder.glob("*.*"):
            if img.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                image_tags.append(f'<img src="{img.name}" alt="{img.stem}">')

        if not image_tags:
            continue

        html_content = subpage_template.format(title=title, images="\n".join(image_tags))
        index_path = folder / "index.html"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        sections.append(f"""
        <div class="card">
          <h2>{folder.name}</h2>
          <a href="{folder.name}/">Open Section</a>
        </div>
        """)

# === STEP 4: WRITE MAIN INDEX.HTML WITH YEAR LINKS ===
year_links = []
for y in ["2024", "2025"]:
    year_path = repo_root / y
    if year_path.exists():
        year_links.append(f'<a href="../{y}/index.html">→ Go to {y}</a>')

main_index_content = (
    main_index_header
    + "\n".join(sections)
    + "</main><div class='year-links'>"
    + " | ".join(year_links)
    + "</div><footer>© 2025 Tuition Online — All Rights Reserved</footer></body></html>"
)

main_index_path = base_dir / "index.html"
with open(main_index_path, "w", encoding="utf-8") as f:
    f.write(main_index_content)

print("✅ All 2023 HTML pages generated successfully with navigation to 2024 and 2025!")

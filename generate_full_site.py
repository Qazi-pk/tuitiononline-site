import os
import shutil
import html
import json
import re
from datetime import datetime

ROOT = r"C:\Users\qmhan\OneDrive\Documents\GitHub\tuitiononline-site"
BACKUP_DIR = os.path.join(ROOT, "html_backup")
MAKE_BACKUPS = True

# --- Collapsible Search with Memory ---
SEARCH_SCRIPT = """
<style>
#searchIcon {
  position: fixed; top: 15px; right: 20px;
  z-index: 10001; background: #2c3e50; color: #fff;
  border-radius: 50%; width: 40px; height: 40px;
  display: flex; justify-content: center; align-items: center;
  font-size: 20px; cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}
#searchBox {
  position: fixed; top: 15px; right: 70px;
  z-index: 10000; padding: 8px 12px;
  font-size: 1rem; border-radius: 6px;
  border: 1px solid #ccc; outline: none;
  width: 0; opacity: 0; transition: width 0.3s ease, opacity 0.3s ease;
}
#searchBox.active {
  width: 200px; opacity: 1; box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
@media (max-width:600px) {
  #searchBox.active { width: 140px; }
}
</style>

<script>
document.addEventListener("DOMContentLoaded", function() {
  const icon = document.createElement("div");
  icon.id = "searchIcon";
  icon.innerHTML = "&#128269;";
  document.body.appendChild(icon);

  const input = document.createElement("input");
  input.type = "search";
  input.placeholder = "Search...";
  input.id = "searchBox";
  document.body.appendChild(input);

  // Restore last query if exists
  const lastQuery = sessionStorage.getItem("searchQuery") || "";
  if (lastQuery) {
    input.value = lastQuery;
    input.classList.add("active");
  }

  icon.addEventListener("click", () => {
    input.classList.toggle("active");
    if (input.classList.contains("active")) input.focus();
  });

  const cards = Array.from(document.querySelectorAll(".card"));

  function filterCards(term) {
    const query = term.toLowerCase();
    cards.forEach(c => {
      const text = c.innerText.toLowerCase();
      c.style.display = text.includes(query) ? "" : "none";
    });
  }

  // Apply filter if memory has something
  if (lastQuery) filterCards(lastQuery);

  input.addEventListener("input", function() {
    const term = input.value;
    sessionStorage.setItem("searchQuery", term);
    filterCards(term);
  });
});
</script>
"""

# --- Templates ---
SECTION_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    body{{font-family:"Segoe UI",Roboto,Arial,sans-serif;background:#f7f9fc;margin:0;color:#222;}}
    header{{background:#2c3e50;color:#fff;padding:1.2rem;text-align:center;font-size:1.6rem;}}
    nav.breadcrumbs{{font-size:.9rem;padding:.5rem 1rem;background:#ecf0f1;margin:0;text-align:left;}}
    nav.breadcrumbs a{{color:#2c3e50;text-decoration:none;}}
    nav.breadcrumbs span{{color:#777;}}
    main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;
          padding:1.5rem;max-width:1100px;margin:1rem auto;}}
    .card{{background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.08);
           overflow:hidden;transition:transform .2s,box-shadow .2s;}}
    .card:hover{{transform:translateY(-4px);box-shadow:0 4px 16px rgba(0,0,0,0.15);}}
    .thumb{{width:100%;height:180px;object-fit:cover;background:#eee;display:block;}}
    .content{{padding:1rem;}}
    .content h3{{margin:0 0 .5rem 0;font-size:1.1rem;color:#2c3e50;}}
    .content p{{font-size:.9rem;color:#555;line-height:1.3em;margin:0;min-height:3em;}}
    a.btn{{display:inline-block;margin-top:.8rem;padding:.5rem .9rem;background:#2c3e50;color:#fff;
           border-radius:6px;text-decoration:none;text-align:center;}}
    footer{{text-align:center;padding:1rem;background:#ecf0f1;color:#555;font-size:.9rem;}}
  </style>
</head>
<body>
  <header>{title}</header>
  <nav class="breadcrumbs">{breadcrumbs}</nav>
  <main>{cards}</main>
  <footer>© {year} Tuition Online — All Rights Reserved</footer>
  {search_js}
</body>
</html>
"""

HOME_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Tuition Online</title>
  <style>
    body{{font-family:"Segoe UI",Roboto,Arial,sans-serif;background:#f7f9fc;margin:0;color:#222;}}
    header{{background:#2c3e50;color:#fff;padding:1.8rem;text-align:center;font-size:2rem;}}
    main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.5rem;
          padding:2rem;max-width:1100px;margin:auto;}}
    .card{{background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.08);
           text-align:center;padding:1.2rem;transition:transform .2s,box-shadow .2s;}}
    .card:hover{{transform:translateY(-4px);box-shadow:0 4px 16px rgba(0,0,0,0.15);}}
    a{{text-decoration:none;color:#2c3e50;font-weight:600;display:block;margin-top:.5rem;}}
    footer{{text-align:center;padding:1rem;background:#ecf0f1;color:#555;font-size:.9rem;}}
  </style>
</head>
<body>
  <header>Tuition Online</header>
  <main>{cards}</main>
  <footer>© {year} Tuition Online — All Rights Reserved</footer>
  {search_js}
</body>
</html>
"""

# --- Utility Functions ---
def friendly_label(fname):
    name = os.path.splitext(fname)[0]
    name = name.replace("-", " ").replace("_", " ")
    return " ".join(name.split()).title()

def extract_excerpt(html_path, max_len=140):
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            text = f.read()
        match = re.search(r"<p>(.*?)</p>", text, re.I | re.S)
        snippet = re.sub(r"<.*?>", "", match.group(1)) if match else re.sub(r"<.*?>", "", text)
        snippet = snippet.strip()
        if len(snippet) > max_len:
            snippet = snippet[:max_len].rsplit(" ", 1)[0] + "..."
        return html.escape(snippet)
    except Exception:
        return ""

def extract_first_image(html_path, base_rel):
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            text = f.read()
        match = re.search(r'<img[^>]+src=["\'](.*?)["\']', text, re.I)
        if match:
            img_src = match.group(1)
            if not img_src.startswith("http"):
                img_src = os.path.normpath(os.path.join("/", base_rel, img_src)).replace("\\", "/")
            return html.escape(img_src)
    except Exception:
        pass
    return ""

def build_card(link, title, excerpt="", thumb=""):
    thumb_html = f'<img src="{thumb}" class="thumb" alt="{title}">' if thumb else '<div class="thumb"></div>'
    return f"""
    <div class="card">
      {thumb_html}
      <div class="content">
        <h3>{html.escape(title)}</h3>
        <p>{excerpt}</p>
        <a class="btn" href="{html.escape(link)}">Open</a>
      </div>
    </div>"""

def make_breadcrumbs(rel_path):
    parts = rel_path.split(os.sep)
    if rel_path in ("", "."):
        return '<a href="/index.html">Home</a>'
    crumbs = ['<a href="/index.html">Home</a>']
    cumulative = ""
    for p in parts:
        if not p or p == ".":
            continue
        cumulative = os.path.join(cumulative, p)
        crumbs.append(f'<a href="/{cumulative}/index.html">{html.escape(p)}</a>')
    return " › ".join(crumbs)

def ensure_backup(src_path, rel_path):
    backup_path = os.path.join(BACKUP_DIR, rel_path)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copy2(src_path, backup_path)

def load_metadata(folder):
    meta_path = os.path.join(folder, "metadata.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def create_section_index(dir_path, dir_rel):
    html_files = [f for f in os.listdir(dir_path)
                  if f.lower().endswith(".html") and f.lower() != "index.html"]
    if not html_files:
        return False

    metadata = load_metadata(dir_path)
    custom_titles = metadata.get("titles", {})

    cards = []
    for fname in sorted(html_files):
        label = custom_titles.get(fname, friendly_label(fname))
        full_path = os.path.join(dir_path, fname)
        link = f"/{os.path.join(dir_rel, fname)}".replace("\\", "/")
        excerpt = extract_excerpt(full_path)
        thumb = extract_first_image(full_path, dir_rel)
        cards.append(build_card(link, label, excerpt, thumb))

    cards_html = "\n".join(cards)
    title = metadata.get("title", os.path.basename(dir_rel) or "Tuition Online")
    breadcrumbs = make_breadcrumbs(dir_rel)

    html_page = SECTION_TEMPLATE.format(
        title=html.escape(title),
        breadcrumbs=breadcrumbs,
        cards=cards_html,
        year=datetime.now().year,
        search_js=SEARCH_SCRIPT
    )

    index_path = os.path.join(dir_path, "index.html")
    if os.path.exists(index_path) and MAKE_BACKUPS:
        rel_index = os.path.relpath(index_path, ROOT)
        ensure_backup(index_path, rel_index)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_page)
    return True

def create_homepage():
    folders = [d for d in os.listdir(ROOT)
               if os.path.isdir(os.path.join(ROOT, d)) and re.match(r"^\d{4}$", d)]
    cards = []
    for year in sorted(folders):
        link = f"/{year}/index.html"
        cards.append(f'<div class="card"><h2>{year}</h2><a href="{link}">Open Section</a></div>')
    cards_html = "\n".join(cards)
    page = HOME_TEMPLATE.format(cards=cards_html, year=datetime.now().year, search_js=SEARCH_SCRIPT)
    index_path = os.path.join(ROOT, "index.html")

    if os.path.exists(index_path) and MAKE_BACKUPS:
        ensure_backup(index_path, "index.html")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(page)

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    count = 0
    for subdir, _, files in os.walk(ROOT):
        if os.path.commonpath([os.path.abspath(subdir), os.path.abspath(BACKUP_DIR)]) == os.path.abspath(BACKUP_DIR):
            continue
        rel = os.path.relpath(subdir, ROOT)
        if rel == ".":
            rel = ""
        html_files = [fn for fn in files if fn.lower().endswith(".html")]
        non_index = [fn for fn in html_files if fn.lower() != "index.html"]
        if non_index:
            if create_section_index(subdir, rel):
                count += 1
    create_homepage()
    print(f"\n✅ Generated homepage and {count} section index pages with collapsible search, memory, and backups.")
    print(f"📦 Backups stored in: {BACKUP_DIR}")

if __name__ == "__main__":
    main()

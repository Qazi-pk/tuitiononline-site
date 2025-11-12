import os
import re
import shutil

# === 1️⃣ Root folder of your local GitHub repo ===
root = r"C:\Users\qmhan\OneDrive\Documents\GitHub\tuitiononline-site"

# === 2️⃣ Backup folder ===
backup_root = os.path.join(root, "html_backup")
os.makedirs(backup_root, exist_ok=True)

# === 3️⃣ Log file ===
log_path = os.path.join(root, "fix_log.txt")
log = []

print("🔍 Starting path fixes and backup...\n")

# === 4️⃣ Walk through every subfolder ===
for subdir, _, files in os.walk(root):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(subdir, file)

            # --- Make backup copy ---
            relative_path = os.path.relpath(file_path, root)
            backup_path = os.path.join(backup_root, relative_path)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(file_path, backup_path)

            # --- Read and replace old links ---
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            new_content, count = re.subn(
                r"/wp-content/uploads/(20\d{2})/",
                r"/\1/",
                content
            )

            # --- Save edited file ---
            if count > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                log.append(f"✅ Fixed {count} paths in: {relative_path}")
                print(f"✅ {relative_path} — {count} replacements")
            else:
                print(f"⏩ {relative_path} — no changes")

# === 5️⃣ Write summary log ===
with open(log_path, "w", encoding="utf-8") as f:
    f.write("\n".join(log))

print("\n🎯 Done! All .html files fixed and backups saved in:")
print(backup_root)
print(f"📄 Log file created: {log_path}")

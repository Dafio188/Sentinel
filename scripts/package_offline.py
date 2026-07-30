import os
import shutil
import sys
import zipfile
from pathlib import Path

def package_offline():
    print("=== AIGate Offline Package Creator ===")

    root_dir = Path(__file__).resolve().parent.parent
    dist_dir = root_dir / "dist"
    dist_dir.mkdir(exist_ok=True)

    zip_filename = dist_dir / "aigate_offline_v1.0.zip"
    if zip_filename.exists():
        zip_filename.unlink()

    print(f"Creazione archivio di distribuzione offline: {zip_filename}")

    include_dirs = ["backend", "docs", "knowledge", "scripts", "frontend"]
    include_files = ["start_aigate.bat", "start_aigate.sh", "pyproject.toml", "README.md"]

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in include_files:
            file_path = root_dir / f
            if file_path.exists():
                zipf.write(file_path, arcname=f)

        for d in include_dirs:
            dir_path = root_dir / d
            if dir_path.exists():
                for root, dirs, files in os.walk(dir_path):
                    dirs[:] = [sub for sub in dirs if sub not in (
                        "__pycache__", "node_modules", ".next", ".pytest_cache", ".git"
                    )]
                    for file in files:
                        if file.endswith((".pyc", ".db", ".sqlite")):
                            continue
                        full_path = Path(root) / file
                        rel_path = full_path.relative_to(root_dir)
                        zipf.write(full_path, arcname=str(rel_path))

    zip_size_mb = zip_filename.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Archivio distribuibile creato con successo! Dimensione: {zip_size_mb:.2f} MB")
    print(f"Percorso: {zip_filename}")

if __name__ == "__main__":
    package_offline()

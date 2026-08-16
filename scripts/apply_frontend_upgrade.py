from __future__ import annotations

import os
import shutil
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE_DIR = os.path.join(BASE_DIR, "UPGRADE_PRONTEND", "wonderful-galileo", "frontend")

def sync_directory(src: str, dst: str):
    if not os.path.exists(src):
        print(f"Source {src} does not exist!")
        return
    os.makedirs(dst, exist_ok=True)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        dest_dir = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(dest_dir, exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dest_file = os.path.join(dest_dir, f)
            shutil.copy2(src_file, dest_file)
            # print(f"  Copied: {rel}/{f}")

def main():
    print("Applying Frontend Upgrade from UPGRADE_PRONTEND...")
    
    # 1. Copy documentation and metadata files
    doc_files = [
        "DESIGN.md",
        "FRONTEND_INTEGRATION_CONTRACT.md",
        "JUSTOR_AI_MASTER_CONTEXT_AZ.md",
        "Justor_Citizen_Authority_Library_60_Production_Pack_v2.md",
        "index.html",
        "tsconfig.json",
        "vite.config.ts",
        "package.json"
    ]
    for doc in doc_files:
        src = os.path.join(SOURCE_DIR, doc)
        dst = os.path.join(BASE_DIR, doc)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  -> Copied root file: {doc}")

    # 2. Sync directories
    dirs_to_sync = [
        ("content", os.path.join(BASE_DIR, "content")),
        ("public", os.path.join(BASE_DIR, "public")),
        ("scripts", os.path.join(BASE_DIR, "scripts")),
        ("src", os.path.join(BASE_DIR, "src")),
    ]
    for s_name, d_path in dirs_to_sync:
        s_path = os.path.join(SOURCE_DIR, s_name)
        print(f"Syncing {s_name} -> {d_path}...")
        sync_directory(s_path, d_path)
        print(f"  -> Synced directory: {s_name}")

    print("\nFrontend upgrade applied successfully!")

if __name__ == "__main__":
    main()

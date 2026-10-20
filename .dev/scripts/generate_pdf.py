#!/usr/bin/env python3
"""
Générateur de PDF hors-ligne et statique pour Campus Nakôbio
Utilise Google Chrome / Chromium en mode headless avec les styles @media print.

Usage:
  python3 .dev/scripts/generate_pdf.py [--all] [--course ID] [--lang LANG] [--cursus {semences,maraichage}]
"""

import os
import sys
import json
import time
import argparse
import subprocess
import http.server
import socketserver
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DIST_DIR = BASE_DIR / "dist"
PDF_DIR = BASE_DIR / "public" / "pdf"

PORT = 4399
SERVER_URL = f"http://127.0.0.1:{PORT}"

class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def log_message(self, format, *args):
        pass  # Silencieux

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), QuietHTTPHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    return httpd

def get_chrome_bin():
    for cmd in ["google-chrome", "chromium-browser", "chromium"]:
        try:
            res = subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                return cmd
        except FileNotFoundError:
            continue
    return None

def find_all_courses():
    courses = []
    
    # 1. Semences (src/data)
    semences_dir = BASE_DIR / "src" / "data"
    for f in semences_dir.glob("*.json"):
        if f.name == "catalog.json":
            continue
        parts = f.stem.split(".")
        if len(parts) == 1:
            course_id = parts[0]
            courses.append({
                "cursus": "semences",
                "id": course_id,
                "lang": "fr",
                "url": f"{SERVER_URL}/semences/{course_id}/",
                "output": PDF_DIR / "semences" / f"{course_id}.pdf"
            })
        elif len(parts) == 2:
            course_id, lang = parts
            courses.append({
                "cursus": "semences",
                "id": course_id,
                "lang": lang,
                "url": f"{SERVER_URL}/semences/{course_id}/{lang}/",
                "output": PDF_DIR / "semences" / f"{course_id}.{lang}.pdf"
            })

    # 2. Maraîchage (src/data/maraichage)
    maraichage_dir = BASE_DIR / "src" / "data" / "maraichage"
    for f in maraichage_dir.glob("*.json"):
        if f.name == "catalog.json":
            continue
        parts = f.stem.split(".")
        if len(parts) == 1:
            course_id = parts[0]
            courses.append({
                "cursus": "maraichage",
                "id": course_id,
                "lang": "fr",
                "url": f"{SERVER_URL}/maraichage/{course_id}/",
                "output": PDF_DIR / "maraichage" / f"{course_id}.pdf"
            })
        elif len(parts) == 2:
            course_id, lang = parts
            courses.append({
                "cursus": "maraichage",
                "id": course_id,
                "lang": lang,
                "url": f"{SERVER_URL}/maraichage/{course_id}/{lang}/",
                "output": PDF_DIR / "maraichage" / f"{course_id}.{lang}.pdf"
            })

    return courses

def generate_pdf_for_course(chrome_bin, course):
    out_file = course["output"]
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={str(out_file)}",
        course["url"]
    ]
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0 and out_file.exists() and out_file.stat().st_size > 1000:
        return True, out_file.stat().st_size
    else:
        return False, res.stderr

def main():
    parser = argparse.ArgumentParser(description="Générateur de PDF multilingues Nakôbio")
    parser.add_argument("--all", action="store_true", help="Générer les PDF pour tout le catalogue")
    parser.add_argument("--course", type=str, help="ID spécifique du cours (ex: a1_cest_quoi_une_graine)")
    parser.add_argument("--lang", type=str, help="Langue spécifique (ex: bm-nko, fr, en)")
    parser.add_argument("--cursus", choices=["semences", "maraichage"], help="Filtrer par cursus")
    args = parser.parse_args()

    chrome_bin = get_chrome_bin()
    if not chrome_bin:
        print("❌ Erreur : Google Chrome ou Chromium est requis pour générer les PDF.")
        sys.exit(1)

    print(f"🔍 Moteur PDF détecté : {chrome_bin}")

    if not DIST_DIR.exists():
        print("⚙️  Le dossier 'dist' n'existe pas. Construction du site Astro...")
        build_res = subprocess.run(["npm", "run", "build"], cwd=str(BASE_DIR))
        if build_res.returncode != 0:
            print("❌ Échec de npm run build.")
            sys.exit(1)

    courses = find_all_courses()
    
    # Filtrages
    if args.cursus:
        courses = [c for c in courses if c["cursus"] == args.cursus]
    if args.course:
        courses = [c for c in courses if c["id"] == args.course]
    if args.lang:
        courses = [c for c in courses if c["lang"] == args.lang]

    if not courses:
        print("⚠️ Aucun cours trouvé correspondant aux critères.")
        sys.exit(0)

    print(f"🚀 Démarrage du serveur statique local sur le port {PORT}...")
    httpd = start_server()
    time.sleep(1)

    try:
        print(f"📄 Génération de {len(courses)} document(s) PDF...")
        success_count = 0
        for idx, course in enumerate(courses, 1):
            cursus = course["cursus"]
            cid = course["id"]
            lang = course["lang"]
            print(f"[{idx}/{len(courses)}] [{cursus}] {cid} ({lang})... ", end="", flush=True)
            ok, result = generate_pdf_for_course(chrome_bin, course)
            if ok:
                size_kb = result / 1024
                print(f"✅ OK ({size_kb:.1f} Ko)")
                success_count += 1
            else:
                print(f"❌ Erreur: {result}")

        print(f"\n🎉 Terminé ! {success_count}/{len(courses)} PDF générés dans {PDF_DIR}.")
    finally:
        httpd.shutdown()

if __name__ == "__main__":
    main()

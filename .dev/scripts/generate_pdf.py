#!/usr/bin/env python3
"""
Outil CLI de Génération PDF Premium Locale pour Campus Nakôbio
=============================================================
Conçu pour être exécuté en local avant commit git des fichiers PDF.
Fonctionnalités avancées :
  - Détection intelligente des modifications : vérifie le hash (MD5) des fichiers JSON
    et ne régénère QUE les cours modifiés ou dont le PDF est manquant.
  - Option --force / -f : force la régénération intégrale de tous les cours.
  - Sélection ciblée :
      * Par numéro ou code de cours : --courses b14,101,a1 ou --courses 14,302
      * Par identifiant ou nom : --course b14_carotte
      * Par cursus : --cursus {semences,maraichage}
      * Par langue : --lang {fr,bm-nko,bm-latn,en,de}
  - Rendu haute fidélité Chrome Headless avec police N'ko locale, RTL et mise en page A4 Premium.
  - Maintien d'un fichier cache local .dev/pdf_build_cache.json pour le suivi incrémental.

Usage :
  python3 .dev/scripts/generate_pdf.py                     # Mode incrémental intelligent (ne fait que les modifiés)
  python3 .dev/scripts/generate_pdf.py -f                  # Force la régénération complète
  python3 .dev/scripts/generate_pdf.py -c b14,101,m3.2     # Génère uniquement les cours listés
  python3 .dev/scripts/generate_pdf.py -l bm-nko           # Génère uniquement la langue N'ko
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
import hashlib
import unicodedata
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DIST_DIR = BASE_DIR / "dist"
PDF_DIR = BASE_DIR / "public" / "pdf"
CACHE_FILE = BASE_DIR / ".dev" / "pdf_build_cache.json"

PORT = 4399
SERVER_URL = f"http://127.0.0.1:{PORT}"

LANG_FILE_CODES = {
    "fr": "fr",
    "en": "en",
    "de": "de",
    "bm-latn": "bm",
    "bm-nko": "nko"
}

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip()
    return re.sub(r"[-\s]+", "-", text)

def build_pdf_filename(cursus: str, course_code: str, title: str, lang: str) -> str:
    lang_code = LANG_FILE_CODES.get(lang, lang)
    clean_code = re.sub(r"[^a-zA-Z0-9.-]", "", course_code)
    clean_title = slugify(title) or "cours"
    return f"{lang_code}_{clean_code}_{clean_title}.pdf"

def compute_source_hash(file_path: Path) -> str:
    try:
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()
    except Exception:
        return ""

def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_cache(cache: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"⚠️ Impossible d'enregistrer le cache : {e}")

class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def log_message(self, format, *args):
        pass

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), QuietHTTPHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    return httpd

def get_chrome_bin():
    for cmd in ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]:
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
    for f in sorted(semences_dir.glob("*.json")):
        if f.name == "catalog.json":
            continue
        try:
            content = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        parts = f.stem.split(".")
        course_id = parts[0]
        lang = parts[1] if len(parts) == 2 else "fr"
        code = content.get("course_code") or course_id.split("_")[0].upper()
        title = content.get("title", course_id)
        
        pdf_name = build_pdf_filename("semences", code, title, lang)
        legacy_name = f"{course_id}.pdf" if lang == "fr" else f"{course_id}.{lang}.pdf"
        
        url_path = f"/semences/{course_id}/" if lang == "fr" else f"/semences/{course_id}/{lang}/"
        courses.append({
            "cursus": "semences",
            "id": course_id,
            "lang": lang,
            "title": title,
            "code": code,
            "source_file": f,
            "url": f"{SERVER_URL}{url_path}",
            "output": PDF_DIR / "semences" / pdf_name,
            "legacy_output": PDF_DIR / "semences" / legacy_name
        })

    # 2. Maraîchage (src/data/maraichage)
    maraichage_dir = BASE_DIR / "src" / "data" / "maraichage"
    for f in sorted(maraichage_dir.glob("*.json")):
        if f.name == "catalog.json":
            continue
        try:
            content = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        parts = f.stem.split(".")
        course_id = parts[0]
        lang = parts[1] if len(parts) == 2 else "fr"
        code = content.get("course_code") or course_id.split("_")[0].upper()
        title = content.get("title", course_id)
        
        pdf_name = build_pdf_filename("maraichage", code, title, lang)
        legacy_name = f"{course_id}.pdf" if lang == "fr" else f"{course_id}.{lang}.pdf"
        
        url_path = f"/maraichage/{course_id}/" if lang == "fr" else f"/maraichage/{course_id}/{lang}/"
        courses.append({
            "cursus": "maraichage",
            "id": course_id,
            "lang": lang,
            "title": title,
            "code": code,
            "source_file": f,
            "url": f"{SERVER_URL}{url_path}",
            "output": PDF_DIR / "maraichage" / pdf_name,
            "legacy_output": PDF_DIR / "maraichage" / legacy_name
        })

    return courses

def matches_query(query: str, course: dict) -> bool:
    q = query.lower().strip()
    if not q:
        return False
    cid = course["id"].lower()
    code = course.get("code", "").lower()
    
    # Égalité directe (b14_carotte, s2.14, m1.1)
    if q == cid or q == code:
        return True
    if cid.startswith(q) or code.startswith(q):
        return True
    if q in cid:
        return True
    
    # Extraction purement numérique (ex: '14' matche 'b14' ou 's2.14')
    q_digits = re.sub(r"[^\d]", "", q)
    if q_digits:
        cid_prefix = cid.split("_")[0]
        cid_digits = re.sub(r"[^\d]", "", cid_prefix)
        if q_digits == cid_digits:
            return True
        code_digits = re.sub(r"[^\d]", "", code)
        if q_digits == code_digits or code_digits.endswith(q_digits):
            return True
            
    return False

def generate_pdf_for_course(chrome_bin, course):
    out_file = course["output"]
    legacy_file = course["legacy_output"]
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Nettoyage automatique des anciens fichiers si le titre du cours a été modifié :
    # On identifie les fichiers existants qui partagent le même Code de cours et la même Langue (ex: fr_S2.14_*.pdf)
    lang_code = LANG_FILE_CODES.get(course["lang"], course["lang"])
    clean_code = re.sub(r"[^a-zA-Z0-9.-]", "", course["code"])
    old_pattern = f"{lang_code}_{clean_code}_*.pdf"
    
    for old_pdf in out_file.parent.glob(old_pattern):
        if old_pdf.name != out_file.name and old_pdf.is_file():
            try:
                old_pdf.unlink()
                print(f"\n   ♻️ Ancien fichier remplacé : {old_pdf.name}")
            except Exception:
                pass

    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--no-pdf-header-footer",
        f"--print-to-pdf={str(out_file)}",
        course["url"]
    ]
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0 and out_file.exists() and out_file.stat().st_size > 1000:
        try:
            if legacy_file.exists() or legacy_file.is_symlink():
                legacy_file.unlink()
            legacy_file.symlink_to(out_file.name)
        except Exception:
            pass
        return True, out_file.stat().st_size
    else:
        return False, res.stderr

def main():
    parser = argparse.ArgumentParser(
        description="Générateur de PDF Premium Nakôbio (Local & Incrémental)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  %(prog)s                         # Génère uniquement les fichiers modifiés ou manquants
  %(prog)s -f                      # Force la régénération de TOUS les cours
  %(prog)s -c b14,101,302          # Génère les cours 14, 101 et 302
  %(prog)s -l bm-nko               # Génère uniquement les variantes N'ko
  %(prog)s --cursus maraichage     # Génère uniquement le maraîchage
        """
    )
    parser.add_argument("-f", "--force", action="store_true", help="Forcer la régénération de tous les PDF (ignore le cache)")
    parser.add_argument("-c", "--courses", type=str, help="Numéro(s) ou ID(s) de cours séparés par virgule (ex: b14,101,a1 ou 14,302)")
    parser.add_argument("--course", type=str, help="ID unique du cours (ex: b14_carotte)")
    parser.add_argument("-l", "--lang", type=str, help="Filtrer par langue (ex: fr, bm-nko, bm-latn, en, de)")
    parser.add_argument("--cursus", choices=["semences", "maraichage"], help="Filtrer par cursus")
    args = parser.parse_args()

    chrome_bin = get_chrome_bin()
    if not chrome_bin:
        print("❌ Erreur : Google Chrome ou Chromium est requis sur votre machine locale pour générer les PDF.")
        sys.exit(1)

    print(f"🌿 Campus Nakôbio — Générateur PDF Premium")
    print(f"🔍 Moteur détecté : {chrome_bin}")

    all_courses = find_all_courses()
    selected_courses = all_courses

    # 1. Filtre par cursus
    if args.cursus:
        selected_courses = [c for c in selected_courses if c["cursus"] == args.cursus]

    # 2. Filtre par langue
    if args.lang:
        selected_courses = [c for c in selected_courses if c["lang"] == args.lang]

    # 3. Filtre par cours (multiples ou unique)
    queries = []
    if args.courses:
        queries.extend([q.strip() for q in args.courses.split(",") if q.strip()])
    if args.course:
        queries.append(args.course.strip())

    if queries:
        filtered = []
        for c in selected_courses:
            if any(matches_query(q, c) for q in queries):
                filtered.append(c)
        selected_courses = filtered

    if not selected_courses:
        print("⚠️ Aucun cours trouvé correspondant aux critères.")
        sys.exit(0)

    # 4. Détection intelligente des modifications (incrémental)
    cache = load_cache()
    courses_to_build = []

    for c in selected_courses:
        out_file = c["output"]
        src_file = c["source_file"]
        current_hash = compute_source_hash(src_file)
        rel_src = str(src_file.relative_to(BASE_DIR))

        needs_build = False
        if args.force:
            needs_build = True
        elif not out_file.exists() or out_file.stat().st_size < 1000:
            needs_build = True
        elif cache.get(rel_src) != current_hash:
            needs_build = True

        if needs_build:
            courses_to_build.append((c, rel_src, current_hash))

    if not courses_to_build:
        print("✨ Tous les fichiers PDF sont déjà à jour ! Aucun cours n'a été modifié.")
        print("💡 Utilisez l'option -f ou --force pour forcer la régénération complète.")
        sys.exit(0)

    print(f"📋 {len(courses_to_build)} document(s) à générer sur un catalogue sélectionné de {len(selected_courses)}.")

    # Vérification et build Astro si nécessaire
    if not DIST_DIR.exists():
        print("⚙️  Le dossier 'dist' n'existe pas. Construction du site Astro...")
        build_res = subprocess.run(["npm", "run", "build"], cwd=str(BASE_DIR))
        if build_res.returncode != 0:
            print("❌ Échec de npm run build.")
            sys.exit(1)

    print(f"🚀 Démarrage du serveur local éphémère (port {PORT})...")
    httpd = start_server()
    time.sleep(1)

    try:
        success_count = 0
        for idx, (course, rel_src, current_hash) in enumerate(courses_to_build, 1):
            cursus = course["cursus"]
            cid = course["id"]
            lang = course["lang"]
            target_name = course["output"].name
            print(f"[{idx}/{len(courses_to_build)}] [{cursus}] {cid} ({lang}) -> {target_name}... ", end="", flush=True)
            ok, result = generate_pdf_for_course(chrome_bin, course)
            if ok:
                size_kb = result / 1024
                print(f"✅ OK ({size_kb:.1f} Ko)")
                cache[rel_src] = current_hash
                success_count += 1
            else:
                print(f"❌ Erreur: {result}")

        save_cache(cache)
        print(f"\n🎉 Terminé ! {success_count}/{len(courses_to_build)} PDF générés dans {PDF_DIR}.")
        print("💡 Vous pouvez maintenant vérifier les PDF et exécuter un `git commit`.")
    finally:
        httpd.shutdown()

if __name__ == "__main__":
    main()

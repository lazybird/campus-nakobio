#!/usr/bin/env python3
"""
Pipeline de traduction universel pour Campus Nakôbio via OpenRouter API.
Gère : English (en), Deutsch (de), Bamanankan Latin (bm-latn), Bamanankan N'ko (bm-nko).
Résistant aux pannes, reprise automatique, sauvegarde incrémentale.
"""

import os
import sys
import json
import re
import time
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# Modèles calibrés par langue
MODELS = {
    "bm-nko": "anthropic/claude-sonnet-4.5",       # Qualité N'ko Unicode supérieure U+07C0-U+07FF
    "bm-latn": "google/gemini-2.5-flash",          # Bamanankan latin d'Afrique de l'Ouest
    "en": "google/gemini-2.5-flash",               # Rapide et précis agronomie
    "de": "google/gemini-2.5-flash"                # Rapide et précis agronomie
}

SYSTEM_PROMPTS = {
    "bm-nko": "You are a professional agricultural translator expert in Nko script (ߒߞߏ). Always output strictly valid JSON with the requested keys.",
    "bm-latn": "Tu es un agronome et traducteur professionnel expert en Bamanankan (Bambara ecriture latine standard malienne). Tu traduis des formations agroecologiques sahéliennes. Format de sortie : STRICTEMENT un objet JSON valide avec les clés demandées.",
    "en": "You are a professional agricultural translator specializing in open-pollinated seed production, soil health and agroecology. Format: STRICTLY valid JSON with the requested keys.",
    "de": "You are a professional agricultural translator specializing in German agroecology and organic farming. Format: STRICTLY valid JSON with the requested keys."
}

def call_openrouter(model, sys_prompt, user_prompt, max_retries=4):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }
    for attempt in range(max_retries):
        try:
            r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=50)
            if r.status_code == 200:
                data = r.json()
                content = data["choices"][0]["message"]["content"]
                m = re.search(r"\{[\s\S]*\}", content)
                if m:
                    return json.loads(m.group(0), strict=False)
                return None
            else:
                print(f"API Warning (attempt {attempt+1}/{max_retries}): status {r.status_code} - {r.text[:120]}", flush=True)
                time.sleep(2 ** attempt)
        except Exception as e:
            print(f"Network error (attempt {attempt+1}/{max_retries}): {e}", flush=True)
            time.sleep(2 ** attempt)
    return None

def translate_course(source_file, target_lang):
    if not os.path.exists(source_file):
        print(f"Fichier introuvable: {source_file}")
        return False

    target_file = source_file.replace(".json", f".{target_lang}.json")
    with open(source_file, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    # Reprise sur fichier existant ou initialisation
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            try:
                target_data = json.load(f)
            except Exception:
                target_data = json.loads(json.dumps(source_data))
    else:
        target_data = json.loads(json.dumps(source_data))

    model = MODELS.get(target_lang, "google/gemini-2.5-flash")
    sys_prompt = SYSTEM_PROMPTS.get(target_lang, "You are a translator. Output valid JSON.")

    print(f"\n🚀 Traduction de {os.path.basename(source_file)} vers [{target_lang}] (modèle: {model})...", flush=True)

    # 1. Traduire les métadonnées globales si pas encore faites
    needs_meta = False
    if target_lang == "bm-nko":
        needs_meta = not any('\u07c0' <= c <= '\u07ff' for c in target_data.get("title", ""))
    elif target_data.get("title") == source_data.get("title"):
        needs_meta = True

    if needs_meta:
        meta_prompt = f"""Traduis les métadonnées du cours vers la langue cible [{target_lang}].
Titre: {source_data.get('title', '')}
Résumé: {source_data.get('summary', '')}
Catégorie: {source_data.get('category', '')}

Réponds STRICTEMENT sous format JSON avec les clés :
{{
  "title": "...",
  "summary": "...",
  "category": "..."
}}"""
        meta_res = call_openrouter(model, sys_prompt, meta_prompt)
        if meta_res:
            target_data["title"] = meta_res.get("title", target_data["title"])
            target_data["summary"] = meta_res.get("summary", target_data["summary"])
            target_data["category"] = meta_res.get("category", target_data["category"])
            print("  ✓ Métadonnées globales traduites", flush=True)

    # 2. Traduire chaque page
    pages = target_data.get("pages", [])
    src_pages = source_data.get("pages", [])
    total_pages = len(pages)

    for idx, page in enumerate(pages):
        page_num = page.get("page_number", idx + 1)
        cur_title = page.get("title", "")
        cur_text = page.get("text", "")

        src_p = src_pages[idx] if idx < len(src_pages) else page
        src_title = src_p.get("title", "")
        src_text = src_p.get("text", "")

        # Test si déjà traduit
        already_translated = False
        if target_lang == "bm-nko":
            if any('\u07c0' <= c <= '\u07ff' for c in cur_title):
                already_translated = True
        else:
            if cur_title != src_title and cur_text != src_text:
                already_translated = True

        if already_translated:
            print(f"  Page {page_num}/{total_pages} : déjà traduite.", flush=True)
            continue

        prompt = f"""Traduis le titre et le texte de cette partie du cours vers [{target_lang}].
Conserve scrupuleusement la structure Markdown (gras **terme**, listes à puces -, sauts de ligne).
Titre source: {src_title}
Texte source:
{src_text}

Réponds STRICTEMENT sous format JSON avec les clés title et text :
{{
  "title": "...",
  "text": "..."
}}"""

        res = call_openrouter(model, sys_prompt, prompt)
        if res:
            page["title"] = res.get("title", cur_title)
            page["text"] = res.get("text", cur_text)
            print(f"  ✓ Page {page_num}/{total_pages} traduite", flush=True)
        else:
            print(f"  ⚠️ Échec traduction page {page_num}/{total_pages}", flush=True)

        # Sauvegarde incrémentale à chaque étape
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(target_data, f, indent=2, ensure_ascii=False)
        time.sleep(0.4)

    print(f"✅ Fichier finalisé avec succès : {target_file}", flush=True)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: translate.py <source_file.json> <lang1> [lang2 ...]")
        sys.exit(1)
    src = sys.argv[1]
    langs = sys.argv[2:]
    for l in langs:
        translate_course(src, l)

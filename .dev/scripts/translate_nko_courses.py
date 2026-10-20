#!/usr/bin/env python3
"""
Traduction ciblée en Bamanankan N'ko (ߒߞߏ) pour 101 et 201 avec Claude Sonnet 4.5
en respectant scrupuleusement la terminologie agroécologique établie dans les diapositives
manuelles (.dev/maraichage/nko/).
"""

import os
import sys
import json
import re
import time
import requests

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-sonnet-4.5"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

SYS_PROMPT = """Tu es le traducteur expert officiel en langue Mandingue / Bamanankan et écriture N'ko (ߒߞߏ - Unicode U+07C0 à U+07FF) pour le Campus de formation agroécologique Nakôbio.
Tu traduis avec précision les modules pédagogiques de maraîchage en sol vivant.

Règles impératives :
1. Vocabulaire obligatoire (conforme aux traductions manuelles de référence) :
   - Maraîchage bio-intensif en sol vivant = ߛߣߍ߬ߞߍ ߓߌ߬ߟߊ߬ߢߐ߲߰ߡߊ ߘߎ߰ߞߟߏ ߓߊߟߏߣߍ߲ ߡߊ߬
   - Sol vivant = ߘߎ߰ߞߟߏ ߓߊߟߏߣߍ߲
   - Bio-intensif = ߛߣߍ߬ߞߍ ߓߌ߬ߟߊ߬ߢߐ߲߰ߡߊ
   - Planches de culture permanentes = ߛߍ߬ߣߍ ߟߊ߬ߘߊ߲߬ߠߌ߲ ߓߟߐߞߐ (ou ߛߍ߬ߣߍ ߟߊ߬ߘߊ߲߬ߠߌ߲)
   - Passe-pieds = ߕߊ߯ߡߊߟߌ ߛߌߟߊ (ou ߛߋ߲߬ߘߏ߲߬ߘߊ)
   - Compost = ߞߏ߲ߔߏߛߌߕߌ (ou ߝߍߘߍ߲ߝߋ߲ ߣߐ߰)
   - Irrigation douce et globale = ߖߌ ߟߊߓߏ߬ߦߊ߬ߟߌ ߡߢߊߣߍ߲ ߊ߬ ߣߌ߫ ߓߍ߯ߦߊߡߊ
   - Humus = ߤߎߡߎߛߌ (ߘߎ߰ߞߟߏ ߝߟߍߣߍ߲ ߠߊߞߎߘߦߊߟߊ߲)
   - Vers de terre = ߘߎ߱ ߕߎߡߎ (ou ߛߊ߬ߡߊ߲)
   - Bactéries / champignons = ߡߢߐߞߎߡߐ߲ ߠߎ߬ ߣߌ߫ ߝߎ߲ߝߎ߲ ߠߎ߬
2. Utilise STRICTEMENT des caractères Unicode N'ko valides (ߒߞߏ).
3. Ne traduis JAMAIS les clés JSON ou les chemins d'images. Réponds STRICTEMENT par un JSON valide avec les clés "title" et "text".
"""

def call_ai(user_prompt, max_retries=3):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.15
    }
    for attempt in range(max_retries):
        try:
            r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                m = re.search(r"\{[\s\S]*\}", content)
                if m:
                    return json.loads(m.group(0), strict=False)
            time.sleep(2 ** attempt)
        except Exception as e:
            print(f"Erreur API: {e}", flush=True)
            time.sleep(2)
    return None

def translate_pages(fr_file, nko_file, start_page=1):
    with open(fr_file, 'r', encoding='utf-8') as f:
        fr_data = json.load(f)
    with open(nko_file, 'r', encoding='utf-8') as f:
        nko_data = json.load(f)
    
    fr_pages = fr_data.get("pages", [])
    nko_pages = nko_data.get("pages", [])
    
    total = len(fr_pages)
    print(f"\nTraitement {os.path.basename(nko_file)} ({total} pages)...", flush=True)
    
    for i, p_fr in enumerate(fr_pages):
        page_num = p_fr.get("page_number", i + 1)
        if page_num < start_page:
            continue
        
        # Vérifier si déjà traduit en N'ko
        p_nko = nko_pages[i] if i < len(nko_pages) else {}
        cur_text = p_nko.get("text", "")
        cur_title = p_nko.get("title", "")
        
        # Test Nko Unicode range U+07C0-U+07FF
        has_nko = any('\u07c0' <= c <= '\u07ff' for c in cur_text + cur_title)
        if has_nko and len(cur_text) > 0 and not any(mot in cur_title for mot in ["POUR QUE", "Planches", "Dans"]):
            print(f"  Page {page_num}/{total} déjà en N'ko. Skip.", flush=True)
            continue
            
        print(f"  Traduction Page {page_num}/{total}...", flush=True)
        user_prompt = f"""Traduis le contenu pédagogique de cette diapositive maraîchère du français vers le Bamanankan en écriture N'ko (ߒߞߏ):

Titre en français:
{p_fr.get('title', '')}

Texte en français:
{p_fr.get('text', '')}

Retourne STRICTEMENT cet objet JSON:
{{
  "title": "...",
  "text": "..."
}}"""
        res = call_ai(user_prompt)
        if res and ("title" in res or "text" in res):
            p_nko["title"] = res.get("title", cur_title)
            p_nko["text"] = res.get("text", cur_text)
            nko_pages[i] = p_nko
            # Sauvegarde incrémentale
            with open(nko_file, 'w', encoding='utf-8') as f:
                json.dump(nko_data, f, ensure_ascii=False, indent=2)
            print(f"  ✓ Page {page_num} traduite et enregistrée.", flush=True)
        else:
            print(f"  ✗ Échec traduction page {page_num}.", flush=True)
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 translate_nko_courses.py <fr_file> <nko_file> [start_page]")
        sys.exit(1)
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    translate_pages(sys.argv[1], sys.argv[2], start)

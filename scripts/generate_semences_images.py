#!/usr/bin/env python3
"""
Pipeline de génération et optimisation d'illustrations pédagogiques pour Campus Nakôbio.
Style : Aquarelle botanique lumineuse, traits fins sepia/encre, textures papier chaud, 100% sans texte.
"""

import os
import sys
import json
import base64
import time
import io
import urllib.request
import urllib.error
from PIL import Image

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not API_KEY and os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if line.startswith("OPENROUTER_API_KEY="):
                API_KEY = line.strip().split("=", 1)[1]

MODEL = "google/gemini-3.1-flash-image"

STYLE_PREFIX = (
    "Masterful, luminous botanical watercolor and ink illustration for an African agricultural training manual. "
    "Technique: Delicate sepia and dark ink outlines, subtle cross-hatching, filled with luminous organic transparent watercolor washes "
    "(earthy moss green, warm terracotta, dark fertile loam, warm golden ochre, vibrant natural vegetable colors). "
    "Paper: Warm cream slightly textured artisan watercolor paper with gentle, soft watercolor blooms. "
    "Composition: Clear, educational, pedagogical focus showing traditional West African agroecological context. "
    "STRICT COMPLIANCE RULE: ZERO TEXT, NO LABELS, NO LETTERS, NO WORDS, NO NUMBERS, NO CAPTIONS, NO SCHEMATIC LABELS. PURE CLEAN ARTWORK ONLY. "
)

def generate_image_for_prompt(prompt_text, max_retries=3):
    full_prompt = f"{STYLE_PREFIX}\nSubject / Scene details:\n{prompt_text}"
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": full_prompt}
                ]
            }
        ]
    }
    
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://campus.nako.bio",
            "X-Title": "Nakobio Campus Semences"
        }
    )
    
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                choice = res["choices"][0]["message"]
                if "images" in choice and choice["images"]:
                    img_obj = choice["images"][0]
                    if isinstance(img_obj, dict):
                        url = img_obj.get("url") or img_obj.get("image_url", {}).get("url") or img_obj.get("b64_json")
                        if url and url.startswith("data:"):
                            return base64.b64decode(url.split(",")[-1])
                        elif url and url.startswith("http"):
                            return urllib.request.urlopen(url).read()
                        else:
                            return base64.b64decode(url)
                    else:
                        img_str = str(img_obj)
                        return base64.b64decode(img_str.split(",")[-1])
                raise ValueError("No images field in response")
        except Exception as e:
            print(f"    [!] Tentative {attempt}/{max_retries} échouée : {e}")
            if attempt < max_retries:
                time.sleep(3 * attempt)
            else:
                raise e

def process_semences_module(module_file):
    json_path = f"src/data/{module_file}"
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Fichier introuvable: {json_path}")
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    mod_id = data["id"]
    pages = data.get("pages", [])
    out_dir = f"public/assets/images/{mod_id}"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"\n=======================================================")
    print(f"Module : {mod_id} ({len(pages)} pages)")
    print(f"Dossier de sortie : {out_dir}")
    print(f"=======================================================")
    
    for p in pages:
        p_num = p["page_number"]
        target_path = f"{out_dir}/page_{p_num:02d}.jpg"
        
        if os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
            print(f"  [✓] Page {p_num:02d}/{len(pages)} déjà existante, passage.")
            continue
            
        desc = p.get("illustration_description") or p.get("title")
        prompt = f"Title: {p.get('title')}\nPedagogical visual description: {desc}\nKey context: {p.get('text', '')[:200]}"
        
        print(f"  [>] Génération Page {p_num:02d}/{len(pages)}: {p.get('title')[:45]}...")
        try:
            img_bytes = generate_image_for_prompt(prompt)
            # Optimisation & sauvegarde JPEG qualité 85
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            # Redimensionner si trop grand (largeur max 1280px)
            if img.width > 1280:
                ratio = 1280 / float(img.width)
                new_h = int(float(img.height) * ratio)
                img = img.resize((1280, new_h), Image.Resampling.LANCZOS)
                
            img.save(target_path, "JPEG", quality=85, optimize=True)
            kb = os.path.getsize(target_path) // 1024
            print(f"      ✓ Page {p_num:02d} enregistrée ({kb} KB)")
            time.sleep(1)
        except Exception as e:
            print(f"      ❌ Erreur sur la page {p_num:02d}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/generate_semences_images.py <module_json_file_in_src_data>")
        print("Exemple: python3 scripts/generate_semences_images.py a2_classification_botanique_simplifiee.json")
        sys.exit(1)
    process_semences_module(sys.argv[1])

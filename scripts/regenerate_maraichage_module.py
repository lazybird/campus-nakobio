#!/usr/bin/env python3
"""
Pipeline officiel de transformation des visuels Maraîchage Nakôbio :
- Format 16:9 / Ratio Semences (1376x768 ou 1280x720)
- Règle stricte Nakôbio : ZÉRO PLANCHE EN BOIS, ZÉRO COFFRAGE (sol vivant pur en pleine terre)
- Respect rigoureux des schémas d'origine et suppression intégrale des textes/labels
- Dégradé périphérique doux vers le blanc pur (#ffffff) sur les 4 bordures
"""

import os
import sys
import json
import base64
import time
import io
import subprocess
from PIL import Image, ImageFilter
import urllib.request
import urllib.error

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not API_KEY and os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if line.startswith("OPENROUTER_API_KEY="):
                API_KEY = line.strip().split("=", 1)[1]
MODEL = "google/gemini-3.1-flash-image"

STYLE_PROMPT = (
    "Transform this technical agricultural slide diagram into a warm, masterfully crafted botanical watercolor and ink illustration in full 16:9 landscape format (ratio 1.78, exactly like a rich traditional botanical atlas plate): "
    "- EXACT COMPOSITION FIDELITY: Faithfully replicate the exact layout, subject matter, biological figures, plant anatomy, roots, cross-sections, and educational flows from the input slide. "
    "- STRICT NAKÔBIO BIO-INTENSIVE AGRONOMIC RULE: "
    "  * Permanent garden beds (\"planches de culture\") in Nakôbio agroecology are PURE LIVING SOIL and organic mulch directly on the ground, separated by simple earth/mulched footpaths (\"passe-pieds\"). "
    "  * STRICTLY FORBIDDEN: NEVER DRAW WOODEN PLANKS, WOODEN BOXES, TIMBER BOARDS, RAISED WOODEN FRAMES, BRICKS OR RAISED GARDEN BEDS. \"Planche\" in French means a flat earthen bed, NOT a wooden plank! "
    "- NATURAL BACKGROUND & PERIMETER FADE: "
    "  * Warm cream/off-white watercolor paper background with organic paint blooms and visible pigment grain. "
    "  * The outer edges of the illustration must softly and gracefully fade out into pure white (#ffffff) near the 4 borders (soft watercolor vignette). "
    "- STRIP ALL TEXT: Remove all words, letters, labels, numbers, banners, and callout boxes. Keep only the pure biological drawings, tools, and technical figures."
)

def apply_subtle_edge_white_fade(img, margin_x=65, margin_y=45):
    w, h = img.size
    pixels = []
    w_thresh = w - 1 - margin_x
    h_thresh = h - 1 - margin_y
    for y in range(h):
        fy = y / float(margin_y) if y < margin_y else ((h - 1 - y) / float(margin_y) if y > h_thresh else 1.0)
        for x in range(w):
            fx = x / float(margin_x) if x < margin_x else ((w - 1 - x) / float(margin_x) if x > w_thresh else 1.0)
            f = min(fx, fy)
            if fx < 1.0 and fy < 1.0:
                dx, dy = 1.0 - fx, 1.0 - fy
                dist = (dx * dx + dy * dy) ** 0.5
                f = 0.0 if dist >= 1.0 else min(f, 1.0 - dist)
            f_smooth = f * f * (3.0 - 2.0 * f)
            pixels.append(int(round(255.0 * f_smooth)))
    mask = Image.new("L", (w, h))
    mask.putdata(pixels)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=2))
    white = Image.new("RGB", (w, h), (255, 255, 255))
    return Image.composite(img, white, mask)

def render_slide_from_pdf(pdf_path, page_num, out_png):
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    prefix = out_png.rsplit('.', 1)[0]
    cmd = ["pdftoppm", "-png", "-r", "150", "-f", str(page_num), "-l", str(page_num), pdf_path, prefix]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    generated = f"{prefix}-{page_num:02d}.png"
    if not os.path.exists(generated):
        generated = f"{prefix}-{page_num}.png"
    if os.path.exists(generated):
        os.replace(generated, out_png)
        return out_png
    parent = os.path.dirname(out_png)
    for f in os.listdir(parent):
        if f.startswith(os.path.basename(prefix)) and f.endswith(".png"):
            os.replace(os.path.join(parent, f), out_png)
            return out_png
    raise FileNotFoundError(f"Failed to render page {page_num} of {pdf_path}")

def call_gemini(png_path):
    im = Image.open(png_path)
    im.thumbnail((1280, 720))
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": STYLE_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_img}"
                        }
                    }
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
            "X-Title": "Nakobio Campus"
        }
    )
    
    with urllib.request.urlopen(req, timeout=90) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        choice = res["choices"][0]["message"]
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
            return base64.b64decode(str(img_obj).split(",")[-1])

def process_module(module_id, pdf_path, start_page=1, end_page=None, force=False):
    print(f"\n==========================================")
    print(f"RÉGÉNÉRATION MODULE : {module_id}")
    print(f"PDF source : {pdf_path}")
    print(f"==========================================")
    
    json_path = f"src/data/maraichage/{module_id}.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    pages = data.get("pages", [])
    tmp_dir = f"/tmp/maraichage_renders/{module_id}"
    out_dir = f"public/assets/images/maraichage/{module_id}"
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    
    for page in pages:
        p_num = page["page_number"]
        if p_num < start_page:
            continue
        if end_page and p_num > end_page:
            break
            
        target_img = f"{out_dir}/page_{p_num:02d}.jpg"
        
        # Cas spécial : si on a déjà pré-généré la page 4 et 5 en V2 dans le brain
        if module_id == "201_sols_vivants" and p_num in (4, 5) and not force:
            brain_sample = f"/home/sylvain/.gemini/antigravity/brain/95dd9df2-c527-40eb-b3e5-9bf584829ee0/samples/page_201_{p_num:02d}_v2_fidele_sans_bois.jpg"
            if os.path.exists(brain_sample):
                print(f"  [✓] Page {p_num:02d} : Copie de la version V2 validée.")
                img = Image.open(brain_sample)
                img.save(target_img, "JPEG", quality=92, optimize=True)
                continue
                
        print(f"  [>] Génération Page {p_num:02d} / {len(pages)} : {page['title'][:40]}...")
        try:
            slide_png = f"{tmp_dir}/slide_{p_num:02d}.png"
            render_slide_from_pdf(pdf_path, p_num, slide_png)
            
            raw_bytes = call_gemini(slide_png)
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            
            # Application du dégradé blanc progressif
            img_faded = apply_subtle_edge_white_fade(img, margin_x=65, margin_y=45)
            
            tmp_target = target_img + ".tmp.jpg"
            img_faded.save(tmp_target, "JPEG", quality=92, optimize=True)
            os.replace(tmp_target, target_img)
            
            w, h = img_faded.size
            print(f"      ✓ Sauvegardé avec succès : {w}x{h} ({os.path.getsize(target_img)//1024} KB)")
            time.sleep(1.5)
        except Exception as e:
            print(f"      ❌ Erreur sur la page {p_num}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 regenerate_maraichage_module.py <module_id> <pdf_path> [start_page] [end_page]")
        sys.exit(1)
        
    mod = sys.argv[1]
    pdf = sys.argv[2]
    s_p = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    e_p = int(sys.argv[4]) if len(sys.argv) > 4 else None
    process_module(mod, pdf, start_page=s_p, end_page=e_p)

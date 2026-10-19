#!/usr/bin/env python3
"""
Pipeline de transformation des visuels du cursus Maraîchage en aquarelle botanique sans texte.
Prend en entrée le slide original extrait du PDF et le convertit via OpenRouter (Gemini Image).
"""

import os
import sys
import json
import base64
import time
import io
import subprocess
from PIL import Image
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
    "Transform this educational agricultural slide/diagram into a warm, masterfully crafted botanical watercolor and ink illustration: "
    "- Exact style match: Fine sepia/dark ink outlines and cross-hatching, filled with rich organic transparent watercolor washes (earthy moss green, dark fertile soil browns, warm ochres, sunlit tones). "
    "- Painted on slightly aged warm cream textured watercolor paper with visible gentle paint blooms and grain. "
    "- Perfectly preserve the technical layout, subject, objects, biological elements, plants, and composition from the input slide. "
    "- CRITICAL STRICT RULE: STRIP OUT AND COMPLETELY REMOVE ALL TEXT, LABELS, LETTERS, NUMBERS, POINTERS, CALLOUT BOXES, AND WORDS. "
    "The image must be 100% PURE ARTWORK with ZERO TEXT, clean and ready for international translation."
)

def render_slide_from_pdf(pdf_path, page_num, out_png):
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    # pdftoppm 1-indexed
    prefix = out_png.rsplit('.', 1)[0]
    cmd = ["pdftoppm", "-png", "-r", "150", "-f", str(page_num), "-l", str(page_num), pdf_path, prefix]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    generated = f"{prefix}-{page_num:02d}.png"
    if not os.path.exists(generated):
        generated = f"{prefix}-{page_num}.png"
    if os.path.exists(generated):
        os.replace(generated, out_png)
        return out_png
    # Find any matching generated file
    parent = os.path.dirname(out_png)
    for f in os.listdir(parent):
        if f.startswith(os.path.basename(prefix)) and f.endswith(".png"):
            os.replace(os.path.join(parent, f), out_png)
            return out_png
    raise FileNotFoundError(f"Failed to render page {page_num} of {pdf_path}")

def crop_diagram_only(image_path):
    im = Image.open(image_path)
    w, h = im.size
    # Crop to diagram only (most slides have the green summary box at the bottom 40%)
    # Keep top 60-65%
    cropped = im.crop((0, 0, w, int(h * 0.62)))
    cropped.thumbnail((1280, 1280))
    buf = io.BytesIO()
    cropped.save(buf, format="PNG")
    return buf.getvalue()

def generate_watercolor(input_png_bytes):
    b64_img = base64.b64encode(input_png_bytes).decode("utf-8")
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

def process_module(module_id, pdf_path, max_pages=None, start_page=1):
    print(f"\n==========================================")
    print(f"Traîtement du module : {module_id}")
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
        if max_pages and p_num > max_pages:
            break
            
        target_img = f"{out_dir}/page_{p_num:02d}.jpg"
        if os.path.exists(target_img):
            print(f"  [✓] Page {p_num:02d} existe déjà, passage.")
            continue
            
        print(f"  [>] Génération Page {p_num:02d} / {len(pages)} : {page['title'][:40]}...")
        try:
            slide_png = f"{tmp_dir}/slide_{p_num:02d}.png"
            render_slide_from_pdf(pdf_path, p_num, slide_png)
            cropped_bytes = crop_diagram_only(slide_png)
            
            img_bytes = generate_watercolor(cropped_bytes)
            
            # Save as optimized JPEG
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img.save(target_img, "JPEG", quality=90, optimize=True)
            print(f"      ✓ Sauvegardé avec succès ({os.path.getsize(target_img)//1024} KB)")
            time.sleep(1) # Gentle sleep between calls
        except Exception as e:
            print(f"      ❌ Erreur sur la page {p_num}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 generate_maraichage_images.py <module_id> <pdf_path> [max_pages] [start_page]")
        sys.exit(1)
        
    mod = sys.argv[1]
    pdf = sys.argv[2]
    max_p = int(sys.argv[3]) if len(sys.argv) > 3 else None
    start_p = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    process_module(mod, pdf, max_pages=max_p, start_page=start_p)

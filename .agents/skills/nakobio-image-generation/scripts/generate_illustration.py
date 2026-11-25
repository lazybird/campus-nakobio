#!/usr/bin/env python3
"""
Outil consolidé de génération, correction et post-traitement d'illustrations
pour Campus Nakôbio (Maraîchage & Semences).

Modèle : google/gemini-3.1-flash-image via OpenRouter
Charte : Aquarelle botanique 16:9, papier crème chaud (#FBF5ED/#F8EDE4),
         encre sépia, zéro texte, zéro planche en bois, fondu blanc périphérique.
"""

import argparse
import base64
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from PIL import Image, ImageFilter

MODEL = "google/gemini-3.1-flash-image"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

PROMPT_PDF = (
    "Transforme ce schéma / cette slide agricole en une illustration chaleureuse à l'aquarelle botanique et à l'encre sépia au format paysage 16:9 (ratio 1.78, style planche d'atlas botanique traditionnel) : "
    "- FIDÉLITÉ TECHNIQUE : Reproduis fidèlement la mise en page, les éléments biologiques, l'anatomie des plantes, les racines, les coupes de sol, les outils et les flux pédagogiques de l'image source. "
    "- CONTEXTE & REPRÉSENTATION OUEST-AFRICAINE : Lorsque des personnes, agriculteurs, agricultrices ou mains apparaissent, représente d'authentiques personnes ouest-africaines aux traits du visage africains naturels, à la peau brun clair à brun chaud (lavis doux terre de Sienne / terre cuite) et aux vêtements ruraux pratiques, dans un environnement agricole ouest-africain / sahélien. "
    "- RÈGLE AGRONOMIQUE STRICTE NAKÔBIO : "
    "  * Les planches de culture permanentes sont en PLEINE TERRE VIVANTE et paillis organique directement au sol, séparées par de simples passe-pieds en terre ou paillés. "
    "  * INTERDICTION ABSOLUE : ne dessine JAMAIS de planches de bois, caissons en bois, coffrages, bordures en briques ou bacs surélevés. "
    "- PALETTE & PAPIER : "
    "  * Traits fins à l'encre sépia/foncée (#886951, #B08967) et hachures subtiles, lavis d'aquarelle transparents et organiques (vert olive/mousse patiné #9A9178, terre cuite #D3B591, sable ocre #E8D1B3, terre humifère). Jamais de vert fluo. "
    "  * Fond : papier aquarelle artisanal crème chaud (#FBF5ED, #F8EDE4) avec de douces auréoles de pigments et un grain visible — strictement AUCUN fond blanc numérique pur (#FFFFFF) façon autocollant au cœur du dessin. "
    "  * Les 4 bords extérieurs de l'illustration s'estompent doucement vers le blanc pur (#FFFFFF) en vignette aquarelle légère. "
    "- SUPPRESSION TOTALE DU TEXTE : Retire 100% des mots, lettres, étiquettes, chiffres, bandeaux, flèches annotées et encadrés de texte. Ne garde que le dessin pur."
)

PROMPT_TEXT = (
    "Illustration pédagogique lumineuse à l'aquarelle botanique et à l'encre sépia, au format paysage 16:9 (ratio 1.78), pour un manuel de formation agroécologique ouest-africain. "
    "- Technique : Traits fins à l'encre sépia/foncée (#886951, #B08967), hachures subtiles, lavis d'aquarelle transparents et organiques (vert olive/mousse patiné #9A9178, terre cuite #D3B591, sable ocre #E8D1B3, terre humifère). Jamais de couleurs fluo. "
    "- Contexte & représentation ouest-africaine : Lorsque des personnes, agriculteurs, agricultrices ou mains apparaissent, représenter d'authentiques personnes ouest-africaines aux traits du visage africains naturels, à la peau brun clair à brun chaud (lavis doux terre de Sienne / terre cuite) et aux vêtements ruraux pratiques, dans un environnement ouest-africain / sahélien. "
    "- Papier : Papier aquarelle artisanal crème chaud (#FBF5ED, #F8EDE4) avec de douces auréoles et du grain — strictement AUCUN fond blanc numérique pur (#FFFFFF) au centre. Les 4 bords extérieurs s'estompent doucement vers le blanc (#FFFFFF). "
    "- Règle agronomique : Les planches de culture sont en pleine terre vivante paillée directement au sol avec des passe-pieds en terre — JAMAIS de planches de bois, caissons en bois ou briques. "
    "- RÈGLE STRICTE ZÉRO TEXTE : AUCUN TEXTE, aucune lettre, aucun mot, aucun chiffre, aucune étiquette ni légende. Uniquement le dessin pur."
)

PROMPT_EDIT = (
    "Modifie cette illustration à l'aquarelle botanique en préservant exactement son style aquarelle artisanal chaud "
    "(papier crème #FBF5ED/#F8EDE4, traits d'encre sépia #886951, palette terreuse et vert olive doux #9A9178/#D3B591/#E8D1B3), "
    "sa composition paysage 16:9, ses bords fondus vers le blanc et la règle zéro texte. "
    "Garde tous les autres éléments inchangés. STRICTEMENT ZÉRO TEXTE, ZÉRO PLANCHE DE BOIS OU CAISSON."
)


def load_api_key():
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    for candidate in (".env", os.path.join(os.getcwd(), ".env")):
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("OPENROUTER_API_KEY="):
                        return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("OPENROUTER_API_KEY introuvable (ni dans l'environnement, ni dans .env).")


def apply_smoothstep_white_fade(img, margin_x=65, margin_y=45):
    """Applique un fondu périphérique doux (smoothstep) vers #FFFFFF sur les 4 bords."""
    img = img.convert("RGB")
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


def render_pdf_page(pdf_path, page_num):
    """Extrait une page PDF (1-indexed) en PNG via pdftoppm."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefix = os.path.join(tmpdir, "slide")
        cmd = ["pdftoppm", "-png", "-r", "150", "-f", str(page_num), "-l", str(page_num), pdf_path, prefix]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for fname in os.listdir(tmpdir):
            if fname.endswith(".png"):
                with open(os.path.join(tmpdir, fname), "rb") as f:
                    return f.read()
    raise FileNotFoundError(f"Impossible de rendre la page {page_num} de {pdf_path}")


def image_to_b64_png(raw_bytes, max_size=(1280, 720)):
    im = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    im.thumbnail(max_size, Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def call_openrouter(prompt_text, input_image_bytes=None, max_retries=3):
    api_key = load_api_key()
    content = [{"type": "text", "text": prompt_text}]
    if input_image_bytes is not None:
        b64_img = image_to_b64_png(input_image_bytes)
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}})

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content}],
    }
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://campus.nako.bio",
            "X-Title": "Nakobio Campus",
        },
    )

    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
            choice = res["choices"][0]["message"]
            images = choice.get("images") or []
            if not images:
                raise ValueError(f"Aucune image retournée par le modèle : {choice.get('content', '')[:200]}")
            img_obj = images[0]
            if isinstance(img_obj, dict):
                url = img_obj.get("url") or img_obj.get("image_url", {}).get("url") or img_obj.get("b64_json")
                if url and url.startswith("data:"):
                    return base64.b64decode(url.split(",", 1)[-1])
                if url and url.startswith("http"):
                    return urllib.request.urlopen(url, timeout=60).read()
                return base64.b64decode(url)
            return base64.b64decode(str(img_obj).split(",", 1)[-1])
        except Exception as e:
            print(f"[!] Tentative {attempt}/{max_retries} échouée : {e}", file=sys.stderr)
            if attempt < max_retries:
                time.sleep(3 * attempt)
            else:
                raise


def save_atomic_jpeg(img, out_path, quality=92):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    tmp_path = out_path + ".tmp.jpg"
    img.convert("RGB").save(tmp_path, "JPEG", quality=quality, optimize=True)
    os.replace(tmp_path, out_path)


def main():
    parser = argparse.ArgumentParser(description="Générateur d'illustrations calibrées Campus Nakôbio")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--pdf", help="Chemin du PDF source (utiliser avec --page)")
    mode.add_argument("--prompt", help="Description textuelle de la scène (mode sans PDF)")
    mode.add_argument("--edit", help="Chemin d'une image existante à corriger (utiliser avec --extra)")
    mode.add_argument("--postprocess-only", help="Applique uniquement le fondu blanc sur une image existante")

    parser.add_argument("--page", type=int, help="Numéro de page PDF (1-indexed, requis avec --pdf)")
    parser.add_argument("--extra", default="", help="Consignes supplémentaires ou description du correctif")
    parser.add_argument("--out", required=True, help="Chemin de sortie JPEG")
    parser.add_argument("--no-fade", action="store_true", help="Désactive le fondu blanc périphérique")
    parser.add_argument("--margin-x", type=int, default=65, help="Marge horizontale du fondu blanc (défaut: 65)")
    parser.add_argument("--margin-y", type=int, default=45, help="Marge verticale du fondu blanc (défaut: 45)")
    parser.add_argument("--quality", type=int, default=92, help="Qualité JPEG (défaut: 92)")
    args = parser.parse_args()

    if args.postprocess_only:
        img = Image.open(args.postprocess_only).convert("RGB")
        if not args.no_fade:
            img = apply_smoothstep_white_fade(img, margin_x=args.margin_x, margin_y=args.margin_y)
        save_atomic_jpeg(img, args.out, quality=args.quality)
        print(f"✓ Post-traité : {args.out} ({img.width}x{img.height}, {os.path.getsize(args.out)//1024} KB)")
        return

    if args.pdf:
        if not args.page:
            parser.error("--page est requis avec --pdf")
        src_bytes = render_pdf_page(args.pdf, args.page)
        full_prompt = PROMPT_PDF
        if args.extra:
            full_prompt += f"\n- ADDITIONAL INSTRUCTIONS: {args.extra}"
        raw_out = call_openrouter(full_prompt, input_image_bytes=src_bytes)
    elif args.edit:
        if not args.extra:
            parser.error("--extra (description du correctif) est requis avec --edit")
        with open(args.edit, "rb") as f:
            src_bytes = f.read()
        full_prompt = f"{PROMPT_EDIT}\nApply ONLY the following correction(s):\n{args.extra}"
        raw_out = call_openrouter(full_prompt, input_image_bytes=src_bytes)
    else:
        full_prompt = f"{PROMPT_TEXT}\nSubject / Scene details:\n{args.prompt}"
        if args.extra:
            full_prompt += f"\nAdditional instructions:\n{args.extra}"
        raw_out = call_openrouter(full_prompt)

    img = Image.open(io.BytesIO(raw_out)).convert("RGB")
    if not args.no_fade:
        img = apply_smoothstep_white_fade(img, margin_x=args.margin_x, margin_y=args.margin_y)
    save_atomic_jpeg(img, args.out, quality=args.quality)
    print(f"✓ Généré : {args.out} ({img.width}x{img.height}, {os.path.getsize(args.out)//1024} KB)")


if __name__ == "__main__":
    main()

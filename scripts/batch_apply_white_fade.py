#!/usr/bin/env python3
"""
Script de généralisation du dégradé périphérique vers le blanc
pour les modules de formation Semences (Campus Nakôbio).
- Efface proprement les pastilles/triangles d'angle résiduels.
- Éclaircit sélectivement les fonds denses (notamment Comme une grande famille humaine - Variante B validée).
- Applique une transition douce (courbe smoothstep) vers le blanc pur (#ffffff) sur les 4 bordures.
- Sauvegarde en place les images optimisées.
"""

import os
import math
import shutil
from PIL import Image, ImageFilter

SEMENCES_DIRS = [
    f"public/assets/images/a{i}_{name}"
    for i, name in [
        (1, "cest_quoi_une_graine"),
        (2, "classification_botanique_simplifiee"),
        (3, "comment_choisir_ses_semences_de_depart"),
        (4, "la_pollinisation"),
        (5, "la_selection_des_plantes_porte_graines"),
        (6, "techniques_disolement"),
        (7, "extraction_sechage_tri_et_conservation"),
    ]
    if os.path.isdir(f"public/assets/images/a{i}_{name}")
]

BACKUP_ROOT = ".dev/backup_semences_all"

def create_fade_mask(w, h, margin_x=75, margin_y=50):
    pixels = []
    w_thresh = w - 1 - margin_x
    h_thresh = h - 1 - margin_y
    for y in range(h):
        if y < margin_y:
            fy = y / float(margin_y)
        elif y > h_thresh:
            fy = (h - 1 - y) / float(margin_y)
        else:
            fy = 1.0
            
        for x in range(w):
            if x < margin_x:
                fx = x / float(margin_x)
            elif x > w_thresh:
                fx = (w - 1 - x) / float(margin_x)
            else:
                fx = 1.0
                
            f = min(fx, fy)
            if fx < 1.0 and fy < 1.0:
                dx = 1.0 - fx
                dy = 1.0 - fy
                dist = math.sqrt(dx * dx + dy * dy)
                if dist >= 1.0:
                    f = 0.0
                else:
                    f = min(f, 1.0 - dist)
                    
            f_smooth = f * f * (3.0 - 2.0 * f)
            pixels.append(int(round(255.0 * f_smooth)))
            
    mask = Image.new("L", (w, h))
    mask.putdata(pixels)
    return mask.filter(ImageFilter.GaussianBlur(radius=2))

def clean_corner_tag(img):
    w, h = img.size
    c = img.getpixel((0, 0))
    if c[0] > 100 and c[1] < 60 and c[2] < 60:
        pixels = list(img.getdata())
        for y in range(min(120, h)):
            for x in range(min(120, w)):
                if x + y <= 110:
                    idx = y * w + x
                    r, g, b = pixels[idx]
                    if r > 90 and g < 70 and b < 70:
                        pixels[idx] = (255, 255, 255)
        out = Image.new("RGB", (w, h))
        out.putdata(pixels)
        return out
    return img

def lighten_dense_background(img, bg_color=(233, 216, 198)):
    w, h = img.size
    pixels = list(img.getdata())
    new_pixels = []
    for r, g, b in pixels:
        diff = math.sqrt((r - bg_color[0])**2 + (g - bg_color[1])**2 + (b - bg_color[2])**2)
        if diff < 25:
            factor = 0.85
        elif diff < 60:
            factor = 0.50
        else:
            factor = 0.20
        nr = min(255, max(0, int(r + (255 - r) * factor)))
        ng = min(255, max(0, int(g + (255 - g) * factor)))
        nb = min(255, max(0, int(b + (255 - b) * factor)))
        new_pixels.append((nr, ng, nb))
    out = Image.new("RGB", (w, h))
    out.putdata(new_pixels)
    return out

def process_and_save(src_path, dst_path, is_famille_humaine=False):
    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    
    img = clean_corner_tag(img)
    if is_famille_humaine:
        img = lighten_dense_background(img)
        
    mask = create_fade_mask(w, h, margin_x=75, margin_y=50)
    white_bg = Image.new("RGB", (w, h), (255, 255, 255))
    result = Image.composite(img, white_bg, mask)
    
    # Écriture atomique
    tmp_path = dst_path + ".tmp.jpg"
    result.save(tmp_path, "JPEG", quality=92, optimize=True)
    os.replace(tmp_path, dst_path)

def main():
    total_processed = 0
    os.makedirs(BACKUP_ROOT, exist_ok=True)
    
    for mod_dir in SEMENCES_DIRS:
        mod_name = os.path.basename(mod_dir)
        backup_dir = os.path.join(BACKUP_ROOT, mod_name)
        os.makedirs(backup_dir, exist_ok=True)
        
        files = sorted([f for f in os.listdir(mod_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"\n=======================================================")
        print(f"Traitement : {mod_name} ({len(files)} illustrations)")
        print(f"=======================================================")
        
        for f in files:
            full_path = os.path.join(mod_dir, f)
            backup_file = os.path.join(backup_dir, f)
            
            # Sauvegarder l'original pré-fade dans le backup si absent
            if not os.path.exists(backup_file):
                shutil.copy2(full_path, backup_file)
                
            # Pour la source, prendre la sauvegarde originale pour éviter les ré-applications multiples
            src_file = backup_file if os.path.exists(backup_file) else full_path
            is_famille = (mod_name == "a2_classification_botanique_simplifiee" and f == "page_02.jpg")
            
            process_and_save(src_file, full_path, is_famille_humaine=is_famille)
            total_processed += 1
            label = " [VARIANTE B VALIDÉE]" if is_famille else ""
            print(f"  [✓] Dégradé blanc appliqué : {f}{label}")

    print(f"\n[SUCCÈS] Total de {total_processed} illustrations traitées avec dégradé vers le blanc.")

if __name__ == "__main__":
    main()

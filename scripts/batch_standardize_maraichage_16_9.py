#!/usr/bin/env python3
"""
Script d'harmonisation standard 16:9 pour les illustrations maraîchage.
- Prend en source les images originales sauvegardées dans .dev/backup_maraichage_all
- Applique un dégradé doux progressif vers le blanc pur (#ffffff) sur les bordures
- Monte la planche panoramique au centre d'un canvas blanc 16:9 standard (1280x720 px)
- Sauvegarde en place les fichiers dans public/assets/images/maraichage
"""

import os
import math
import shutil
from PIL import Image, ImageFilter

MARAICHAGE_ROOT = "public/assets/images/maraichage"
BACKUP_ROOT = ".dev/backup_maraichage_all"
TARGET_WIDTH = 1280
TARGET_HEIGHT = 720 # 16:9 exact

def get_module_dirs():
    dirs = []
    if not os.path.exists(MARAICHAGE_ROOT):
        return dirs
    for entry in sorted(os.listdir(MARAICHAGE_ROOT)):
        full = os.path.join(MARAICHAGE_ROOT, entry)
        if os.path.isdir(full):
            dirs.append(full)
    return dirs

def create_fade_mask(w, h, margin_x=70, margin_y=45):
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

def process_image(src_path, dst_path):
    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    
    # 1. Appliquer le dégradé doux vers le blanc pur sur les bordures natives
    mx = max(35, int(round(65.0 * (w / 1200.0))))
    my = max(30, int(round(45.0 * (h / 700.0))))
    mask = create_fade_mask(w, h, margin_x=mx, margin_y=my)
    white_bg = Image.new("RGB", (w, h), (255, 255, 255))
    faded_img = Image.composite(img, white_bg, mask)
    
    # 2. Harmoniser sur ratio 16:9
    target_ratio = 16.0 / 9.0
    img_ratio = w / float(h)
    
    if img_ratio > target_ratio + 0.05:
        # Image plus large que 16:9 (panoramique classique 1745x608)
        # On crée un canvas blanc avec une hauteur proportionnelle à la largeur pour avoir 16:9
        pad_h = int(round(w / target_ratio))
        canvas = Image.new("RGB", (w, pad_h), (255, 255, 255))
        y_offset = (pad_h - h) // 2
        canvas.paste(faded_img, (0, y_offset))
        final_img = canvas.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    elif img_ratio < target_ratio - 0.05:
        # Image plus haute que 16:9
        pad_w = int(round(h * target_ratio))
        canvas = Image.new("RGB", (pad_w, h), (255, 255, 255))
        x_offset = (pad_w - w) // 2
        canvas.paste(faded_img, (x_offset, 0))
        final_img = canvas.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    else:
        # Déjà proche de 16:9
        final_img = faded_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
        
    # Écriture atomique
    tmp_path = dst_path + ".tmp.jpg"
    final_img.save(tmp_path, "JPEG", quality=92, optimize=True)
    os.replace(tmp_path, dst_path)

def main():
    total_processed = 0
    module_dirs = get_module_dirs()
    print(f"Modules maraîchage trouvés : {len(module_dirs)}")
    
    for mod_dir in module_dirs:
        mod_name = os.path.basename(mod_dir)
        backup_dir = os.path.join(BACKUP_ROOT, mod_name)
        
        files = sorted([f for f in os.listdir(mod_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"\n=======================================================")
        print(f"Traitement 16:9 : {mod_name} ({len(files)} illustrations)")
        print(f"=======================================================")
        
        for f in files:
            full_path = os.path.join(mod_dir, f)
            backup_file = os.path.join(backup_dir, f)
            src_file = backup_file if os.path.exists(backup_file) else full_path
            
            process_image(src_file, full_path)
            total_processed += 1
            print(f"  [✓] 16:9 blanc standardisé : {f}")

    print(f"\n[SUCCÈS] Total de {total_processed} illustrations maraîchage harmonisées au standard 16:9 ({TARGET_WIDTH}x{TARGET_HEIGHT}).")

if __name__ == "__main__":
    main()

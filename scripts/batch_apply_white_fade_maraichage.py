#!/usr/bin/env python3
"""
Script de généralisation du dégradé périphérique vers le blanc
pour les modules de formation Maraîchage en Sol Vivant (Campus Nakôbio).
- Applique une transition douce (courbe smoothstep) vers le blanc pur (#ffffff) sur les 4 bordures.
- Crée une sauvegarde miroir sous .dev/backup_maraichage_all avant toute modification.
- Écriture atomique avec optimisation JPEG qualité 92.
"""

import os
import math
import shutil
from PIL import Image, ImageFilter

MARAICHAGE_ROOT = "public/assets/images/maraichage"
BACKUP_ROOT = ".dev/backup_maraichage_all"

def get_module_dirs():
    dirs = []
    if not os.path.exists(MARAICHAGE_ROOT):
        return dirs
    for entry in sorted(os.listdir(MARAICHAGE_ROOT)):
        full = os.path.join(MARAICHAGE_ROOT, entry)
        if os.path.isdir(full):
            dirs.append(full)
    return dirs

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

def process_and_save(src_path, dst_path):
    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    
    # Adapter la marge aux proportions réelles de l'image
    mx = max(40, int(round(75.0 * (w / 1200.0))))
    my = max(35, int(round(50.0 * (h / 700.0))))
    
    mask = create_fade_mask(w, h, margin_x=mx, margin_y=my)
    white_bg = Image.new("RGB", (w, h), (255, 255, 255))
    result = Image.composite(img, white_bg, mask)
    
    # Écriture atomique
    tmp_path = dst_path + ".tmp.jpg"
    result.save(tmp_path, "JPEG", quality=92, optimize=True)
    os.replace(tmp_path, dst_path)

def main():
    total_processed = 0
    os.makedirs(BACKUP_ROOT, exist_ok=True)
    
    module_dirs = get_module_dirs()
    print(f"Modules maraîchage trouvés : {len(module_dirs)}")
    
    for mod_dir in module_dirs:
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
                
            # Utiliser la sauvegarde comme source pour garantir une application propre
            src_file = backup_file if os.path.exists(backup_file) else full_path
            
            process_and_save(src_file, full_path)
            total_processed += 1
            print(f"  [✓] Dégradé blanc appliqué : {f}")

    print(f"\n[SUCCÈS] Total de {total_processed} illustrations maraîchage traitées avec dégradé vers le blanc.")

if __name__ == "__main__":
    main()

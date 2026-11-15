#!/usr/bin/env python3
"""
Script de recalibrage colorimétrique global pour Campus Nakôbio.
Harmonise la palette des modules de formation récents (a2, a3, etc.)
vers la palette de référence de la vague initiale (octobre 2025).
Préserve à 100% la netteté et la géométrie des dessins originaux.
"""

import os
import math
import shutil
from PIL import Image

REF_DIR = ".dev/2025-10-13 - Images formation semences"
TARGET_MODULES = [
    "public/assets/images/a2_classification_botanique_simplifiee",
    "public/assets/images/a3_comment_choisir_ses_semences_de_depart"
]
BACKUP_DIR = ".dev/backup_pre_recalibration"

def rgb_to_lab(r, g, b):
    r_lin = r / 255.0
    g_lin = g / 255.0
    b_lin = b / 255.0
    L = max(0.3811 * r_lin + 0.5783 * g_lin + 0.0402 * b_lin, 1e-5)
    M = max(0.1967 * r_lin + 0.7244 * g_lin + 0.0782 * b_lin, 1e-5)
    S = max(0.0241 * r_lin + 0.1288 * g_lin + 0.8444 * b_lin, 1e-5)
    L_log = math.log10(L)
    M_log = math.log10(M)
    S_log = math.log10(S)
    l_val = (L_log + M_log + S_log) / 1.7320508
    alpha = (L_log + M_log - 2 * S_log) / 2.4494897
    beta = (L_log - M_log) / 1.41421356
    return l_val, alpha, beta

def lab_to_rgb(l_val, alpha, beta):
    L_log = (l_val / 1.7320508) + (alpha / 2.4494897) + (beta / 1.41421356)
    M_log = (l_val / 1.7320508) + (alpha / 2.4494897) - (beta / 1.41421356)
    S_log = (l_val / 1.7320508) - (2 * alpha / 2.4494897)
    L, M, S = 10**L_log, 10**M_log, 10**S_log
    r_lin =  4.4679 * L - 3.5873 * M + 0.1193 * S
    g_lin = -1.2186 * L + 2.3809 * M - 0.1624 * S
    b_lin =  0.0497 * L - 0.2439 * M + 1.2045 * S
    r = min(255, max(0, int(r_lin * 255.0 + 0.5)))
    g = min(255, max(0, int(g_lin * 255.0 + 0.5)))
    b = min(255, max(0, int(b_lin * 255.0 + 0.5)))
    return r, g, b

def compute_reference_stats():
    print(f"[*] Analyse de la palette de référence dans {REF_DIR}...")
    ref_images = [os.path.join(REF_DIR, f) for f in os.listdir(REF_DIR) if f.lower().endswith(('.jpg', '.png'))]
    ref_samples = []
    for p in ref_images:
        im = Image.open(p).convert('RGB').resize((80, 45))
        for pixel in im.getdata():
            ref_samples.append(rgb_to_lab(*pixel))
            
    mean_l = sum(x[0] for x in ref_samples) / len(ref_samples)
    mean_a = sum(x[1] for x in ref_samples) / len(ref_samples)
    mean_b = sum(x[2] for x in ref_samples) / len(ref_samples)
    std_l = math.sqrt(sum((x[0] - mean_l)**2 for x in ref_samples) / len(ref_samples))
    std_a = math.sqrt(sum((x[1] - mean_a)**2 for x in ref_samples) / len(ref_samples))
    std_b = math.sqrt(sum((x[2] - mean_b)**2 for x in ref_samples) / len(ref_samples))
    print(f"[✓] Référence calculée : L_moy={mean_l:.4f}, a_moy={mean_a:.4f}, b_moy={mean_b:.4f}")
    return (mean_l, mean_a, mean_b, std_l, std_a, std_b)

def calibrate_image(img_path, ref_stats, strength=0.85):
    mean_ref_l, mean_ref_a, mean_ref_b, std_ref_l, std_ref_a, std_ref_b = ref_stats
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    small = img.resize((80, 45))
    src_samples = [rgb_to_lab(*pixel) for pixel in small.getdata()]
    
    mean_src_l = sum(x[0] for x in src_samples) / len(src_samples)
    mean_src_a = sum(x[1] for x in src_samples) / len(src_samples)
    mean_src_b = sum(x[2] for x in src_samples) / len(src_samples)
    
    std_src_l = max(1e-4, math.sqrt(sum((x[0] - mean_src_l)**2 for x in src_samples) / len(src_samples)))
    std_src_a = max(1e-4, math.sqrt(sum((x[1] - mean_src_a)**2 for x in src_samples) / len(src_samples)))
    std_src_b = max(1e-4, math.sqrt(sum((x[2] - mean_src_b)**2 for x in src_samples) / len(src_samples)))
    
    pixels = list(img.getdata())
    out_pixels = []
    
    scale_l = (std_ref_l / std_src_l) * strength + (1.0 - strength)
    scale_a = (std_ref_a / std_src_a) * strength + (1.0 - strength)
    scale_b = (std_ref_b / std_src_b) * strength + (1.0 - strength)
    
    for r, g, b in pixels:
        l_val, alpha, beta = rgb_to_lab(r, g, b)
        nl = (l_val - mean_src_l) * scale_l + (mean_ref_l * strength + mean_src_l * (1 - strength))
        na = (alpha - mean_src_a) * scale_a + (mean_ref_a * strength + mean_src_a * (1 - strength))
        nb = (beta - mean_src_b) * scale_b + (mean_ref_b * strength + mean_src_b * (1 - strength))
        nr, ng, nnb = lab_to_rgb(nl, na, nb)
        out_pixels.append((nr, ng, nnb))
        
    out_img = Image.new('RGB', (w, h))
    out_img.putdata(out_pixels)
    return out_img

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ref_stats = compute_reference_stats()
    
    total_processed = 0
    for mod_path in TARGET_MODULES:
        mod_name = os.path.basename(mod_path)
        mod_backup = os.path.join(BACKUP_DIR, mod_name)
        os.makedirs(mod_backup, exist_ok=True)
        
        files = sorted([f for f in os.listdir(mod_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"\n=======================================================")
        print(f"Recalibrage du module : {mod_name} ({len(files)} fichiers)")
        print(f"=======================================================")
        
        for f in files:
            full_path = os.path.join(mod_path, f)
            backup_file = os.path.join(mod_backup, f)
            
            # 1. Sauvegarde préalable sécurisée
            if not os.path.exists(backup_file):
                shutil.copy2(full_path, backup_file)
                
            # 2. Recalibrage
            calibrated = calibrate_image(full_path, ref_stats, strength=0.85)
            calibrated.save(full_path, "JPEG", quality=90, optimize=True)
            total_processed += 1
            print(f"  [✓] Recalibré : {f}")

    print(f"\n[SUCCÈS] Total de {total_processed} illustrations recalibrées avec succès.")
    print(f"[NOTE] Sauvegardes originales conservées dans : {BACKUP_DIR}")

if __name__ == "__main__":
    main()

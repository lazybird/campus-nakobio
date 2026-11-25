---
name: nakobio-image-generation
description: >-
  Pipeline automatisé Antigravity pour générer, régénérer, corriger et
  post-traiter les illustrations du Campus Nakôbio via OpenRouter
  (google/gemini-3.1-flash-image), scripts Python et recalibrage colorimétrique.
  S'appuie sur la charte métier nakobio-charte-illustrations.
---

# Pipeline Automatisé de Génération d'Images — Campus Nakôbio

Ce skill couvre la **partie technique et automatisation** dans le dépôt
`nakobio/campus` (OpenRouter, extraction PDF, post-traitement *smoothstep* et
recalibrage colorimétrique LAB).

> **Charte métier (couleurs, règles agronomiques, prompts)** : voir le skill
> partageable [nakobio-charte-illustrations](../nakobio-charte-illustrations/SKILL.md).

---

## 1. Configuration Technique

| Paramètre | Valeur |
| :--- | :--- |
| **Endpoint API** | `https://openrouter.ai/api/v1/chat/completions` |
| **Modèle** | `google/gemini-3.1-flash-image` |
| **Authentification** | `OPENROUTER_API_KEY` (variable d'environnement ou `.env` à la racine) |
| **Dépendances locales** | Python 3, `Pillow` (`PIL`), `pdftoppm` (`poppler-utils`) |
| **Export** | JPEG optimisé (`quality=92`, `optimize=True`), écriture atomique via `.tmp.jpg` |
| **Post-traitement** | Fondu périphérique *smoothstep* vers `#FFFFFF` (`margin_x=65`, `margin_y=45`, `GaussianBlur(radius=2)`) |

---

## 2. Script Consolidé (Usage Unitaire & Correctifs)

Le script `.agents/skills/nakobio-image-generation/scripts/generate_illustration.py`
embarque la charte métier et le post-traitement *smoothstep* :

```bash
# 1. Slide PDF -> Aquarelle 16:9 + fondu blanc
python3 .agents/skills/nakobio-image-generation/scripts/generate_illustration.py \
  --pdf ".dev/maraichage/supports/version HR/Version 169 Irrigation.pdf" \
  --page 4 \
  --out "public/assets/images/maraichage/302_mettre_en_place_lirrigation/page_04.jpg"

# 2. Slide PDF avec consigne supplémentaire
python3 .agents/skills/nakobio-image-generation/scripts/generate_illustration.py \
  --pdf ".dev/maraichage/supports/..." \
  --page 7 \
  --extra "Show drip irrigation tubes directly on mulched soil, no wooden borders" \
  --out "public/assets/images/maraichage/<module>/page_07.jpg"

# 3. Correctif ciblé sur une image existante
python3 .agents/skills/nakobio-image-generation/scripts/generate_illustration.py \
  --edit "public/assets/images/maraichage/301_realiser_les_planches_de_cultures/page_05.jpg" \
  --extra "Remove wooden planks around the garden bed, use flat mulched living soil" \
  --out "public/assets/images/maraichage/301_realiser_les_planches_de_cultures/page_05.jpg"

# 4. Création depuis une description (sans PDF)
python3 .agents/skills/nakobio-image-generation/scripts/generate_illustration.py \
  --prompt "Cross-section of a three-bay compost pile in a West African garden..." \
  --out "public/assets/images/maraichage/<module>/page_01.jpg"

# 5. Post-traitement fondu blanc seul (sans appel API)
python3 .agents/skills/nakobio-image-generation/scripts/generate_illustration.py \
  --postprocess-only "public/assets/images/maraichage/<module>/page_01.jpg" \
  --out "public/assets/images/maraichage/<module>/page_01.jpg"
```

---

## 3. Scripts Batch du Dépôt

- **Régénération complète d'un module Maraîchage depuis PDF** :
  `python3 scripts/regenerate_maraichage_module.py <module_id> "<pdf_path>" [start_page] [end_page]`
  *(Attention : ne plus utiliser l'ancien `scripts/generate_maraichage_images.py` qui rognait à 62% et produisait un ratio panoramique étroit 2.87).*
- **Génération batch Semences depuis JSON** :
  `python3 scripts/generate_semences_images.py <module_json_in_src_data>`
- **Recalibrage colorimétrique non-destructif (transfert LAB vers Vague 1)** :
  `python3 scripts/batch_recalibrate_semences.py` — harmonise la teinte vers `.dev/2025-10-13 - Images formation semences` (`strength=0.85`) sans altérer le dessin.
- **Fondu blanc périphérique en batch** :
  `scripts/batch_apply_white_fade.py` (Semences, `margin_x=75, margin_y=50`) / `scripts/batch_apply_white_fade_maraichage.py` (Maraîchage, `margin_x=65, margin_y=45`).

---

## 4. Conventions de Fichiers & Sécurité

- **Maraîchage** : `public/assets/images/maraichage/<module_id>/page_<NN>.jpg`
- **Semences** : `public/assets/images/<module_id>/page_<NN>.jpg`
- **Sauvegardes** : avant un batch destructif, sauvegarder dans `.dev/backup_.../` (ignoré par Git).
- **Vérification** : appliquer la checklist qualité de `nakobio-charte-illustrations` avant tout commit.

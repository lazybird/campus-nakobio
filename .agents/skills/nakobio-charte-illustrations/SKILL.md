---
name: nakobio-charte-illustrations
description: >-
  Charte graphique, règles agronomiques et prompts de référence pour créer ou
  corriger les illustrations pédagogiques aquarelle du Campus Nakôbio (Maraîchage
  et Semences). Agnostique de l'outil IA (Gemini, ChatGPT, Claude, etc.) et
  conçu pour être partagé avec toute l'équipe.
---

# Charte Métier des Illustrations — Campus Nakôbio

Ce document rassemble les **règles visuelles, colorimétriques et agronomiques**
à respecter pour toute création ou retouche d'illustration pédagogique du Campus
Nakôbio (cursus Maraîchage & Semences), **quel que soit l'outil utilisé**
(Gemini, ChatGPT, Claude, ou retouche manuelle).

---

## 1. Identité Visuelle & Style

- **Style** : Aquarelle botanique et encre sépia, inspirée des planches
  d'atlas botanique traditionnel — chaleureuse, lumineuse, lisible et
  pédagogique.
- **Format** : **Paysage 16:9** (ex. `1376 × 768 px` ou `1280 × 720 px`),
  identique pour les cours Semences et Maraîchage.
- **Bordures** : L'illustration doit s'estomper doucement vers le blanc pur
  (`#FFFFFF`) sur les 4 bords extérieurs (effet vignette aquarelle douce), afin
  de s'intégrer sans cadre ni bordure nette sur les pages blanches du site.

---

## 2. Palette de Couleurs Officielle (Vague 1 — Référence)

| Rôle | Teinte & Ambiance | Code HEX | Usage |
| :--- | :--- | :--- | :--- |
| **Fond / Papier** | Blanc cassé / Papier crème | `#FBF5ED` / `#F8EDE4` | Fond aquarelle chaud naturel au cœur du dessin (**jamais** de blanc numérique pur `#FFFFFF` dans le dessin) |
| **Ombres douces** | Sable chaud / Ocre clair | `#E8D1B3` | Lavis de fond, transitions douces |
| **Terre / Peau** | Terre cuite / Argile dorée | `#D3B591` | Sols tropicaux/sahéliens, graines, mains de cultivateurs |
| **Contraste & Traits** | Brun loam / Sépia doux | `#B08967` & `#886951` | Traits d'encre sépia, hachures fines, écorces, ombrages |
| **Végétal** | Vert olive / Mousse patinée | `#9A9178` | Feuillages et plantes (vert naturel atténué, **jamais** fluo ou saturé) |

> [!IMPORTANT]
> **Éviter l'effet « autocollant détouré »** : le fond de l'illustration doit
> conserver une texture de papier aquarelle crème chaleureux (`#FBF5ED` /
> `#F8EDE4`). Seule la périphérie extérieure se fond doucement vers le blanc
> `#FFFFFF`.

---

## 3. Règles Agronomiques & Pédagogiques Strictes (Nakôbio)

1. **ZÉRO planche en bois / ZÉRO coffrage** :
   - En maraîchage bio-intensif Nakôbio, une *« planche de culture »* est une
     **bande de pleine terre vivante** paillée directement au sol, séparée par
     de simples passe-pieds en terre ou en paillis.
   - **Interdiction absolue** de dessiner des planches de bois, caissons,
     coffrages, bordures en briques ou bacs surélevés (erreur fréquente des IA
     qui traduisent littéralement le mot *« planche »* par du bois).
2. **ZÉRO texte dans l'image** :
   - **Aucun** mot, lettre, chiffre, étiquette, titre, légende ou bulle de texte
     ne doit apparaître dans l'illustration.
   - Les cours sont traduits en plusieurs langues (français, anglais, allemand,
     bamanankan, n'ko) : l'image doit être 100% visuelle.
3. **Contexte géographique & représentation humaine ouest-africaine** :
   - **Personnages (agriculteurs, agricultrices, mains)** : privilégier systématiquement des personnes **ouest-africaines** — traits du visage africains naturels, peau **brun clair à brun chaud** (rendue en lavis d'aquarelle doux terre de Sienne / ombre naturelle, jamais pâle ni caricaturale), vêtements pratiques du quotidien rural ouest-africain.
   - **Environnement** : sols tropicaux / sahéliens (terre chaude, latérite, sol humifère), outils locaux, végétaux et paysages d'Afrique de l'Ouest.
4. **Fidélité pédagogique** :
   - Lorsqu'on reprend un schéma de cours existant, conserver exactement la
     logique technique (coupes de sol, racines, circulation de l'eau, étapes du
     compost, outils) sans inventer d'éléments parasites.

---

## 4. Prompts Prêts à Copier-Coller

### A. Créer une nouvelle illustration depuis une description
```text
Masterful, luminous botanical watercolor and ink illustration in full 16:9 landscape format for a West African agroecological training manual.
- Style: Delicate sepia/dark ink outlines (#886951, #B08967), subtle cross-hatching, organic transparent watercolor washes (muted moss green #9A9178, warm terracotta #D3B591, sandy ochre #E8D1B3, fertile loam). Never neon colors.
- West African Context & Representation: Whenever people, farmers, or hands appear, depict authentic West African individuals with natural African facial features, warm light-to-medium brown skin tones (rendered with gentle sienna/terracotta watercolor washes), and practical rural West African farming attire. Set scenes in a West African / Sahelian agroecological environment with local tools and warm soils.
- Paper & Borders: Unbroken warm artisan cream watercolor paper (#FBF5ED, #F8EDE4) with gentle paint blooms and grain — strictly NO sterile pure digital white (#FFFFFF) sticker background inside the artwork. Outer edges softly fade toward white (#FFFFFF) near the 4 borders.
- Strict Agronomic Rule: Garden beds ("planches de culture") are pure living soil and organic mulch directly on the ground with earthen footpaths — NEVER draw wooden planks, wooden boxes, raised wooden frames, or bricks.
- Strict Text Rule: ZERO TEXT, NO LABELS, NO LETTERS, NO WORDS, NO NUMBERS, NO CAPTIONS. Pure clean artwork only.

Scene to illustrate:
[DÉCRIRE LA SCÈNE ICI]
```

### B. Transformer un schéma / slide existant en aquarelle
*(Joindre l'image du schéma ou de la slide source)*
```text
Transform this agricultural slide/diagram into a warm botanical watercolor and ink illustration in full 16:9 landscape format (traditional botanical atlas plate):
- Faithfully preserve the exact technical layout, biological elements, roots, cross-sections, tools, and educational flows from the input image.
- WEST AFRICAN CONTEXT & REPRESENTATION: Adapt any people, farmers, or hands into authentic West African individuals with natural African facial features, warm light-to-medium brown skin tones (soft sienna/terracotta watercolor washes), and practical rural West African clothing, in a West African / Sahelian agricultural setting.
- STRICT AGRONOMIC RULE: Permanent garden beds ("planches de culture") are PURE LIVING SOIL and organic mulch directly on the ground, separated by simple earthen/mulched footpaths. NEVER draw wooden planks, wooden boxes, timber boards, raised frames, or bricks.
- COLOR & PAPER: Sepia ink outlines (#886951, #B08967), muted olive/moss green (#9A9178), terracotta (#D3B591), warm sand ochre (#E8D1B3), on warm artisan cream watercolor paper (#FBF5ED, #F8EDE4) — NO sterile pure white (#FFFFFF) sticker background inside the artwork. Softly fade the 4 outer edges toward white (#FFFFFF).
- STRIP ALL TEXT: Remove 100% of words, letters, labels, numbers, banners, and callout boxes. Keep ONLY the pure artwork.
```

### C. Corriger une illustration existante (retouche ciblée)
*(Joindre l'illustration existante à corriger)*
```text
Edit this botanical watercolor illustration while preserving its exact warm artisan watercolor style (#FBF5ED/#F8EDE4 cream paper, sepia ink outlines #886951, muted earthy/olive palette), 16:9 landscape composition, soft white outer borders, and zero-text rule.
Apply ONLY the following correction(s):
[DÉCRIRE LE CORRECTIF PRÉCIS ICI — ex: "Remove the wooden planks around the garden bed and replace them with flat mulched living soil and earthen footpaths"]
Keep all other elements unchanged. STRICTLY ZERO TEXT, ZERO WOODEN PLANKS OR RAISED BOXES.
```

---

## 5. Checklist Qualité Avant Validation

Avant d'intégrer une illustration sur le Campus Nakôbio, vérifier :
- [ ] **Zéro texte** : aucune lettre, chiffre ou étiquette résiduelle.
- [ ] **Zéro bois / coffrage** : les planches de culture sont en pleine terre vivante paillée.
- [ ] **Palette chaude** : papier crème (`#FBF5ED`/`#F8EDE4`), encre sépia, verts olive doux (pas de vert fluo ni de fond blanc clinique).
- [ ] **Bords fondus** : les 4 bords s'estompent doucement vers le blanc (`#FFFFFF`).
- [ ] **Format 16:9** : cadrage paysage équilibré, cohérent avec les autres slides.
- [ ] **Justesse agronomique** : fidèle au contenu pédagogique de la slide.

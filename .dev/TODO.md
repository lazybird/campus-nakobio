# Roadmap & Backlog Technique — Campus Nakôbio

Ce document centralise les fonctionnalités planifiées et les spécifications techniques à implémenter dans les prochains cycles de développement.

---

## 1. Génération dynamique des PDF multilingues (FR, EN, DE, Bambara Latin, Bambara N'ko)

### Contexte & Objectif
- Les supports de formation au format PDF doivent être générés **dynamiquement** à partir du contenu source de la leçon (fichiers JSON de données).
- Lorsqu'une mise à jour est apportée au texte ou aux étapes d'un cours (en français ou en traduction), le PDF correspondant doit être automatiquement synchronisé et à jour sans intervention manuelle.
- Permettre le téléchargement dans la langue sélectionnée par l'utilisateur (ex. consultation du site en français/anglais, mais téléchargement direct du PDF en ߒߞߏ ou Bamanankan).

### Spécifications & Défis techniques
1. **Support complet du N'ko (ߒߞߏ) :**
   - Écriture de droite à gauche (**RTL** - Right-To-Left).
   - Embarquement de polices compatibles (ex: *Noto Sans NKo*, *Kigelia*).
   - Gestion du rendu et ligatures N'ko lors de la conversion PDF (via Puppeteer/Playwright headless, Typst, Weasyprint ou template HTML d'impression).
2. **Architecture de rendu :**
   - Endpoint de rendu / page dédiée d'impression (ex: `/semences/[id]/print?lang=bm-nko`) stylisée avec les règles CSS `@media print`.
   - Pipeline de génération statique au build ou à la demande selon les performances souhaitées.

---

## 2. Intégration Multimédia : Vidéos & Audio (YouTube / Médias enrichis)

### Contexte & Objectif
- Renforcer la transmission des savoirs agroécologiques auprès des apprenants et maraîchers sur le terrain (tradition orale forte, contextualisation visuelle des gestes techniques).
- Associer des contenus multimédias (vidéos / audios hébergés notamment sur YouTube) aux leçons.

### Spécifications fonctionnelles
1. **Granularité d'intégration :**
   - **Niveau cours :** Vidéo d'introduction globale du module.
   - **Niveau étape / section :** Possibilité de lier un extrait ou une vidéo spécifique à une étape précise d'un parcours (ex: le geste de pollinisation ou l'extraction des graines).
2. **Schéma de données (JSON) :**
   - Prévoir dans le schéma des leçons des champs optionnels :
     ```json
     {
       "media": {
         "type": "youtube",
         "url": "https://www.youtube.com/watch?v=...",
         "timestamp_start": 45,
         "title": "Démonstration du geste de sélection"
       }
     }
     ```
3. **UX & Performance :**
   - Chargement différé (*lazy-loading* / façade lite-youtube) pour préserver la bande passante sur mobile et connexions limitées en zone rurale.
   - Intégration ergonomique dans le visualiseur pas-à-pas (onglet ou volet média sans casser le flux de lecture).

=> Il serait logique que les vidéos "niveau cours" inclue par défaut toutes les vidéos du "niveau étape/section".

---

## 3. Gestion des langues & Déploiement progressif (Architecture validée)

- **UI Globale :** Français (par défaut), Anglais, Allemand (navigation standard LTR).
- **Contenu Pédagogique (Cours) :** Français, Anglais, Allemand, Bambara (Latin), Bambara (N'ko - ߒߞߏ).
- **Déploiement progressif :** Badges de disponibilité des langues sur les catalogues + fallback gracieux vers le français si une traduction n'est pas encore prête.

=> Le travail sur la gestion des langues au niveau de contenu de cours à été faite. On va laisser pour l'instant le sujet de la traduction du site qui est moins prioritaire et peut se faire quand le site sera plus testé.

---

## 4. Intégration et Génération d'Images de Formation (Semences & Maraîchage)

### Contexte & Objectif
- Harmoniser le style visuel de l'ensemble des formations (illustrations pédagogiques de type aquarelle botanique lumineuse, didactique et sans texte intégré).
- Remplacer les images manquantes ou placeholders par des visuels attrayants et optimisés.

### Pistes d'implémentation
1. **Intégration du lot existant (`.dev/Images formation semences`) :**
   - Associer les 18 illustrations déjà finalisées aux 18 étapes du module fondamental `a1_cest_quoi_une_graine`.
   - Renommer et déplacer dans `public/assets/images/a1_cest_quoi_une_graine/page_01.jpg` à `page_18.jpg` (en complétant les images 4, 5, 7 à 17 actuellement absentes).
2. **Poursuite de la génération d'images via OpenRouter :**
   - ✅ **Fondamentaux Semences (`a1` à `a7`) : 100% illustrés en production** (116 illustrations uniques au style aquarelle botanique sahélienne, sans texte).
   - Reste : Traiter les fiches espèces potagères (`b1` à `b27`) et les modules Maraîchage complémentaires.
   - Lier automatiquement les nouvelles images générées aux fichiers JSON correspondants et optimiser leur poids (WebP/compression).

---

## 5. Optimisation Mobile, UX Terrain & Économie de Bande Passante

### Contexte & Objectif
- La majorité des apprenants et producteurs accèdent au campus via smartphone, souvent avec des forfaits données limités et coûteux en zone rurale. L'application doit être rapide, intuitive au doigt et sobre en consommation réseau.

### Pistes d'implémentation
1. **Optimisation drastique des images :**
   - Conversion systématique des visuels au format moderne ultra-léger (**WebP / AVIF**).
   - Génération de déclinaisons responsives (`srcset`) : servir des résolutions adaptées aux écrans mobiles (max 480px / 720px de large) plutôt que les images source haute définition.
   - Attributs `loading="lazy"` et `decoding="async"` stricts sur toutes les diapositives et illustrations.
2. **Ergonomie Mobile (Touch-First) :**
   - Barre de navigation basse (*bottom bar*) fixée en bas d'écran dans le lecteur de cours : boutons "Précédent", "Suivant" et indicateur d'étapes dimensionnés pour une manipulation facile au pouce (`min-height: 48px`).
   - Sommaire et sélecteur de langues adaptés : affichage sous forme de tiroir tactile (*bottom sheet*) pour une sélection plus fluide que les menus déroulants natifs.
   - Amélioration de la lisibilité extérieure (contrastes renforcés, typographie claire min 16px).
3. **Persistance & Mode Hors-Ligne (PWA / Service Worker) :**
   - Mise en place d'une mise en cache locale des cours et images consultés (stratégie `CacheFirst` via Service Worker), évitant de reconsommer la data lors des réouvertures répétées d'une même fiche au champ.

---

## 6. Harmonisation de la Numérotation et Codification des Cursus

### Contexte & Objectif
- Deux logiques hétérogènes coexistent actuellement :
  - **Semences :** Codes alphanumériques (`A1` à `A7` pour les fondamentaux, `B1` à `B27` pour les fiches légumes, `C1`-`C2` pour les enquêtes).
  - **Maraîchage :** Codes numériques à trois chiffres (`101`, `201`, `301` à `306`, `401` à `403`).
- L'objectif est d'offrir une signalétique claire, professionnelle et uniforme aux apprenants à travers tout le catalogue.

### Pistes d'implémentation
1. **Normalisation des métadonnées (sans casser les URLs existantes) :**
   - Conserver les identifiants techniques actuels (fichiers/slugs) pour préserver les liens et l'historique.
   - Ajouter dans les fichiers JSON et catalogues un code pédagogique harmonisé et lisible :
     - Maraîchage : **M1.1**, **M2.1**, **M2.2**, **M3.1** à **M3.6**, **M4.1** à **M4.3** (structure modulaire issue de la conception).
     - Semences : **S1.01** à **S1.07** (Fondamentaux), **S2.01** à **S2.27** (Espèces potagères), **S3.01** (Outils de suivi).
2. **Affichage uniforme :**
   - Badges visuels standardisés sur les cartes de catalogue et dans le fil d'Ariane du lecteur (`[M3.2]`, `[S1.04]`).
=> Ok, pour le cours sur les outils, on pour utiliser la lettre T pour "Tools" ou "Technique".

---

## 7. Pipeline de Traduction Automatisée & Maîtrise des Coûts (OpenRouter)

### Contexte & Objectif
- Traduire les fiches de cours en **Anglais**, **Allemand**, **Bambara (alphabet latin)** et **Bambara (N'ko ߒߞߏ)**.
- Éviter d'impacter les quotas de tokens personnels en déportant la génération vers l'API OpenRouter avec les modèles les plus compétitifs et pertinents.

### Pistes d'implémentation
1. **Anglais (Maraîchage) : Exploitation des sources PDF existantes (Coût Token = 0)**
   - Extraire directement le texte déjà rédigé dans les PDF haute définition du dossier `.dev/maraichage/supports/version HR` (ex: `Anglais Version 169 Planches.pdf`, `Plant health.pdf`, `Crop rotation.pdf`).
   - Générer automatiquement les fichiers correspondants `src/data/maraichage/[id].en.json`.
2. **Anglais (Semences) & Allemand : Modèles IA haute performance à coût réduit**
   - Utiliser via OpenRouter des modèles performants et très économiques (ex: **DeepSeek V3 / Chat** ou **Qwen 2.5 72B** à ~$0.14-$0.20 / 1M tokens).
   - Coût estimé pour la traduction intégrale de tout le catalogue : < 0.50 $.
3. **Bambara Latin & Bambara N'ko (ߒߞߏ) : Modèles multilingues & Glossaire agronomique**
   - Évaluer via OpenRouter les modèles démontrant de fortes capacités multilingues peu dotées (**Gemini 1.5/2.0 Flash**, **Qwen 2.5 72B**) ou le modèle spécialisé **NLLB-200** (No Language Left Behind).
   - Injecter un glossaire terminologique agricole validé (termes clés : compost, semence reproductible, lit de semence, paillage, arrosage) pour garantir la justesse technique des traductions en Bamanankan.
   - Sauvegarde structurée dans `src/data/[cursus]/[id].[lang].json` avec prise en charge RTL pour le N'ko.
   
=> Pour les traduction, au vu du coût qui n'est pas élevé, je préfère aumenter le budget et utiliser de meilleurs modèles.
# Roadmap & Backlog Technique — Campus Nakôbio

Ce document centralise les fonctionnalités planifiées et les spécifications techniques à implémenter dans les prochains cycles de développement.

---

## 1. Génération dynamique des PDF multilingues (FR, EN, DE, Bambara Latin, Bambara N'ko) — ✅ RÉALISÉ

### Contexte & Objectif
- Les supports de formation au format PDF doivent être générés **dynamiquement** à partir du contenu source de la leçon (fichiers JSON de données).
- Lorsqu'une mise à jour est apportée au texte ou aux étapes d'un cours (en français ou en traduction), le PDF correspondant est automatiquement synchronisé et à jour sans intervention manuelle.
- Téléchargement direct ou impression dans la langue sélectionnée par l'utilisateur (consultation web et menu déroulant multilingue de téléchargement PDF immédiat en FR, EN, DE, Bamanankan Latin, ߒߞߏ).

### Implémentation réalisée :
1. **Support complet du N'ko (ߒߞߏ) & Mise en page Premium A4 :**
   - Écriture de droite à gauche (**RTL**) nativement gérée dans les fiches et feuilles de style print (`[dir="rtl"]`, `.is-rtl`).
   - Cartouche d'en-tête officiel Nakôbio dédié au print (`.print-official-banner`) avec logo/titre officiel, code module et langue.
   - Embarquement local de la police vectorielle *Noto Sans NKo* dans `public/assets/fonts/` avec `@font-face` assurant une indépendance réseau totale et des ligatures parfaites en impression/PDF.
2. **Architecture de rendu & Ergonomie UI :**
   - Rendu d'impression `@media print` unifié dans `src/styles/design-system/print.css` (mise en page A4 sans coupure de carte, suppression automatique des barres de navigation et vidéos interactives, ajustement des contrastes et paddings).
   - Menu déroulant intelligent dans la barre supérieure de chaque leçon (`/semences/[id]`, `/semences/[id]/[lang]`, `/maraichage/[id]`, `/maraichage/[id]/[lang]`) permettant à la fois le **téléchargement direct en 1 clic** avec noms explicites pour mobile/iPhone (ex: `Semences-S2.14-Produire-ses-semences-de-Carotte-FR.pdf`) et l'impression native locale/AirPrint.
3. **Outil CLI local puissant & incrémental (`.dev/scripts/generate_pdf.py`) :**
   - Conçu pour l'exécution locale sur machine de dev avant commit git.
   - **Détection intelligente par hash MD5** : ne recalcule que les cours dont le contenu source JSON a changé ou dont le PDF manque.
   - **Options de filtrage flexibles** :
     * `python3 .dev/scripts/generate_pdf.py` (incrémental)
     * `python3 .dev/scripts/generate_pdf.py -f` (force la régénération complète)
     * `python3 .dev/scripts/generate_pdf.py -c b14,101,302` (ciblage par numéros de cours ou codes)
     * `python3 .dev/scripts/generate_pdf.py -l bm-nko` (ciblage linguistique)
     * `python3 .dev/scripts/generate_pdf.py --cursus maraichage` (ciblage par cursus)
   - Maintien du cache dans `.dev/pdf_build_cache.json`.

---

## 2. Intégration Multimédia : Vidéos & Audio (YouTube / Médias enrichis)

### Contexte & Objectif
- Renforcer la transmission des savoirs agroécologiques auprès des apprenants et maraîchers sur le terrain (tradition orale forte, contextualisation visuelle des gestes techniques).
- Associer des contenus multimédias (vidéos / podcasts hébergés sur la chaîne officielle YouTube [@nakobio](https://www.youtube.com/@nakobio)) aux cours et à leurs étapes.
- Prise en compte rigoureuse de la langue active : les vidéos/audios présentés doivent correspondre à la langue de consultation sélectionnée (FR, EN, Bamanankan Latin & N'ko ߒߞߏ). *Note : le contenu Swahili de la chaîne n'est pas diffusé sur le campus.*

### 1. Granularité & Règle d'agrégation
- **Niveau cours (global) :** Zone multimédia située sous le sommaire des chapitres. Elle regroupe :
  1. Les vidéos générales / tutoriels liés au thème global du cours.
  2. Par agrégation automatique, toutes les vidéos rattachées aux différentes sections/parties du cours.
- **Niveau section / étape (local) :** Remplacement ergonomique de la zone "Partie suivante" (en bas de fiche) par un accordéon vidéo contextuel pour la section en cours.
- **Filtrage linguistique dynamique :**
  - Si l'utilisateur consulte le cours en **FR** ➔ vidéos/podcasts en français.
  - Si l'utilisateur consulte le cours en **EN** ➔ vidéos/podcasts en anglais (ex: *Harvest Preservation...* `mtrg--oDvFQ`, tutoriel maïs `l-XX1z31YZI`).
  - Si l'utilisateur consulte le cours en **Bambara (Latin ou N'ko ߒߞߏ)** ➔ vidéos et podcasts en bamanankan (ex: Épisodes 5 à 17 avec Seydou, formation Kalaban Koura `lfFnV5h3nS0`).
  - Fallback intelligent : possibilité d'afficher en second plan les versions originales si une langue n'a pas encore de vidéo dédiée.

### 2. Schéma de données (JSON de cours et pages)
Champs optionnels supportant le multilinguisme :
```json
{
  "media": [
    {
      "type": "youtube",
      "id": "INE31nI_iTI",
      "url": "https://www.youtube.com/watch?v=INE31nI_iTI",
      "lang": "fr",
      "category": "cours", // "cours" | "podcast" | "tutoriel"
      "title": "Conserver et Gérer les Récoltes : Méthodes et Bonnes Pratiques",
      "timestamp_start": 0
    }
  ]
}
```
*Note : peut être placé à la racine du JSON (cours) et/ou dans les objets `pages[]` (sections).*

### 3. Emplacements UX / UI retenus (Validés sur maquettes)
1. **Zone A — Hub vidéo sous le sommaire (`lesson-video-hub`) :**
   - Placée directement sous le bloc *« Sommaire des chapitres »*.
   - Dépliée/repliée via un composant accordéon `<details class="video-accordion-hub">` pour ne pas alourdir la page verticalement.
   - Affiche le compteur de vidéos disponibles dans la langue courante (ex: `🎥 Vidéos & Podcasts associés (3)`).
   - Onglets ou badges de filtre optionnels : "Tous", "Pratique / Terrain", "Podcasts d'échange".

2. **Zone B — En bas de chaque section (remplace le séparateur "Partie suivante") :**
   - La zone du lien "Partie suivante" (non indispensable grâce au défilement continu et aux repères de navigation) est remplacée ou enrichie par un panneau accordéon compact.
   - Accordéon fermé par défaut : *"🎥 Voir la démonstration pratique en vidéo (1)"*.
   - Une fois ouvert : lecteur vidéo intégré sans distraction.

### 4. Performance & Économie de bande passante (Connexions sahéliennes)
- **Façade Lite-YouTube (Zero-JS initial) :**
  - **Ne jamais charger l'iframe YouTube directement** au chargement de la page (économise ~1,2 Mo de JS et 15 requêtes Google par vidéo).
  - Utiliser une vignette WebP/JPEG légère (`https://i.ytimg.com/vi/{ID}/hqdefault.jpg`) avec un bouton de lecture central stylisé.
  - L'iframe YouTube n'est injectée dans le DOM **qu'au clic actif de l'apprenant** (`autoplay=1`).

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
   - ✅ **Fondamentaux Semences (`a1` à `a7`) : 100% illustrés en production** (116 illustrations uniques).
   - ✅ **Fiches Légumes Semences (`b1` à `b27`) : 100% illustrées en production** (345 illustrations uniques au style aquarelle botanique sans texte réparties sur les 27 fiches potagères).
   - **Total Cursus Semences Paysannes : 461 illustrations originales en ligne.**
   - Reste : Traiter les modules Maraîchage complémentaires.

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
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



---

## 3. Gestion des langues & Déploiement progressif (Architecture validée)

- **UI Globale :** Français (par défaut), Anglais, Allemand (navigation standard LTR).
- **Contenu Pédagogique (Cours) :** Français, Anglais, Allemand, Bambara (Latin), Bambara (N'ko - ߒߞߏ).
- **Déploiement progressif :** Badges de disponibilité des langues sur les catalogues + fallback gracieux vers le français si une traduction n'est pas encore prête.

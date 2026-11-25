# Charte Métier des Illustrations — Campus Nakôbio

Ce document rassemble les **règles visuelles, colorimétriques et agronomiques**
à respecter pour toute création ou retouche d'illustration pédagogique du Campus
Nakôbio (cursus Maraîchage & Semences), **quel que soit l'outil utilisé**
(Gemini, ChatGPT, Claude, ou retouche manuelle).


## 1. Identité Visuelle & Style

- **Style** : Aquarelle botanique et encre sépia, inspirée des planches
  d'atlas botanique traditionnel — chaleureuse, lumineuse, lisible et
  pédagogique.
- **Format** : **Paysage 16:9** (ex. `1376 × 768 px` ou `1280 × 720 px`),
  identique pour les cours Semences et Maraîchage.
- **Bordures** : L'illustration doit s'estomper doucement vers le blanc pur
  (`#FFFFFF`) sur les 4 bords extérieurs (effet vignette aquarelle douce), afin
  de s'intégrer sans cadre ni bordure nette sur les pages blanches du site.


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


## 4. Prompts Prêts à Copier-Coller

### A. Créer une nouvelle illustration depuis une description
```text
Illustration pédagogique lumineuse à l'aquarelle botanique et à l'encre sépia, au format paysage 16:9, pour un manuel de formation agroécologique ouest-africain.
- Style : Traits fins à l'encre sépia/foncée (#886951, #B08967), hachures subtiles, lavis d'aquarelle transparents et organiques (vert olive/mousse patiné #9A9178, terre cuite #D3B591, sable ocre #E8D1B3, terre humifère). Jamais de couleurs fluo.
- Contexte & représentation ouest-africaine : Lorsque des personnes, agriculteurs, agricultrices ou mains apparaissent, représenter d'authentiques personnes ouest-africaines aux traits du visage africains naturels, à la peau brun clair à brun chaud (rendue en lavis d'aquarelle doux terre de Sienne / terre cuite), vêtues de tenues rurales pratiques d'Afrique de l'Ouest, dans un environnement agroécologique ouest-africain / sahélien avec outils locaux et sols chauds.
- Papier & bordures : Papier aquarelle artisanal crème chaud et légèrement texturé (#FBF5ED, #F8EDE4) avec de douces auréoles de pigments — strictement AUCUN fond blanc numérique pur (#FFFFFF) façon autocollant au cœur du dessin. Les 4 bords extérieurs s'estompent doucement vers le blanc pur (#FFFFFF) en vignette légère.
- Règle agronomique stricte : Les planches de culture sont des bandes de pleine terre vivante et de paillis organique directement au sol, séparées par de simples passe-pieds en terre ou paillés. INTERDICTION ABSOLUE de dessiner des planches de bois, caissons en bois, coffrages, bordures en briques ou bacs surélevés.
- Règle zéro texte : STRICTEMENT AUCUN TEXTE, aucune lettre, aucun mot, aucun chiffre, aucune étiquette ni légende. Uniquement le dessin pur.

Scène à illustrer :
[DÉCRIRE LA SCÈNE ICI]
```

### B. Transformer un schéma / slide existant en aquarelle
*(Joindre l'image du schéma ou de la slide source)*
```text
Transforme ce schéma / cette slide agricole en une illustration chaleureuse à l'aquarelle botanique et à l'encre sépia au format paysage 16:9 (style planche d'atlas botanique traditionnel) :
- Fidélité technique : Reproduis fidèlement la mise en page, les éléments biologiques, l'anatomie des plantes, les racines, les coupes de sol, les outils et les flux pédagogiques de l'image source.
- Contexte & représentation ouest-africaine : Adapte toute personne, agriculteur, agricultrice ou main en d'authentiques personnes ouest-africaines aux traits du visage africains naturels, à la peau brun clair à brun chaud (lavis doux terre de Sienne / terre cuite) et aux vêtements ruraux pratiques, dans un environnement agricole ouest-africain / sahélien.
- Règle agronomique stricte : Les planches de culture permanentes sont en PLEINE TERRE VIVANTE et paillis organique directement au sol, séparées par de simples passe-pieds en terre ou paillés. INTERDICTION ABSOLUE de dessiner des planches de bois, caissons, coffrages, briques ou bacs surélevés.
- Couleurs & papier : Traits d'encre sépia (#886951, #B08967), vert olive/mousse patiné (#9A9178), terre cuite (#D3B591), sable ocre (#E8D1B3), sur papier aquarelle crème artisanal (#FBF5ED, #F8EDE4) — AUCUN fond blanc numérique pur (#FFFFFF) façon autocollant au centre. Les 4 bords extérieurs se fondent doucement vers le blanc (#FFFFFF).
- Suppression totale du texte : Retire 100% des mots, lettres, étiquettes, chiffres, bandeaux et encadrés de texte. Ne garde que le dessin pur.
```

### C. Corriger une illustration existante (retouche ciblée)
*(Joindre l'illustration existante à corriger)*
```text
Modifie cette illustration à l'aquarelle botanique en préservant exactement son style aquarelle artisanal chaud (papier crème #FBF5ED/#F8EDE4, traits d'encre sépia #886951, palette terreuse et vert olive doux), sa composition paysage 16:9, ses bords fondus vers le blanc et la règle zéro texte.
Applique UNIQUEMENT le(s) correctif(s) suivant(s) :
[DÉCRIRE LE CORRECTIF PRÉCIS ICI — ex. : "Supprimer les bordures en bois autour de la planche de culture et les remplacer par de la pleine terre paillée avec des passe-pieds en terre"]
Garde tous les autres éléments inchangés. STRICTEMENT ZÉRO TEXTE, ZÉRO PLANCHE DE BOIS OU CAISSON.
```


## 5. Checklist Qualité Avant Validation

Avant d'intégrer une illustration sur le Campus Nakôbio, vérifier :
- [ ] **Zéro texte** : aucune lettre, chiffre ou étiquette résiduelle.
- [ ] **Zéro bois / coffrage** : les planches de culture sont en pleine terre vivante paillée.
- [ ] **Palette chaude** : papier crème (`#FBF5ED`/`#F8EDE4`), encre sépia, verts olive doux (pas de vert fluo ni de fond blanc clinique).
- [ ] **Bords fondus** : les 4 bords s'estompent doucement vers le blanc (`#FFFFFF`).
- [ ] **Format 16:9** : cadrage paysage équilibré, cohérent avec les autres slides.
- [ ] **Justesse agronomique** : fidèle au contenu pédagogique de la slide.

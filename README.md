# Plateforme de Formation Agroécologique — Nakôbio

Site web développé avec [Astro](https://astro.build) pour diffuser les supports et formations en agroécologie adaptés aux climats sahéliens et tropicaux.

## Deux Parcours Pédagogiques

1. **Production de Semences Paysannes (`/semences`)**
   - 36 modules pratiques illustrés étape par étape (fondamentaux botaniques, isolement, pollinisation, extraction et 27 fiches espèces légumières).
   - Visualiseur pas-à-pas avec mode d'impression et export PDF optimisé pour le terrain.
   - Filtrage dynamique par catégorie et recherche instantanée.

2. **Maraîchage Bio-Intensif en Sol Vivant (`/maraichage`)**
   - Méthode de régénération biologique des sols et maraîchage intensif sur petites surfaces (planches permanentes, pépinières, irrigation).
   - Page d'attente sobre annonçant la version web interactive à venir.

---

## Prérequis

- [Node.js](https://nodejs.org/) v20+ ou v22+
- npm v10+

---

## Démarrage Rapide en Local

### 1. Installation des dépendances
```bash
npm install
```

### 2. Lancer le serveur de développement
```bash
npm run dev
```
Le site est disponible par défaut sur : `http://localhost:3000`

### 3. Compiler pour la production
```bash
npm run build
```
Les fichiers HTML/CSS/JS statiques sont générés dans le dossier `dist/`.

### 4. Prévisualiser le build localement
```bash
npm run preview
```

---

## Déploiement sur Dokploy

Ce projet utilise les standards de conteneurisation éprouvés sur l'écosystème Malihub (notamment `dsml`, `sites` et `jobavenir`). Un skill IA global `dokploy-astro-deployment` est également disponible dans Antigravity.

### Configuration du service dans Dokploy

1. **Création de l'application** : Créez une nouvelle application dans votre projet Dokploy.
2. **Fournisseur de code (Git Provider)** : Connectez votre dépôt GitHub.
3. **Type de Build** : Choisissez **Dockerfile**.
4. **Context de build** : `/` (racine de ce dépôt).
5. **Port de l'application** : `3000`.
6. **Domaine & SSL** : Dokploy configure automatiquement le routage Traefik et les certificats Let's Encrypt (HTTPS).

### Dockerfile utilisé
Le build utilise `node:22`, installe `sirv-cli` pour servir le dossier statique `dist/` avec support SPA/fallback (`--single`), compression et CORS :

```dockerfile
FROM node:22

WORKDIR /app
COPY package*.json ./
RUN npm install -g sirv-cli && npm install
COPY . .
RUN npm run build

EXPOSE 3000
CMD ["sirv", "dist", "--port", "3000", "--host", "0.0.0.0", "--cors", "--single"]
```

---

## Structure du Projet

```text
├── Dockerfile             # Configuration conteneur Dokploy
├── .dockerignore          # Fichiers exclus du build Docker
├── astro.config.mjs       # Configuration Astro (SSG)
├── package.json
├── public/                # Assets statiques distribués tels quels
│   ├── assets/images/     # Illustrations des cours et logos officiels
│   └── data/              # Fichiers JSON de données pour accès client
├── src/
│   ├── components/        # Navbar, Footer
│   ├── data/              # Données JSON sources compilées statiquement
│   ├── layouts/           # Layout principal (Layout.astro)
│   ├── pages/
│   │   ├── index.astro            # Landing page 2 parcours
│   │   ├── maraichage.astro       # Page d'attente maraîchage
│   │   └── semences/
│   │       ├── index.astro        # Catalogue 36 formations
│   │       └── [id].astro         # Visualiseur dynamique d'un cours
│   └── styles/
│       └── theme.css              # Charte graphique sobre
```

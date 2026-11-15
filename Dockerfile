FROM node:22

WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances
RUN npm install

# Copie de tout le code source
COPY . .

# Construction du site Astro (mode hybrid)
RUN npm run build

# Variables d'environnement serveur Astro Node
ENV HOST=0.0.0.0
ENV PORT=3000

# Port Dokploy standard
EXPOSE 3000

# Démarrage du serveur Node Astro
CMD ["node", "dist/server/entry.mjs"]

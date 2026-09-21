FROM node:22

WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances et sirv-cli pour le service statique
RUN npm install -g sirv-cli && npm install

# Copie de tout le code source
COPY . .

# Construction du site statique Astro
RUN npm run build

# Port Dokploy standard
EXPOSE 3000

# Démarrage du serveur statique compatible Traefik / Dokploy
CMD ["sirv", "dist", "--port", "3000", "--host", "0.0.0.0", "--cors", "--single"]

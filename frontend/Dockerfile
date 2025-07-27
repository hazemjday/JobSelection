# Utilise Node.js pour le développement
FROM node:18

# Crée le dossier de travail
WORKDIR /app

# Copie le reste du code source
COPY . .

# Expose le port 3000 (React)
EXPOSE 3000

# Lancement de l'app en mode dev
CMD ["npm", "start"]
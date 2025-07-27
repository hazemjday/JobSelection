FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# Étape 5 : Exposer le port Flask
EXPOSE 5000

# Étape 6 : Démarrer l'application
CMD ["python", "backend.py"]

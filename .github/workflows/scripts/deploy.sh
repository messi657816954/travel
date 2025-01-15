#!/bin/bash

# Définition des variables
APP_DIR=/var/www/travel
VENV_DIR=$APP_DIR/venv
GITHUB_REPO="messi657816954/travel"

# Mise à jour du code depuis GitHub
cd $APP_DIR || exit
git pull origin main

# Activation de l'environnement virtuel et mise à jour des dépendances
source $VENV_DIR/bin/activate
pip install -r requirements.txt

# Application des migrations
python manage.py migrate --noinput

# Collecte des fichiers statiques
python manage.py collectstatic --noinput

# Mise à jour des permissions
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Redémarrage d'Apache
sudo systemctl restart apache2

# Affichage d'un message de succès
echo "Déploiement terminé avec succès!"

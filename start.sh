#!/bin/bash

# Ce script démarre le serveur et ouvre l'application dans le navigateur.

# Trouve le répertoire où se trouve le script pour s'assurer que les commandes s'exécutent au bon endroit
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

# Arrête toute instance précédente du serveur pour éviter les conflits
_pkill -f generator.py


echo "Démarrage du serveur Flask en arrière-plan..."
# Lance le serveur en arrière-plan
python3 generator.py &

# Laisse un petit temps au serveur pour démarrer
sleep 3

echo "Ouverture de l'application dans votre navigateur..."
# Ouvre l'URL dans le navigateur par défaut de macOS
open http://127.0.0.1:5001

echo "C'est prêt ! Vous pouvez fermer cette fenêtre de terminal."

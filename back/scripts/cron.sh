#!/bin/bash

# 1. Définir le répertoire racine (parent de scripts/ et frère de venv/)
# On remonte de deux niveaux depuis 'back/scripts/' vers la racine du projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../" && pwd)"

# 2. Configurer les logs
LOG_FILE="$ROOT_DIR/back/logs/cron.log"
mkdir -p "$ROOT_DIR/back/logs"

echo "---  Lancement : $(date) ---" >> "$LOG_FILE"

# 3. Activation du VENV
# Le chemin vers le venv est ROOT_DIR/venv/
VENV_PATH="$ROOT_DIR/venv/bin/activate" # Windows (Git Bash/WSL)

if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
    echo " Environnement virtuel activé." >> "$LOG_FILE"
else
    echo " Erreur : venv introuvable à $VENV_PATH" >> "$LOG_FILE"
    exit 1
fi

# 4. Exécution du pipeline
# On se place dans 'newprjt' pour que les imports python fonctionnent
cd "$ROOT_DIR/back"
python -m scripts.main_pipeline >> "$LOG_FILE" 2>&1

echo "---  Fin : $(date) ---" >> "$LOG_FILE"
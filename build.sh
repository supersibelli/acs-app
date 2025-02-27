#!/usr/bin/env bash
# exit on error
set -o errexit

# Crear directorio instance si no existe
mkdir -p instance

# Recrear la base de datos
python recrear_db.py

# Generar datos de ejemplo si es necesario
python generar_acs.py 
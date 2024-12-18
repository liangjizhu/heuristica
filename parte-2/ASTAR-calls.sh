#!/bin/bash

# Ruta absoluta del script Python
SCRIPT="./ASTARRodaje.py"

# Ruta absoluta del directorio donde están los mapas
MAP_DIR="./ASTAR-tests"

# Heurísticas a usar
HEURISTICAS=(1 2)

# Verificar que el directorio de mapas existe
if [ ! -d "$MAP_DIR" ]; then
    echo "Error: El directorio $MAP_DIR no existe."
    exit 1
fi

# Buscar todos los archivos que coincidan con el patrón mapa*.csv
MAPAS=$(find "$MAP_DIR" -type f -name "mapa*.csv" | sort)

# Verificar si hay mapas disponibles
if [ -z "$MAPAS" ]; then
    echo "Error: No se encontraron archivos que coincidan con el patrón mapa*.csv en $MAP_DIR."
    exit 1
fi

# Ejecutar el script para cada mapa y heurística
for MAPA in $MAPAS; do
    for HEURISTICA in "${HEURISTICAS[@]}"; do
        echo "Ejecutando $SCRIPT $MAPA $HEURISTICA"
        python3 "$SCRIPT" "$MAPA" $HEURISTICA
    done
done

echo "Ejecución completa."

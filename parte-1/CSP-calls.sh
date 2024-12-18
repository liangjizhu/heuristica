#!/bin/bash

# Ruta absoluta del script Python
SCRIPT="./CSPMaintenance.py"

# Ruta absoluta del directorio donde están los casos de prueba
TEST_DIR="./CSP-tests"

# Verificar que el directorio de pruebas existe
if [ ! -d "$TEST_DIR" ]; then
    echo "Error: El directorio $TEST_DIR no existe."
    exit 1
fi

# Buscar todos los archivos que coincidan con el patrón maintenance*.txt
TEST_FILES=$(find "$TEST_DIR" -type f -name "maintenance*.txt" | sort)

# Verificar si hay archivos de prueba disponibles
if [ -z "$TEST_FILES" ]; then
    echo "Error: No se encontraron archivos que coincidan con el patrón maintenance*.txt en $TEST_DIR."
    exit 1
fi

# Ejecutar el script para cada archivo de prueba
for TEST_FILE in $TEST_FILES; do
    echo "Ejecutando $SCRIPT con $TEST_FILE"
    python3 "$SCRIPT" "$TEST_FILE"
done

echo "Ejecución completa."

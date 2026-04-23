[# English](README.en.md) | [Español](README.md) | [中文](README.zh.md)

# heuristica

## Introducción

Este repositorio contiene scripts en Python para resolver problemas de **satisfacción de restricciones (CSP)** y problemas de **búsqueda de caminos**. Los scripts están organizados en distintos directorios según su funcionalidad y propósito.

## Estructura del repositorio

El repositorio se organiza de la siguiente forma:

- `enunciado/`: Contiene varios scripts de Python para distintos problemas.
  - `alumnos.py`: Script para resolver un CSP relacionado con estudiantes.
  - `n-queens.py`: Script para resolver el problema de las N reinas mediante procesamiento de restricciones.
  - `n-queens-fun.py`: Versión modificada de `n-queens.py` con un enfoque diferente.
  - `sum-words.py`: Script para resolver el acertijo “sum-words” mediante procesamiento de restricciones.
- `parte-1/`: Contiene scripts y ficheros de prueba para la primera parte del proyecto.
  - `CSP-calls.sh`: Script de shell para ejecutar pruebas relacionadas con CSP.
  - `CSP-tests/`: Directorio con ficheros de prueba para CSP.
  - `CSPMaintenance.py`: Script en Python para resolver problemas de planificación de mantenimiento mediante restricciones.
- `parte-2/`: Contiene scripts y ficheros de prueba para la segunda parte del proyecto.
  - `ASTAR-calls.sh`: Script de shell para ejecutar pruebas relacionadas con búsqueda de caminos.
  - `ASTAR-tests/`: Directorio con ficheros de prueba para A*.
  - `ASTARRodaje.py`: Script en Python para resolver problemas de búsqueda de caminos usando el algoritmo A*.
- `.gitignore`: Especifica archivos y directorios que Git debe ignorar.
- `requirements.txt`: Lista de dependencias del proyecto.

## Instalación

Para preparar el entorno e instalar las dependencias:

1. Clona el repositorio:

   ```bash
   git clone https://github.com/liangjizhu/heuristica.git
   cd heuristica
   ```

2. Crea un entorno virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Ejecutar scripts de satisfacción de restricciones (CSP)

Para ejecutar los scripts de CSP:

- `alumnos.py`:

  ```bash
  python enunciado/alumnos.py
  ```

- `n-queens.py`:

  ```bash
  python enunciado/n-queens.py
  ```

- `n-queens-fun.py`:

  ```bash
  python enunciado/n-queens-fun.py
  ```

- `sum-words.py`:

  ```bash
  python enunciado/sum-words.py
  ```

### Ejecutar el script de planificación de mantenimiento

Para ejecutar el script de mantenimiento:

```bash
python parte-1/CSPMaintenance.py <ruta_fichero_entrada>
```

### Ejecutar el script de búsqueda de caminos

Para ejecutar el script de búsqueda de caminos:

```bash
python parte-2/ASTARRodaje.py <path mapa.csv> <num-h>
```

### Ejecutar las pruebas

Para ejecutar las pruebas:

- Pruebas de CSP:

  ```bash
  bash parte-1/CSP-calls.sh
  ```

- Pruebas de A*:

  ```bash
  bash parte-2/ASTAR-calls.sh
  ```


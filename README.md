# heuristica

## Introduction

This repository contains Python scripts for solving constraint satisfaction problems and pathfinding problems. The scripts are organized into different directories based on their functionality and purpose.

## Repository Structure

The repository is structured as follows:

- `enunciado/`: Contains various Python scripts for different problems.
  - `alumnos.py`: Script for solving a constraint satisfaction problem involving students.
  - `n-queens.py`: Script for solving the N-queens problem using constraint processing.
  - `n-queens-fun.py`: Modified version of `n-queens.py` with a different approach.
  - `sum-words.py`: Script for solving a sum-words brain teaser using constraint processing.
- `parte-1/`: Contains scripts and test files for the first part of the project.
  - `CSP-calls.sh`: Shell script for running tests related to constraint satisfaction problems.
  - `CSP-tests/`: Directory containing test files for constraint satisfaction problems.
  - `CSPMaintenance.py`: Python script for solving maintenance scheduling problems using constraint processing.
- `parte-2/`: Contains scripts and test files for the second part of the project.
  - `ASTAR-calls.sh`: Shell script for running tests related to pathfinding problems.
  - `ASTAR-tests/`: Directory containing test files for pathfinding problems.
  - `ASTARRodaje.py`: Python script for solving pathfinding problems using the A* algorithm.
- `.gitignore`: Specifies files and directories to be ignored by Git.
- `requirements.txt`: Lists the dependencies required for the project.

## Installation

To set up the environment and install the dependencies, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/liangjizhu/heuristica.git
   cd heuristica
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Constraint Satisfaction Problem Scripts

To run the constraint satisfaction problem scripts, use the following commands:

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

### Running Maintenance Scheduling Problem Script

To run the maintenance scheduling problem script, use the following command:
```bash
python parte-1/CSPMaintenance.py <ruta_fichero_entrada>
```

### Running Pathfinding Problem Script

To run the pathfinding problem script, use the following command:
```bash
python parte-2/ASTARRodaje.py <path mapa.csv> <num-h>
```

### Running Tests

To run the tests, use the following commands:

- Constraint Satisfaction Problem Tests:
  ```bash
  bash parte-1/CSP-calls.sh
  ```

- Pathfinding Problem Tests:
  ```bash
  bash parte-2/ASTAR-calls.sh
  ```


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import heapq
from collections import deque

#######################################################################
# Lectura de argumentos
#######################################################################

if len(sys.argv) < 3:
    print("Uso: python ASTARRodaje.py <path mapa.csv> <num-h>")
    sys.exit(1)

map_path = sys.argv[1]
num_heuristica = int(sys.argv[2])

#######################################################################
# Lectura del mapa y datos
#######################################################################

# Estructuras para el mapa
# B: Blanca (transitable y se puede esperar)
# A: Amarilla (transitable, no se puede esperar)
# G: Gris (no transitable)
with open(map_path, 'r') as file:
    lines = [line.strip() for line in file.readlines()]

num_aviones = int(lines[0])
aviones_data = lines[1:num_aviones+1]
map_data = lines[num_aviones+1:]

# Destinos:
iniciales = []
finales = []

for i, line in enumerate(aviones_data):
    # Ejemplo: "(3,3) (0,2)"
    parts = line.replace('(', '').replace(')', '').split()
    # parts = ["3,3", "0,2"]
    init = tuple(map(int, parts[0].split(',')))
    goal = tuple(map(int, parts[1].split(',')))
    iniciales.append(init)
    finales.append(goal)

mapa = []
for row in map_data:
    # Cada fila podría tener formato: "B;B;B;B"
    mapa.append(row.split(';'))

rows = len(mapa)
cols = len(mapa[0])

#######################################################################
# Funciones auxiliares
#######################################################################

def es_transitable(celda):
    return celda in ['B','A']

def puede_esperar(celda):
    # Se puede esperar en B (blanca), no en A (amarilla)
    return celda == 'B'

def vecinos(row, col):
    # Movimientos: arriba, abajo, izquierda, derecha
    direcciones = [(-1,0), (1,0), (0,-1), (0,1)]
    for dr, dc in direcciones:
        vecino_row, vecino_col = row+dr, col+dc
        if 0 <= vecino_row < rows and 0 <= vecino_col < cols and es_transitable(mapa[vecino_row][vecino_col]):
            yield vecino_row, vecino_col

#######################################################################
# Heurísticas
#######################################################################

# Heurística 1: max distancia Manhattan
def heuristica_1(estado):
    # estado: tuple de posiciones [(row1, col1), (row2, col2), ...]
    distancia = 0
    for (row, col), (row_goal, col_goal) in zip(estado, finales):
        dist_manhattan = abs(row - row_goal) + abs(col - col_goal)
        if dist_manhattan > distancia:
            distancia = dist_manhattan
    return distancia

# Heurística 2: Distancia real más corta ignorando otros aviones.
# Precalcular la distancia mínima para cada avión a su meta
distancias_min = []
def precalcular_distancias():
    # Usaremos BFS para cada meta.
    # distancias_min[i][row][col] = distancia del (row,col) a la meta del avión i
    for i, goal in enumerate(finales):
        dist_map = [[float('inf')]*cols for _ in range(rows)]
        queue = deque()
        row_goal, col_goal = goal
        dist_map[row_goal][col_goal] = 0
        queue.append((row_goal, col_goal))
        while queue:
            row, col = queue.popleft()
            for vecino_row, vecino_col in vecinos(row,col):
                if dist_map[vecino_row][vecino_col] == float('inf'):
                    dist_map[vecino_row][vecino_col] = dist_map[row][col] + 1
                    queue.append((vecino_row,vecino_col))
        distancias_min.append(dist_map)

def heuristica_2(estado):
    # Se asume que distancias_min ya está computada.
    distancia = 0
    # distancia del (row, col) a la meta del avión i
    for i, (row, col) in enumerate(estado):
        dist_min = distancias_min[i][row][col]
        if dist_min == float('inf'):
            # Si es inalcanzable, heurística puede ser muy alta
            # Esto podría pasar si no hay camino, en cuyo caso no existe solución.
            return float('inf')
        if dist_min > distancia:
            distancia = dist_min
    return distancia

if num_heuristica == 2:
    precalcular_distancias()

#######################################################################
# Estado y búsqueda A*
#######################################################################

# Representaremos el estado como una tupla ((row1,col1), (row2,col2), ..., tiempo)
# Sin embargo, el tiempo no es necesario guardarlo explícitamente si g(n) lo 
# representamos con el coste acumulado. El estado para visited puede ignorar tiempo.
#
# visited: set de posiciones de aviones sin tiempo -> para evitar ciclos.

estado_inicial = tuple(iniciales)
goal_posiciones = tuple(finales)

def es_objetivo(estado):
    return estado == goal_posiciones

def acciones_avion(posicion):
    # posicion: (row,col)
    # Acciones: moverse a vecinos o esperar.
    # Esperar solo si puede esperar en esta celda
    row, col = posicion
    possible = []
    # Moverse a vecinos
    for vecino_row, vecino_col in vecinos(row,col):
        possible.append((vecino_row,vecino_col))
    # Esperar
    if puede_esperar(mapa[row][col]):
        possible.append((row,col))
    return possible

def generan_conflicto(estado_anterior, estado_nuevo):
    # Verifica colisiones:
    # 1. Dos aviones en la misma celda a la vez
    # 2. Intercambio de posiciones entre dos aviones
    # estado_anterior -> estado anterior
    # estado_nuevo -> estado generado
    # Ambos son tuplas de posiciones [(row1, col1), (row2, col2),...]
    n = len(estado_nuevo)
    # Mismo lugar
    if len(set(estado_nuevo)) < n:
        return True
    
    # Intercambio de posiciones
    # Si a1 estaba en celdax y a2 en celday, no puede que en el siguiente:
    # a1 esté en celday y a2 en celdax.
    for i in range(n):
        for j in range(i + 1, n):
            if estado_anterior[i] == estado_nuevo[j] and estado_anterior[j] == estado_nuevo[i]:
                return True
    return False

def obtener_sucesores(estado):
    # estado: ((row1, col1), (row2, col2),...)
    # Generar todas las combinaciones de acciones.
    aviones_posiciones = list(estado)
    acciones = [acciones_avion(posicion) for posicion in aviones_posiciones]

    # Generar el producto cartesiano de acciones
    # Para evitar explosión, se puede hacer de forma incremental
    from itertools import product
    for combinacion in product(*acciones):
        estado_nuevo = tuple(combinacion)
        # Chequear colisiones
        if not generan_conflicto(estado, estado_nuevo):
            yield estado_nuevo

def heuristica(estado):
    if num_heuristica == 2:
        return heuristica_2(estado)
    return heuristica_1(estado)

# Busqueda A*
def busqueda_a_estrella():
    start = estado_inicial
    heuristica_inicial = heuristica(start)
    
    # Estructura de A*: cola de prioridad
    # Cada elemento: (f, g, state, parent)
    # parent = (padre, acciones que llevaron a este estado)
    # Aquí guardaremos solo padre y la acción tomada por cada avión
    open_list = []
    heapq.heappush(open_list, (heuristica_inicial, 0, start, None))
    visited = set()
    visited.add(start)

    parents = {start: None}

    nodos_expandidos = 0
    start_time = time.time()

    while open_list:
        f, g, current, _ = heapq.heappop(open_list)
        nodos_expandidos += 1

        if es_objetivo(current):
            end_time = time.time()
            # Reconstruir solución
            plan = reconstruir_solucion(current, parents)
            return plan, g, heuristica_inicial, nodos_expandidos, (end_time - start_time)

        for succ in obtener_sucesores(current):
            if succ not in visited:
                visited.add(succ)
                gn = g + 1
                fn = gn + heuristica(succ)
                parents[succ] = current
                heapq.heappush(open_list, (fn, gn, succ, None))

    return None, None, None, None, None  # Sin solución

def reconstruir_solucion(goal_state, parents):
    # Reconstruye la secuencia de estados desde el estado objetivo hasta el inicial.
    path = []
    cur = goal_state
    while cur is not None:
        path.append(cur)
        cur = parents[cur]
    path.reverse()

    # path es una lista de estados: [(r1,c1),(r2,c2),...], ...]
    # Queremos acciones por avión.
    # Las acciones para cada avión es la transición entre estados consecutivos.
    # Debemos inferir movimiento: (x,y) -> (x,y), (x,y+1), etc.
    # Notar que un estado no guarda directamente la acción, hay que deducirla.
    # Si (r,c) no cambia, es espera (w).
    
    # path: [initial_state, ..., goal_state]
    # Vamos a crear un plan por cada avión.
    n = len(iniciales)
    aviones_trayectoria = [[] for _ in range(n)]
    for state in path:
        for i,(r,c) in enumerate(state):
            aviones_trayectoria[i].append((r,c))
    return aviones_trayectoria

#######################################################################
# Ejecución de la búsqueda
#######################################################################

plan, makespan, h_inicial, nodos_expandidos, tiempo_total = busqueda_a_estrella()

if plan is None:
    print("No se ha encontrado solución")
    sys.exit(0)

# plan es una lista de listas: plan[i] = [(r,c), (r,c), ...] para el avión i

#######################################################################
# Formato de salida
#######################################################################
# Generar fichero de salida
import os
map_name = os.path.basename(map_path).split('.')[0]

output_file = f"{map_name}-{num_heuristica}.output"
stat_file = f"{map_name}-{num_heuristica}.stat"

# Escribimos la solución
with open(output_file, 'w') as f_out:
    for avion_plan in plan:
        # Ejemplo de formateo:
        # (3,3) → (3,2) → (3,1) ↑ ...
        # Aquí simplemente imprimimos las posiciones, incluyendo si hay esperas:
        line = ""
        for idx, pos in enumerate(avion_plan):
            if idx > 0:
                # Determinar movimiento:
                prev = avion_plan[idx-1]
                dx = pos[0] - prev[0]
                dy = pos[1] - prev[1]
                if dx == 0 and dy == 0:
                    # Espera
                    line += " w"
                elif dx == -1:
                    line += " ↑"
                elif dx == 1:
                    line += " ↓"
                elif dy == -1:
                    line += " ←"
                elif dy == 1:
                    line += " →"
            # Siempre escribir la posición actual
            line += f" ({pos[0]},{pos[1]})"
        f_out.write(line.strip() + "\n")

with open(stat_file, 'w') as f_stat:
    f_stat.write(f"Tiempo total: {int(tiempo_total)}s\n")
    f_stat.write(f"Makespan: {makespan}\n")
    f_stat.write(f"h inicial: {h_inicial}\n")
    f_stat.write(f"Nodos expandidos: {nodos_expandidos}\n")

print("Solución y estadísticas generadas.")

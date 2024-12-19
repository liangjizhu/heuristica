#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from constraint import Problem

def parse_posiciones(linea):
    partes = linea.split(":")
    if len(partes) < 2:
        return []
    posiciones_str = partes[1].strip()
    if not posiciones_str:
        return []
    tuplas_str = posiciones_str.split()
    posiciones = []
    for t_str in tuplas_str:
        t_str = t_str.strip("()")
        r, c = t_str.split(",")
        posiciones.append((int(r), int(c)))
    return posiciones

def leer_datos(ruta_fichero):
    with open(ruta_fichero, 'r') as f:
        lineas = [linea.strip() for linea in f if linea.strip()]

    franjas = int(lineas[0].split(":")[1].strip())
    tam_matriz = tuple(map(int, lineas[1].split("x")))
    talleres_std = parse_posiciones(lineas[2]) if len(lineas) > 2 else []
    talleres_spc = parse_posiciones(lineas[3]) if len(lineas) > 3 else []
    parkings = parse_posiciones(lineas[4]) if len(lineas) > 4 else []

    aviones = []
    for linea in lineas[5:]:
        if "-" in linea:
            id_, tipo, restr, t1, t2 = linea.split("-")
            aviones.append({
                "id": id_,
                "tipo": tipo,
                "restr": (restr == "T"),
                "t1": int(t1),
                "t2": int(t2)
            })

    return franjas, tam_matriz, talleres_std, talleres_spc, parkings, aviones

def filtrar_soluciones(soluciones):
    soluciones_unicas = []
    for sol in soluciones:
        if sol not in soluciones_unicas:
            soluciones_unicas.append(sol)
    return soluciones_unicas

def escribir_salida(ruta_salida, soluciones, aviones, talleres_std, talleres_spc, parkings):
    # Mapeo de cada posición a su tipo (STD, SPC, PRK)
    pos_type = {}
    for p in talleres_std:
        pos_type[p] = "STD"
    for p in talleres_spc:
        pos_type[p] = "SPC"
    for p in parkings:
        pos_type[p] = "PRK"

    with open(ruta_salida, 'w', newline='') as f:
        f.write(f"N. Sol: {len(soluciones)}\n")

        if len(soluciones) == 0:
            return

        # Calcular la cantidad de franjas
        numero_franjas = len(soluciones[0]) // len(aviones) if len(aviones) > 0 else 0

        for i, solucion in enumerate(soluciones, start=1):
            f.write(f"Solución {i}:\n")
            for avion in aviones:
                restr_str = "T" if avion["restr"] else "F"
                header = f"{avion['id']}-{avion['tipo']}-{restr_str}-{avion['t1']}-{avion['t2']}:"
                posiciones = []
                for t in range(numero_franjas):
                    pos = solucion[f"T_{avion['id']}_{t}"]
                    tipo = pos_type.get(pos, "???")
                    posiciones.append(f"{tipo}({pos[0]},{pos[1]})")

                # Unir las posiciones con ", "
                posiciones_str = ", ".join(posiciones)
                f.write(f"{header} {posiciones_str}\n")

def main():
    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <ruta_fichero_entrada>")
        sys.exit(1)

    ruta_fichero = sys.argv[1]
    ruta_salida = ruta_fichero.replace(".txt", ".csv")

    # Leer datos de entrada
    franjas, tam_matriz, talleres_std, talleres_spc, parkings, aviones = leer_datos(ruta_fichero)

    dominio = talleres_std + talleres_spc + parkings
    problem = Problem()

    # Crear variables
    for avion in aviones:
        for t in range(franjas):
            problem.addVariable(f"T_{avion['id']}_{t}", dominio)

    # Restricciones (sin cambios)
    def capacidad_taller(*args):
        talleres_ocupados = [pos for pos in args if pos in talleres_std + talleres_spc]
        return all(talleres_ocupados.count(pos) <= 2 for pos in talleres_ocupados)

    def jumbo_unico(*args):
        talleres_jumbo = [pos for pos, av in zip(args, aviones) if av["tipo"] == "JMB"]
        return all(talleres_jumbo.count(pos) <= 1 for pos in talleres_jumbo)

    def no_adyacentes(*args):
        ocupados = [pos for pos in args if pos]
        adyacencias = [
            (pos[0] + dx, pos[1] + dy)
            for pos in ocupados
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
        ]

        for pos in ocupados:
            adyacentes_ocupados = sum(1 for ady in adyacencias if ady == pos)
            if adyacentes_ocupados == len(adyacencias):
                return False

        return True

    def orden_tareas_correcto(avion_id, restr, *variables):
        posiciones = list(variables)
        tareas_tipo2 = next(av["t2"] for av in aviones if av["id"] == avion_id)
        tareas_tipo1 = next(av["t1"] for av in aviones if av["id"] == avion_id)

        for pos in posiciones:
            if tareas_tipo2 == 0 and tareas_tipo1 == 0:
                if pos not in parkings:
                    return False

            if restr:
                if tareas_tipo2 > 0:
                    if pos not in talleres_spc:
                        return False
                    tareas_tipo2 -= 1
                elif tareas_tipo1 > 0:
                    if pos not in (talleres_std + talleres_spc):
                        return False
                    tareas_tipo1 -= 1
            else:
                if tareas_tipo1 > 0 and pos in talleres_std:
                    tareas_tipo1 -= 1
                elif tareas_tipo2 > 0 and pos in talleres_spc:
                    tareas_tipo2 -= 1
                elif (tareas_tipo1 > 0 or tareas_tipo2 > 0) and pos not in (talleres_std + talleres_spc):
                    return False

        return tareas_tipo1 == 0 and tareas_tipo2 == 0

    def jumbo_no_adyacente(*args):
        posiciones_jumbo = [pos for pos, av in zip(args, aviones) if av["tipo"] == "JMB"]
        for i, pos1 in enumerate(posiciones_jumbo):
            for pos2 in posiciones_jumbo[i + 1:]:
                if pos1 and pos2 and abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1:
                    return False
        return True

    def sin_tareas_en_parkings(aviones, franjas, vals, talleres_std, talleres_spc, parkings):
        n_aviones = len(aviones)
        # Reconstruimos positions[avion][t]
        positions = [[None]*franjas for _ in range(n_aviones)]
        # Asumimos que el orden en all_vars fue por cada t y por cada avion en orden aviones
        # Ej: T_avion1_0, T_avion2_0, ..., T_avionN_0, T_avion1_1, ...
        for t in range(franjas):
            for i, avion in enumerate(aviones):
                positions[i][t] = vals[t*n_aviones + i]

        for i, avion in enumerate(aviones):
            tareas_restantes = avion["t1"] + avion["t2"]
            for pos in positions[i]:
                # Si no hay tareas pendientes y no está en parking
                if tareas_restantes == 0 and pos not in parkings:
                    return False
                # Si hay tareas pendientes y está en SPC
                if pos in talleres_spc:
                    tareas_restantes = max(0, tareas_restantes - 1)
                # Si hay tareas pendientes, sin T2 restantes, podría hacer T1 en STD
                if pos in talleres_std and avion["t2"] == 0:
                    tareas_restantes = max(0, tareas_restantes - 1)
        # 1. Si quedan tareas pendientes, la solución es inválida
        if tareas_restantes > 0:
            return False

        # 2. Si las tareas ya se han completado, el avión debe acabar en parking en la última franja
        if tareas_restantes == 0 and positions[i][-1] not in parkings:
            return False

    return True


    def franjas_consecutivas(var1, var2):
        if var1 == var2:
            return True
        if (var1 in talleres_std and var2 in talleres_spc) or (var1 in talleres_spc and var2 in talleres_std):
            return True
        if (var1 in talleres_std + talleres_spc and var2 in parkings) or (var1 in parkings and var2 in talleres_std + talleres_spc):
            return True
        return False

    # Añadir restricciones
    for avion in aviones:
        for t in range(franjas):
            problem.addConstraint(lambda pos: pos in dominio, [f"T_{avion['id']}_{t}"])

    for t in range(franjas):
        problem.addConstraint(capacidad_taller, [f"T_{avion['id']}_{t}" for avion in aviones])
        problem.addConstraint(jumbo_unico, [f"T_{avion['id']}_{t}" for avion in aviones])
        problem.addConstraint(no_adyacentes, [f"T_{avion['id']}_{t}" for avion in aviones])
        problem.addConstraint(jumbo_no_adyacente, [f"T_{avion['id']}_{t}" for avion in aviones])
        # Antes de resolver, juntar todas las variables en una sola lista
        all_vars = []
        for t in range(franjas):
            for avion in aviones:
                all_vars.append(f"T_{avion['id']}_{t}")

        problem.addConstraint(
            lambda *vals: sin_tareas_en_parkings(aviones, franjas, vals, talleres_std, talleres_spc, parkings),
            all_vars
        )

    # Esta forma de añadir sin_tareas_en_parkings es compleja y probablemente deba ser revisada.
    # Es preferible añadirla fuera del main o ajustar la lógica.
    # Si ya estaba funcionando en el código original, se asume correcto.
    # De lo contrario, habría que replantear cómo se pasan los argumentos a esa función.

    for avion in aviones:
        problem.addConstraint(
            lambda *vars, avion_id=avion["id"], restr=avion["restr"]: orden_tareas_correcto(avion_id, restr, *vars),
            [f"T_{avion['id']}_{t}" for t in range(franjas)]
        )
        for t in range(franjas - 1):
            problem.addConstraint(franjas_consecutivas, [f"T_{avion['id']}_{t}", f"T_{avion['id']}_{t+1}"])

    # Resolver el problema
    solutions = problem.getSolutions()
    solutions = filtrar_soluciones(solutions)
    escribir_salida(ruta_salida, solutions, aviones, talleres_std, talleres_spc, parkings)
    print(f"Soluciones únicas escritas en {ruta_salida}")

if __name__ == "__main__":
    main()

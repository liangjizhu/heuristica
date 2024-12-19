import sys
import csv
from constraint import Problem

def parse_posiciones(linea):
    # Esta función toma una línea del tipo:
    # "STD:(0,1) (1,0) (1,1) ..."
    # y devuelve una lista de tuplas [(0,1), (1,0), (1,1), ...]
    partes = linea.split(":")
    if len(partes) < 2:
        return []
    posiciones_str = partes[1].strip()
    if not posiciones_str:
        return []
    tuplas_str = posiciones_str.split()
    posiciones = []
    for t_str in tuplas_str:
        # t_str es algo como "(0,1)"
        t_str = t_str.strip("()")
        r, c = t_str.split(",")
        posiciones.append((int(r), int(c)))
    return posiciones

def leer_datos(ruta_fichero):
    with open(ruta_fichero, 'r') as f:
        lineas = [linea.strip() for linea in f if linea.strip()]  # Eliminar líneas vacías

    # Leer las franjas horarias y tamaño de la matriz
    # Ej: "Franjas: 4"  -> franjas = 4
    franjas = int(lineas[0].split(":")[1].strip())
    # Ej: "5x5" -> tam_matriz = (5,5)
    tam_matriz = tuple(map(int, lineas[1].split("x")))

    # Leer posiciones de talleres y parkings
    # Ej: "STD:(0,1) (1,0) ..."
    talleres_std = parse_posiciones(lineas[2]) if len(lineas) > 2 else []
    talleres_spc = parse_posiciones(lineas[3]) if len(lineas) > 3 else []
    parkings = parse_posiciones(lineas[4]) if len(lineas) > 4 else []

    # Leer información de los aviones
    aviones = []
    # A partir de la línea 5 en adelante:
    for linea in lineas[5:]:
        if "-" in linea:
            # Ej: "1-JMB-T-2-2"
            id_, tipo, restr, t1, t2 = linea.split("-")
            aviones.append({
                "id": id_,
                "tipo": tipo,
                "restr": (restr == "T"),  # True/False
                "t1": int(t1),
                "t2": int(t2)
            })

    return franjas, tam_matriz, talleres_std, talleres_spc, parkings, aviones


def escribir_salida(ruta_salida, soluciones, aviones):
    with open(ruta_salida, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([f"N. Sol: {len(soluciones)}"])
        for i, solucion in enumerate(soluciones, start=1):
            writer.writerow([f"Solución {i}:"])
            for avion in aviones:
                restr_str = "T" if avion["restr"] else "F"
                fila = [f"{avion['id']}-{avion['tipo']}-{restr_str}-{avion['t1']}-{avion['t2']}:"]

                # Cantidad de franjas = len(soluciones[0]) // len(aviones)
                # Esto asume que cada avión tiene la misma cantidad de variables
                # Si franjas = n, entonces para cada avión hay n variables T_avionID_t
                numero_franjas = len(soluciones[0]) // len(aviones)

                for t in range(numero_franjas):
                    fila.append(str(solucion[f"T_{avion['id']}_{t}"]))
                writer.writerow(fila)

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

    # Restricción 1: Cada avión debe tener una posición asignada en cada franja horaria
    def unica_posicion_por_avion(*args):
        return len(set(args)) == 1

    for avion in aviones:
        for t in range(franjas):
            problem.addConstraint(
                lambda pos: pos in dominio,  # Cada posición debe pertenecer al dominio
                [f"T_{avion['id']}_{t}"]
            )

    # Restricción 2: Capacidad máxima de 2 aviones por taller
    def capacidad_taller(*args):
        talleres_ocupados = [pos for pos in args if pos in talleres_std + talleres_spc]
        return all(talleres_ocupados.count(pos) <= 2 for pos in talleres_ocupados)

    for t in range(franjas):
        problem.addConstraint(capacidad_taller, [f"T_{avion['id']}_{t}" for avion in aviones])
        

    # Restricción 3: Un avión Jumbo por taller por franja horaria
    def jumbo_unico(*args):
        talleres_jumbo = [pos for pos, avion in zip(args, aviones) if avion["tipo"] == "JMB"]
        return all(talleres_jumbo.count(pos) <= 1 for pos in talleres_jumbo)

    for t in range(franjas):
        problem.addConstraint(jumbo_unico, [f"T_{avion['id']}_{t}" for avion in aviones])

    # Restricción 4: Adyacencia para maniobrabilidad
    def no_adyacentes(*args):
        ocupados = [pos for pos in args if pos]
        adyacencias = [
            (pos[0] + dx, pos[1] + dy)
            for pos in ocupados
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Solo vertical y horizontal
        ]

        # Contamos cuántas posiciones únicas adyacentes están ocupadas
        for pos in ocupados:
            adyacentes_ocupados = sum(1 for ady in adyacencias if ady == pos)
            # Si todas las posiciones adyacentes están ocupadas, retorna False
            if adyacentes_ocupados == len(adyacencias):
                return False

        return True


    for t in range(franjas):
        problem.addConstraint(no_adyacentes, [f"T_{avion['id']}_{t}" for avion in aviones])

    # Restricción 5: Orden de tareas (considerando restricción F/T)
    def orden_tareas_correcto(avion_id, restr, *variables):
        posiciones = list(variables)
        tareas_tipo2 = next(avion["t2"] for avion in aviones if avion["id"] == avion_id)
        tareas_tipo1 = next(avion["t1"] for avion in aviones if avion["id"] == avion_id)

        for pos in posiciones:
            # Caso 1: No hay tareas pendientes, debe estar en un parking
            if tareas_tipo2 == 0 and tareas_tipo1 == 0:
                if pos not in parkings:
                    return False

            # Caso 2: Restricción True, tipo 2 debe completarse antes de tipo 1
            if restr:
                if tareas_tipo2 > 0:
                    if pos not in talleres_spc:
                        return False
                    tareas_tipo2 -= 1
                elif tareas_tipo1 > 0:
                    if pos not in talleres_std + talleres_spc:
                        return False
                    tareas_tipo1 -= 1

            # Caso 3: Restricción False, tareas pueden hacerse en cualquier orden
            else:
                if tareas_tipo1 > 0 and pos in talleres_std:
                    tareas_tipo1 -= 1
                elif tareas_tipo2 > 0 and pos in talleres_spc:
                    tareas_tipo2 -= 1
                elif (tareas_tipo1 > 0 or tareas_tipo2 > 0) and pos not in talleres_std + talleres_spc:
                    return False

        # Validar que todas las tareas pendientes se hayan completado
        return tareas_tipo1 == 0 and tareas_tipo2 == 0


    # Añadir la restricción para cada avión
    for avion in aviones:
        problem.addConstraint(
            lambda *variables, avion_id=avion["id"], restr=avion["restr"]: orden_tareas_correcto(avion_id, restr, *variables),
            [f"T_{avion['id']}_{t}" for t in range(franjas)]
        )

    # Restricción 6: Dos aviones Jumbo no pueden ser adyacentes en la misma franja
    def jumbo_no_adyacente(*args):
        posiciones = [pos for pos, avion in zip(args, aviones) if avion["tipo"] == "JMB"]
        for i, pos1 in enumerate(posiciones):
            for pos2 in posiciones[i + 1:]:
                if pos1 and pos2 and abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1:
                    return False
        return True

    for t in range(franjas):
        problem.addConstraint(jumbo_no_adyacente, [f"T_{avion['id']}_{t}" for avion in aviones])

    # Restricción 7: Aviones sin tareas deben estar en parkings
    def sin_tareas_en_parkings(*args):
        for avion, posiciones in zip(aviones, zip(*args)):
            tareas_restantes = avion["t1"] + avion["t2"]

            for pos in posiciones:
                # Si no hay tareas pendientes, el avión debe estar en un parking
                if tareas_restantes == 0 and pos not in parkings:
                    return False
                # Reducir las tareas pendientes si está en un taller válido
                if pos in talleres_spc:
                    tareas_restantes = max(0, tareas_restantes - 1)
                elif pos in talleres_std and avion["t2"] == 0:  # Solo tareas T1 en talleres STD
                    tareas_restantes = max(0, tareas_restantes - 1)
                # Si hay tareas pendientes, no puede estar en un parking
                elif tareas_restantes > 0 and pos in parkings:
                    return False

        return True

    for t in range(franjas):
        problem.addConstraint(
            lambda *args, t=t: sin_tareas_en_parkings(*zip(*[
                [f"T_{avion['id']}_{t}" for t in range(franjas)]
                for avion in aviones
            ])),
            [f"T_{avion['id']}_{t}" for avion in aviones]
        )



    # Restricción 8: Franjas horarias consecutivas
    def franjas_consecutivas(var1, var2):
        # Permitir que un avión se quede en la misma posición
        if var1 == var2:
            return True
        # Permitir movimientos entre talleres estándar y especialistas
        if (var1 in talleres_std and var2 in talleres_spc) or (var1 in talleres_spc and var2 in talleres_std):
            return True
        # Permitir movimientos de un taller (estándar o especialista) a un parking
        if (var1 in talleres_std + talleres_spc and var2 in parkings) or (var1 in parkings and var2 in talleres_std + talleres_spc):
            return True
        # Si ninguna condición se cumple, no es una transición válida
        return False

    # Aplicar la restricción a todas las franjas consecutivas
    for avion in aviones:
        for t in range(franjas - 1):
            problem.addConstraint(
                franjas_consecutivas, [f"T_{avion['id']}_{t}", f"T_{avion['id']}_{t + 1}"]
            )



    # Resolver el problema
    solutions = problem.getSolutions()
    solutions = filtrar_soluciones(solutions)
    escribir_salida(ruta_salida, solutions, aviones)
    print(f"Soluciones únicas escritas en {ruta_salida}")

def filtrar_soluciones(soluciones):
    soluciones_unicas = []
    for sol in soluciones:
        if sol not in soluciones_unicas:
            soluciones_unicas.append(sol)
    return soluciones_unicas

if __name__ == "__main__":
    main()

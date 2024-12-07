import ast
import sys
import csv
from constraint import Problem


def leer_datos(ruta_fichero):
    with open(ruta_fichero, 'r') as f:
        lineas = [linea.strip() for linea in f if linea.strip()]  # Eliminar líneas vacías

    # Leer las franjas horarias y tamaño de la matriz
    franjas = int(lineas[0].split(":")[1].strip())
    tam_matriz = tuple(map(int, lineas[1].split("x")))

    # Leer posiciones de talleres y parkings
    talleres_std = ast.literal_eval(lineas[2].split(":")[1].strip())
    talleres_spc = ast.literal_eval(lineas[3].split(":")[1].strip())
    parkings = ast.literal_eval(lineas[4].split(":")[1].strip())

    # Leer información de los aviones
    aviones = []
    for linea in lineas[5:]:
        if "-" in linea:  # Verificar que la línea tenga el formato correcto
            id_, tipo, restr, t1, t2 = linea.split("-")
            aviones.append({
                "id": id_,
                "tipo": tipo,
                "restr": restr == "T",
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
                fila = [f"{avion['id']}-{avion['tipo']}-T-{avion['t1']}-{avion['t2']}:"]
                for t in range(len(soluciones[0]) // len(aviones)):
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

    # Restricción 1: Todo avión tiene una posición única en cada franja horaria
    def unica_posicion(*args):
        return len(args) == len(set(args))

    for t in range(franjas):
        problem.addConstraint(unica_posicion, [f"T_{avion['id']}_{t}" for avion in aviones])

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
        for i, pos1 in enumerate(args):
            for j, pos2 in enumerate(args):
                if i != j and pos1 and pos2:
                    if abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1:
                        return False
        return True

    for t in range(franjas):
        problem.addConstraint(no_adyacentes, [f"T_{avion['id']}_{t}" for avion in aviones])

    # Restricción 5: Orden de tareas (tipo 2 antes de tipo 1 si restricción es True)
    def orden_tareas(*variables):
        posiciones = list(variables)
        for i in range(len(posiciones) - 1):
            if posiciones[i] in talleres_std and posiciones[i + 1] in talleres_spc:
                return False
        return True

    for avion in aviones:
        if avion["restr"]:
            problem.addConstraint(
                orden_tareas, [f"T_{avion['id']}_{t}" for t in range(franjas)]
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
    def sin_tareas_es_parking(*args):
        return all(pos in parkings for pos in args)

    for t in range(franjas):
        problem.addConstraint(sin_tareas_es_parking, [f"T_{avion['id']}_{t}" for avion in aviones])

    # Restricción 8: Franjas horarias consecutivas
    def franjas_consecutivas(var1, var2):
        return var1 == var2 or var2 in parkings

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

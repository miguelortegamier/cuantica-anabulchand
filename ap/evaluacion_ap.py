def decodificar_matriz(sample, m, n):
    matriz = [[0 for _ in range(n)] for _ in range(m)]

    for i in range(m):
        for j in range(n):
            matriz[i][j] = int(round(sample[f"x_{i}_{j}"]))

    return matriz


def coste_total(matriz_asignacion, costes):
    total = 0

    for i in range(len(costes)):
        for j in range(len(costes[0])):
            total += costes[i][j] * matriz_asignacion[i][j]

    return total


def violacion_total(matriz_asignacion):
    m = len(matriz_asignacion)
    n = len(matriz_asignacion[0])
    violacion = 0

    for i in range(m):
        violacion += abs(sum(matriz_asignacion[i]) - 1)

    for j in range(n):
        violacion += abs(sum(matriz_asignacion[i][j] for i in range(m)) - 1)

    return violacion


def evaluar_resultado_qaoa(resultado, problema):
    m = len(problema.costes)
    n = len(problema.costes[0])

    sample = resultado.variables_dict
    matriz = decodificar_matriz(sample, m, n)
    coste = coste_total(matriz, problema.costes)
    violacion = violacion_total(matriz)

    return {
        "x": [matriz[i][j] for i in range(m) for j in range(n)],
        "matriz": matriz,
        "coste": coste,
        "violacion": violacion,
        "factible": violacion == 0,
    }


def evaluar_resultado_sa(sample, problema):
    m = len(problema.costes)
    n = len(problema.costes[0])

    matriz = decodificar_matriz(sample, m, n)
    coste = coste_total(matriz, problema.costes)
    violacion = violacion_total(matriz)

    return {
        "x": [matriz[i][j] for i in range(m) for j in range(n)],
        "matriz": matriz,
        "coste": coste,
        "violacion": violacion,
        "factible": violacion == 0,
    }

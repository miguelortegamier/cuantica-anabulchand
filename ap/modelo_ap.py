from dataclasses import dataclass
from qiskit_optimization import QuadraticProgram

@dataclass
class AP:
    costes: list[list[float]]


def nombre_variable(i, j):
    return f"x_{i}_{j}"


def construir_qubo(problema, penalizacion=None):
    m = len(problema.costes)
    n = len(problema.costes[0])

    if any(len(fila) != n for fila in problema.costes):
        raise ValueError("La matriz de costes debe ser rectangular.")

    if m != n:
        raise ValueError("Esta version sencilla requiere m = n.")

    if penalizacion is None:
        max_coste = max(max(fila) for fila in problema.costes)
        penalizacion = m * max_coste + 1

    qp = QuadraticProgram()

    for i in range(m):
        for j in range(n):
            qp.binary_var(name=nombre_variable(i, j))

    lineal = {}
    cuadratico = {}
    constante = penalizacion * (m + n)

    for i in range(m):
        for j in range(n):
            var = nombre_variable(i, j)
            lineal[var] = lineal.get(var, 0) + problema.costes[i][j] - 2 * penalizacion

    for i in range(m):
        for j1 in range(n):
            for j2 in range(j1 + 1, n):
                var1 = nombre_variable(i, j1)
                var2 = nombre_variable(i, j2)
                cuadratico[(var1, var2)] = cuadratico.get((var1, var2), 0) + 2 * penalizacion

    for j in range(n):
        for i1 in range(m):
            for i2 in range(i1 + 1, m):
                var1 = nombre_variable(i1, j)
                var2 = nombre_variable(i2, j)
                cuadratico[(var1, var2)] = cuadratico.get((var1, var2), 0) + 2 * penalizacion

    qp.minimize(constant=constante, linear=lineal, quadratic=cuadratico)
    return qp, penalizacion


def construir_problema(caso):
    problema = AP(costes=caso["costes"])
    qp, penalizacion = construir_qubo(problema)
    return problema, qp, penalizacion

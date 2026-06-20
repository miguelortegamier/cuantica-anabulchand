from dataclasses import dataclass
import math
from qiskit_optimization import QuadraticProgram

@dataclass
class KP:
    valores: list[int]
    pesos: list[int]
    capacidad: int


def crear_variables(qp, n, Kmax):
    for i in range(n):
        qp.binary_var(name=f"x{i}")

    #Bits auxiliares para representar la holgura de la capacidad.
    for k in range(Kmax + 1):
        qp.binary_var(name=f"s{k}")


def func_objetivo(problema, Kmax):
    lineal, cuadratico = {}, {}

    p, n = sum(problema.valores), len(problema.valores)

    lineal = {f"x{i}": -problema.valores[i] for i in range(n)}

    #Objetivo: maximizar valor y penalizar desviarse de la capacidad.
    variables = (
        [(f"x{i}", problema.pesos[i]) for i in range(n)] +
        [(f"s{i}", 2**i) for i in range(Kmax + 1)]
    )

    for i in range(len(variables)):
        vari, coefi = variables[i]

        lineal[vari] = lineal.get(vari, 0) + p * (
            coefi**2 - 2 * problema.capacidad * coefi
        )

        for j in range(i + 1, len(variables)):
            varj, coefj = variables[j]
            cuadratico[(vari, varj)] = cuadratico.get((vari, varj), 0) + (
                2 * p * coefi * coefj
            )

    constante = p * problema.capacidad**2

    return lineal, cuadratico, constante


def prob_mochila(problema, Kmax):
    qp = QuadraticProgram()
    crear_variables(qp, len(problema.valores), Kmax)
    lineal, cuadratico, constante = func_objetivo(problema, Kmax)
    qp.minimize(constant=constante, linear=lineal, quadratic=cuadratico)
    return qp


def construir_problema(caso):
    problema = KP(
        valores=caso["valores"],
        pesos=caso["pesos"],
        capacidad=caso["capacidad"],
    )
    Kmax = int(math.floor(math.log2(problema.capacidad)))
    qp = prob_mochila(problema, Kmax)
    return problema, qp

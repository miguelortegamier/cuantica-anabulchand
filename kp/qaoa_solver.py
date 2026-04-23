import time
import math
import random
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import SPSA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from ruido import crear_sampler_con_ruido
from evaluacion import evaluar_resultado_qaoa

def actualizar_mejor(mejor_resultado, resultado, evaluado):
    if mejor_resultado is None:
        return (resultado, evaluado)

    _, mejor_eval = mejor_resultado

    if evaluado["factible"]:
        if not mejor_eval["factible"] or evaluado["valor"] > mejor_eval["valor"]:
            return (resultado, evaluado)
    else:
        if not mejor_eval["factible"] and evaluado["peso"] < mejor_eval["peso"]:
            return (resultado, evaluado)

    return mejor_resultado

def generar_registro(i, evaluado, punto_inicial, opt_val_total):
    return {
        "start": i,
        "valor": evaluado["valor"],
        "peso": evaluado["peso"],
        "factible": evaluado["factible"],
        "x": evaluado["x"],
        "punto_inicial": punto_inicial,
        "ratio_optimo": evaluado["valor"] / opt_val_total,
    }

def calcular_metricas(historial, opt_val_total, t_solver, sampler):
    factibles = [h for h in historial if h["factible"]]
    optimos = [h for h in historial if h["valor"] == opt_val_total and h["factible"]]

    prob_optimo = len(optimos) / len(historial)

    ratio_medio = (
        sum(h["ratio_optimo"] for h in factibles) / len(factibles)
        if factibles else 0
    )

    t_cuantico = sampler.tiempo_total
    t_clasico = t_solver - t_cuantico

    todos_tiempos = [
        t for h in historial for t in h.get("tiempos_iter", [])
    ]

    tiempo_medio_iter_global = (
        sum(todos_tiempos) / len(todos_tiempos)
        if todos_tiempos else 0
    )

    todos_evals = [
        h.get("num_evals", 0) for h in historial
    ]

    total_evals = sum(todos_evals)

    tiempo_por_eval = (
        t_solver / total_evals
        if total_evals > 0 else 0
    )

    return {
        "num_factibles": len(factibles),
        "prob_optimo": prob_optimo,
        "ratio_medio": ratio_medio,
        "t_solver": t_solver,
        "t_cuantico": t_cuantico,
        "t_clasico": t_clasico,
        "tiempo_medio_iter": tiempo_medio_iter_global,
        "tiempo_por_eval": tiempo_por_eval,
        "total_evals": total_evals,
    }

def ejecutar_qaoa_once(qp, sampler, repeticiones, maxiter, punto_inicial):
    t_callback = []

    def callback(eval_count, params, value, metadata):
        t_callback.append({
            "time": time.perf_counter(),
            "eval": eval_count,
            "value": value
        })

    qaoa = QAOA(
        sampler=sampler,
        optimizer=SPSA(maxiter=maxiter),
        reps=repeticiones,
        initial_point=punto_inicial,
        callback=callback,
    )

    solver = MinimumEigenOptimizer(qaoa)

    t0 = time.perf_counter()
    resultado = solver.solve(qp)
    t1 = time.perf_counter()

    return resultado, (t1 - t0), t_callback

def procesar_callback(t_callback):
    tiempos_iter = []
    valores = []
    evals = []

    for i in range(1, len(t_callback)):
        dt = t_callback[i]["time"] - t_callback[i - 1]["time"]
        tiempos_iter.append(dt)

    for item in t_callback:
        valores.append(item["value"])
        evals.append(item["eval"])

    return tiempos_iter, valores, evals

def ejecutar_multi_start(
    qp, problema, sampler, starts, repeticiones, maxiter, semilla, opt_val_total
):
    rng = random.Random(semilla)

    historial = []
    mejor_resultado = None
    t_solver = 0

    for i in range(starts):
        punto_inicial = [rng.uniform(0, math.pi) for _ in range(2 * repeticiones)]

        resultado, t_run, t_callback = ejecutar_qaoa_once(
            qp, sampler, repeticiones, maxiter, punto_inicial
        )

        tiempos_iter, valores_iter, evals_iter = procesar_callback(t_callback)

        t_solver += t_run

        evaluado = evaluar_resultado_qaoa(resultado, problema)

        registro = generar_registro(
            i, evaluado, punto_inicial, opt_val_total
        )

        registro.update({
            "tiempos_iter": tiempos_iter,
            "valores_iter": valores_iter,
            "evals_iter": evals_iter,
            "num_iters": len(tiempos_iter),
            "tiempo_medio_iter": (
                sum(tiempos_iter) / len(tiempos_iter)
                if tiempos_iter else 0
            ),
            "num_evals": evals_iter[-1] if evals_iter else 0
        })

        historial.append(registro)

        mejor_resultado = actualizar_mejor(
            mejor_resultado, resultado, evaluado
        )

    return mejor_resultado, historial, t_solver

def resolver_qaoa(
    qp,
    problema,
    opt_val_total,
    maxiter=100,
    repeticiones=3,
    starts=10,
    semilla=0,
    shots=1024,
):
    sampler = crear_sampler_con_ruido(shots, semilla, timed=True)

    mejor_resultado, historial, t_solver = ejecutar_multi_start(
        qp,
        problema,
        sampler,
        starts,
        repeticiones,
        maxiter,
        semilla,
        opt_val_total,
    )

    metricas = calcular_metricas(
        historial,
        opt_val_total,
        t_solver,
        sampler,
    )

    if mejor_resultado is None:
        raise RuntimeError("QAOA no devolvió solución.")

    return mejor_resultado[0], historial, metricas

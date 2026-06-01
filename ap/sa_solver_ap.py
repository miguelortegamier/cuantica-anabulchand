import statistics
import time

import dimod
from neal import SimulatedAnnealingSampler
from qiskit_optimization.converters import QuadraticProgramToQubo

from evaluacion_ap import evaluar_resultado_sa


def resolver_sa_multi_start(qp, problema, opt_coste, starts=10, num_reads=10, semilla=0):
    historial_starts = []
    total_muestras, muestras_opt, muestras_fact = 0, 0, 0
    mejor_eval = None
    ratios_factibles = []

    sampler = SimulatedAnnealingSampler()
    Q, _ = qp_qubo(qp)

    for i in range(starts):
        t0 = time.perf_counter()

        sampleset = sampler.sample_qubo(Q, num_reads=num_reads, seed=semilla + i)

        evaluaciones = [
            evaluar_resultado_sa(sample, problema)
            for sample in sampleset.samples()
        ]

        t1 = time.perf_counter()

        mejor_start = min(
            evaluaciones,
            key=lambda e: (
                0 if e["factible"] else 1,
                e["coste"] if e["factible"] else e["violacion"],
                e["coste"],
            ),
        )

        optimo_bool = any(
            e["factible"] and e["coste"] == opt_coste
            for e in evaluaciones
        )

        for e in evaluaciones:
            total_muestras += 1

            if e["factible"]:
                muestras_fact += 1
                ratios_factibles.append(
                    opt_coste / e["coste"] if e["coste"] > 0 else 0
                )

                if e["coste"] == opt_coste:
                    muestras_opt += 1

            if mejor_eval is None:
                mejor_eval = e
            elif e["factible"]:
                if (not mejor_eval["factible"]) or (e["coste"] < mejor_eval["coste"]):
                    mejor_eval = e
            elif (not mejor_eval["factible"]) and (e["violacion"] < mejor_eval["violacion"]):
                mejor_eval = e

        historial_starts.append({
            "start": i,
            "coste_mejor": mejor_start["coste"],
            "factible": mejor_start["factible"],
            "optimo_bool": optimo_bool,
            "tiempo": t1 - t0,
        })

    prob_optimo_muestras = (
        muestras_opt / total_muestras if total_muestras else 0
    )

    prob_optimo_starts = (
        sum(1 for h in historial_starts if h["optimo_bool"]) / starts
        if starts > 0 else 0
    )

    tasa_fact_muestras = (
        muestras_fact / total_muestras if total_muestras else 0
    )

    ratio_medio_factibles = (
        statistics.mean(ratios_factibles) if ratios_factibles else 0
    )

    metricas = {
        "prob_optimo_muestras": prob_optimo_muestras,
        "prob_optimo_starts": prob_optimo_starts,
        "tasa_factibilidad_muestras": tasa_fact_muestras,
        "ratio_medio_factibles": ratio_medio_factibles,
        "total_muestras": total_muestras,
        "starts": starts,
    }

    return mejor_eval, metricas, historial_starts


def qp_qubo(qp):
    conv = QuadraticProgramToQubo()
    qubo = conv.convert(qp)

    Q = {}

    for var, coef in qubo.objective.linear.to_dict(use_name=True).items():
        Q[(var, var)] = coef

    for (i, j), coef in qubo.objective.quadratic.to_dict(use_name=True).items():
        Q[(i, j)] = coef

    return Q, qubo


def resolver_sa(qp, num_reads=100):
    Q, qubo = qp_qubo(qp)

    sampler = SimulatedAnnealingSampler()
    sampleset = sampler.sample_qubo(Q, num_reads=num_reads)

    return sampleset, qubo

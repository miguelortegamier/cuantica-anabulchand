import dimod
from neal import SimulatedAnnealingSampler
from qiskit_optimization.converters import QuadraticProgramToQubo
import time
import statistics

from evaluacion_kp import evaluar_resultado_sa

def resolver_sa_multi_start(qp, problema, opt_val_total, starts = 10, num_reads = 10):
    
    historial_starts = []
    total_muestras, muestras_opt, muestras_fact = 0, 0, 0
    mejor_eval = None 
    ratios_factibles = []

    t0_total = time.perf_counter()

    sampler = SimulatedAnnealingSampler()
    Q, _ = qp_qubo(qp)

    for i in range(starts):
        t0 = time.perf_counter()

        sampleset = sampler.sample_qubo(Q, num_reads=num_reads)

        evaluaciones = [
            evaluar_resultado_sa(sample, problema)
            for sample in sampleset.samples()
        ]

        t1 = time.perf_counter()

        mejor_start = max(evaluaciones, key=lambda e: (e["factible"], e["valor"]))

        optimo_bool = any(e["factible"] and e["valor"] == opt_val_total for e in evaluaciones)

        for e in evaluaciones:
            total_muestras += 1

            if e["factible"]:
                muestras_fact += 1
                ratios_factibles.append(e["valor"] / opt_val_total if opt_val_total > 0 else 0)

                if e["valor"] == opt_val_total:
                    muestras_opt += 1

            if mejor_eval is None or (
                (e["factible"], e["valor"]) > 
                (mejor_eval["factible"], mejor_eval["valor"])
            ):

                mejor_eval = e

        historial_starts.append({
            "start": i,
            "valor_mejor": mejor_start["valor"],
            "factible": mejor_start["factible"],
            "optimo_bool": optimo_bool,
            "tiempo": t1 - t0,
        })

    t_total = time.perf_counter() - t0_total

    prob_optimo_muestras = (
        muestras_opt / total_muestras if total_muestras else 0
    )

    prob_optimo_starts = (
        sum(1 for h in historial_starts if h["optimo_bool"])/starts 
        if starts > 0 else 0
    )

    tasa_fact_muestras = (muestras_fact / total_muestras if total_muestras else 0)

    ratio_medio_factibles = (
        statistics.mean(ratios_factibles) if ratios_factibles else 0
    )

    mejor_valor_start = [h["valor_mejor"] for h in historial_starts]

    valor_medio_start = statistics.mean(mejor_valor_start) if mejor_valor_start else 0
    std_valor_start = statistics.pstdev(mejor_valor_start) if len(mejor_valor_start) > 1 else 0

    tiempo_medio_start = (
        statistics.mean(h["tiempo"] for h in historial_starts)
        if historial_starts else 0
    )

    metricas = {
        "prob_optimo_muestras": prob_optimo_muestras, #Proporción muestras alcanzan óptimo
        "prob_optimo_starts": prob_optimo_starts, #Proporción starts encuentran al menos un óptimo
        "tasa_factibilidad_muestras": tasa_fact_muestras, #Proporción muestras cumplen restricción
        "ratio_medio_factibles": ratio_medio_factibles, #Calidad media de las soluciones factibles 
        "valor_medio_start": valor_medio_start, #Valor medio mejor solución cada start (no normalizado)
        "std_valor_start": std_valor_start, #Variabilidad rendimiento entre starts (no normalizado)
        "tiempo_total": t_total,
        "tiempo_medio_start": tiempo_medio_start,
        "total_muestras": total_muestras,
        "starts": starts,
        "num_reads_start": num_reads
    }

    return mejor_eval, metricas, historial_starts


def qp_qubo(qp):
    conv = QuadraticProgramToQubo()
    qubo = conv.convert(qp)

    Q = {}

    for var, coef in qubo.objective.linear.to_dict().items():
        Q[(var, var)] = coef

    for (i, j), coef in qubo.objective.quadratic.to_dict().items():
        Q[(i, j)] = coef

    return Q, qubo


def resolver_sa(qp, num_reads=100):
    Q, qubo = qp_qubo(qp)

    sampler = SimulatedAnnealingSampler()
    sampleset = sampler.sample_qubo(Q, num_reads=num_reads)

    return sampleset, qubo

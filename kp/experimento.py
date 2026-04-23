import time
from modelo import construir_problema
from qaoa_solver import resolver_qaoa
from ruido import crear_sampler_con_ruido
from evaluacion import evaluar_resultado_qaoa, evaluar_resultado_sa

def construir_fila_resultado(caso, evaluado, metricas, tiempo_total):
    return {
        "id": caso["id"],
        "optimo": caso["optimo"],
        "valor_total": evaluado["valor"],
        "peso": evaluado["peso"],
        "factible": evaluado["factible"],
        "coincide": evaluado["valor"] == caso["optimo"] and evaluado["factible"],
        "ratio_optimo": (
            evaluado["valor"] / caso["optimo"]
            if evaluado["factible"] and caso["optimo"] > 0
            else 0),
        "prob_optimo": metricas["prob_optimo"],
        "ratio_optimo_medio": metricas["ratio_medio"],
        "tiempo_total": tiempo_total,
        "t_solver": metricas["t_solver"],
        "t_cuantico": metricas["t_cuantico"],
        "t_clasico": metricas["t_clasico"],
    }

def ejecutar_experimentos(casos, metodo):
    resultados = []

    for caso in casos:
        problema, qp = construir_problema(caso)

        t0 = time.perf_counter()

        if metodo == "qaoa":
            result_qaoa, historial, metricas = resolver_qaoa(
                qp,
                problema,
                caso["optimo"],
            )
            
            evaluado = evaluar_resultado_qaoa(result_qaoa, problema)

        elif metodo == "sa":
            from sa_solver import resolver_sa

            t_solver_0 = time.perf_counter()

            sampleset, _ = resolver_sa(qp, num_reads=100)

            t_solver = time.perf_counter() - t_solver_0

            evaluaciones = [
                evaluar_resultado_sa(sample, problema)
                for sample in sampleset.samples()
            ]

            factibles = [e for e in evaluaciones if e["factible"]]

            optimos = [
                e for e in evaluaciones
                if e["factible"] and e["valor"] == caso["optimo"]
            ]

            total, optimos = 0, 0

            for sample, energy, num_occurrences in sampleset.data():
                total += num_occurrences
                if evaluar_resultado_sa(sample, problema)["factible"] and evaluar_resultado_sa(sample, problema)["valor"] == caso["optimo"]:
                    optimos += num_occurrences

            prob_optimo = optimos / total if total > 0 else 0

            ratio_medio = (
                sum(e["valor"] / caso["optimo"] for e in factibles)
                / len(factibles)
                if factibles else 0
            )

            evaluado = max(
                evaluaciones,
                key=lambda e: (e["factible"], e["valor"])
            )

            metricas = {
                "prob_optimo": prob_optimo, #Solo va a dar 0 o 1 para SA
                "ratio_medio": ratio_medio, #Lo mismo -> Poner en tablas diferenciadas
                "t_solver": t_solver,
                "t_cuantico": 0,
                "t_clasico": t_solver,
            }
        else:
            raise ValueError(f"Metodo no reconocido: {metodo}")

        tiempo_total = time.perf_counter() - t0

        fila = construir_fila_resultado(
            caso,
            evaluado,
            metricas,
            tiempo_total,
        )

        resultados.append(fila)

    return resultados

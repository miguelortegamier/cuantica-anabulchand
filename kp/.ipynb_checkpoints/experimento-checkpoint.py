import time
from modelo import construir_problema
from qaoa_solver import resolver_qaoa
from ruido import crear_sampler_con_ruido
from evaluacion import evaluar_resultado

def construir_fila_resultado(caso, evaluado, metricas, tiempo_total):
    return {
        "id": caso["id"],
        "optimo": caso["optimo_ref"],
        "valor_total": evaluado["valor"],
        "peso": evaluado["peso"],
        "factible": evaluado["factible"],
        "coincide": evaluado["valor"] == caso["optimo"] and evaluado["factible"],
        "ratio_optimo": (
            evaluado["valor"] / caso["optimo"]
            if evaluado["factible"] and caso["optimo"] > 0
            else 0),
        if caso["optimo"] > 0 else 0,
        "prob_optimo": metricas["prob_optimo"],
        "ratio_optimo_medio": metricas["ratio_medio"],
        "tiempo_total": tiempo_total,
        "t_solver": metricas["t_solver"],
        "t_cuantico": metricas["t_cuantico"],
        "t_clasico": metricas["t_clasico"],
    }

def ejecutar_experimentos(casos):
    resultados = []

    for caso in casos:
        problema, qp = construir_problema(caso)

        t0 = time.perf_counter()

        result_qaoa, historial, metricas = resolver_qaoa(
            qp,
            problema,
            caso["optimo"],
        )

        tiempo_total = time.perf_counter() - t0

        evaluado = evaluar_resultado(result_qaoa, problema)

        fila = construir_fila_resultado(
            caso,
            evaluado,
            metricas,
            tiempo_total,
        )

        resultados.append(fila)

    return resultados

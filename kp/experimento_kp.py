import csv
from pathlib import Path
import time
from modelo_kp import construir_problema
from qaoa_solver_kp import resolver_qaoa
from evaluacion_kp import evaluar_resultado_qaoa, evaluar_resultado_sa
from sa_solver_kp import resolver_sa_multi_start

NO_APLICA = "N/A"
METODOS_QAOA = {"qaoa", "qaoa_warmstart"}
METODOS_SA = {"sa"}

CAMPOS_QAOA = [
    "prob_optimo",
    "ratio_optimo_medio",
    "t_solver",
    "t_cuantico",
    "t_clasico",
    "pct_tiempo_solver_sobre_total",
    "pct_tiempo_cuantico_sobre_solver",
    "pct_tiempo_clasico_sobre_solver",
    "tiempo_medio_iter",
    "tiempo_por_eval",
    "total_evals",
    "num_factibles_qaoa",
]
CAMPOS_SA = [
    "prob_optimo_muestras",
    "prob_optimo_starts",
    "tasa_factibilidad",
    "ratio_medio_factibles",
    "valor_medio_start",
    "std_valor_start",
    "tiempo_medio_start",
    "total_muestras",
    "reads_por_start",
    "muestras_esperadas",
]
CAMPOS_WARMSTART = [
    "warmstart",
    "epsilon_warmstart",
]

def guardar_fila_csv(fila, ruta_csv):
    ruta_csv = Path(ruta_csv)
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)

    escribir_cabecera = (not ruta_csv.exists()) or ruta_csv.stat().st_size == 0

    with ruta_csv.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fila.keys()))

        if escribir_cabecera:
            writer.writeheader()

        writer.writerow(fila)


def marcar_no_aplica_por_metodo(fila, metodo):
    if metodo in METODOS_SA:
        for campo in CAMPOS_QAOA + CAMPOS_WARMSTART:
            fila[campo] = NO_APLICA
    elif metodo in METODOS_QAOA:
        for campo in CAMPOS_SA:
            fila[campo] = NO_APLICA

        if metodo == "qaoa":
            for campo in CAMPOS_WARMSTART:
                fila[campo] = NO_APLICA
    else:
        raise ValueError(f"Metodo no reconocido: {metodo}")

    return fila


def construir_fila_resultado(caso, evaluado, metricas, tiempo_total, metodo, problema, qp):
    optimo = caso["optimo"]
    valor = evaluado["valor"]
    peso = evaluado["peso"]
    capacidad = problema.capacidad
    factible = evaluado["factible"]
    coincide = valor == optimo and factible
    ratio_optimo = (
        valor / optimo
        if factible and optimo > 0
        else 0
    )
    brecha_optimo = (
        optimo - valor
        if factible
        else None
    )
    exceso_peso = max(0, peso - capacidad)
    t_solver = metricas.get("t_solver")
    t_cuantico = metricas.get("t_cuantico")
    t_clasico = metricas.get("t_clasico")
    starts = metricas.get("starts")
    reads_por_start = metricas.get("num_reads_start")
    total_muestras = metricas.get("total_muestras")
    total_evals = metricas.get("total_evals")

    fila = {
        "id": caso["id"],
        "num_items": len(problema.valores),
        "capacidad": capacidad,
        "num_variables_qubo": qp.get_num_binary_vars(),
        "optimo": optimo,
        "valor_total": valor,
        "peso": peso,
        "factible": factible,
        "coincide": coincide,
        "ratio_optimo": ratio_optimo,
        "brecha_optimo": brecha_optimo,
        "exceso_peso": exceso_peso,
        "prob_optimo": metricas.get("prob_optimo"),
        "ratio_optimo_medio": metricas.get("ratio_medio"),
        "tiempo_total": tiempo_total,
        "t_solver": t_solver,
        "t_cuantico": t_cuantico,
        "t_clasico": t_clasico,
        "pct_tiempo_solver_sobre_total": (
            t_solver / tiempo_total if t_solver is not None and tiempo_total > 0 else None
        ),
        "pct_tiempo_cuantico_sobre_solver": (
            t_cuantico / t_solver if t_cuantico is not None and t_solver not in (None, 0) else None
        ),
        "pct_tiempo_clasico_sobre_solver": (
            t_clasico / t_solver if t_clasico is not None and t_solver not in (None, 0) else None
        ),
        "tiempo_medio_iter": metricas.get("tiempo_medio_iter"),
        "tiempo_por_eval": metricas.get("tiempo_por_eval"),
        "total_evals": total_evals,
        "num_factibles_qaoa": metricas.get("num_factibles"),
        "prob_optimo_muestras": metricas.get("prob_optimo_muestras"),
        "prob_optimo_starts": metricas.get("prob_optimo_starts"),
        "tasa_factibilidad": metricas.get("tasa_factibilidad_muestras"),
        "ratio_medio_factibles": metricas.get("ratio_medio_factibles"),
        "valor_medio_start": metricas.get("valor_medio_start"),
        "std_valor_start": metricas.get("std_valor_start"),
        "tiempo_medio_start": metricas.get("tiempo_medio_start"),
        "total_muestras": total_muestras,
        "starts": starts,
        "reads_por_start": reads_por_start,
        "muestras_esperadas": (
            starts * reads_por_start if starts is not None and reads_por_start is not None else None
        ),
        "metodo": metodo,
        "warmstart": metricas.get("warmstart", False),
        "epsilon_warmstart": metricas.get("epsilon_warmstart", None),
    }

    return marcar_no_aplica_por_metodo(fila, metodo)

def ejecutar_experimentos(casos, metodo, ruta_csv=None):
    resultados = []

    if ruta_csv is None:
        ruta_csv = Path(__file__).resolve().parent / "resultados_kp.csv"

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
        elif metodo == "qaoa_warmstart":
            result_qaoa, historial, metricas = resolver_qaoa(
                qp,
                problema,
                caso["optimo"],
                warmstart=True,
            )

            evaluado = evaluar_resultado_qaoa(result_qaoa, problema)

        elif metodo == "sa":
            starts, num_reads = 10, 100
            reads_por_start = num_reads // starts if num_reads >= starts else 1

            mejor_eval, metricas, historial = resolver_sa_multi_start(
                qp,
                problema,
                caso["optimo"],
                starts=starts,
                num_reads=reads_por_start,
            )

            evaluado = mejor_eval
        else:
            raise ValueError(f"Metodo no reconocido: {metodo}")

        tiempo_total = time.perf_counter() - t0

        fila = construir_fila_resultado(
            caso,
            evaluado,
            metricas,
            tiempo_total,
            metodo,
            problema,
            qp,
        )

        resultados.append(fila)
        guardar_fila_csv(fila, ruta_csv)

    return resultados

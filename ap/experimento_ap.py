import csv
from pathlib import Path
import time

from evaluacion_ap import evaluar_resultado_qaoa, evaluar_resultado_sa
from modelo_ap import construir_problema
from qaoa_solver_ap import resolver_qaoa
from sa_solver_ap import resolver_sa_multi_start

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
    "coste_medio_start",
    "std_coste_start",
    "tiempo_medio_start",
    "total_muestras",
    "reads_por_start",
    "muestras_esperadas",
]
CAMPOS_WARMSTART = [
    "warmstart",
    "epsilon_warmstart",
]

CAMPOS_CSV_AP = [
    "id",
    "num_filas",
    "num_columnas",
    "tamano_matriz",
    "num_variables_qubo",
    "optimo",
    "coste_total",
    "violacion",
    "factible",
    "coincide",
    "ratio_optimo",
    "brecha_optimo",
    "desviacion_relativa_optimo",
    "prob_optimo",
    "ratio_optimo_medio",
    "tiempo_total",
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
    "prob_optimo_muestras",
    "prob_optimo_starts",
    "tasa_factibilidad",
    "ratio_medio_factibles",
    "coste_medio_start",
    "std_coste_start",
    "tiempo_medio_start",
    "total_muestras",
    "starts",
    "reads_por_start",
    "muestras_esperadas",
    "penalizacion",
    "metodo",
    "warmstart",
    "epsilon_warmstart",
]


def guardar_fila_csv(fila, ruta_csv):
    ruta_csv = Path(ruta_csv)
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)

    escribir_cabecera = True
    modo = "a"

    if ruta_csv.exists() and ruta_csv.stat().st_size > 0:
        with ruta_csv.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            cabecera_existente = next(reader, [])

        if cabecera_existente == CAMPOS_CSV_AP:
            escribir_cabecera = False
        else:
            # El CSV de AP estuvo cambiando de esquema; si detectamos uno
            # antiguo, regeneramos el fichero con la cabecera estable actual.
            modo = "w"

    with ruta_csv.open(modo, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV_AP)

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


def construir_fila_resultado(
    caso,
    evaluado,
    metricas,
    tiempo_total,
    penalizacion,
    metodo,
    problema,
    qp,
):
    m = len(problema.costes)
    n = len(problema.costes[0])
    optimo = caso["optimo"]
    coste = evaluado["coste"]
    violacion = evaluado["violacion"]
    factible = evaluado["factible"]
    coincide = factible and coste == optimo
    ratio_optimo = (
        optimo / coste
        if factible and coste > 0
        else 0
    )
    brecha_optimo = (
        coste - optimo
        if factible
        else None
    )
    t_solver = metricas.get("t_solver")
    t_cuantico = metricas.get("t_cuantico")
    t_clasico = metricas.get("t_clasico")
    total_evals = metricas.get("total_evals")
    starts = metricas.get("starts")
    reads_por_start = metricas.get("num_reads_start")
    total_muestras = metricas.get("total_muestras")

    fila = {
        "id": caso["id"],
        "num_filas": m,
        "num_columnas": n,
        "tamano_matriz": f"{m}x{n}",
        "num_variables_qubo": qp.get_num_binary_vars(),
        "optimo": optimo,
        "coste_total": coste,
        "violacion": violacion,
        "factible": factible,
        "coincide": coincide,
        "ratio_optimo": ratio_optimo,
        "brecha_optimo": brecha_optimo,
        "desviacion_relativa_optimo": (
            brecha_optimo / optimo if brecha_optimo is not None and optimo > 0 else None
        ),
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
        "coste_medio_start": metricas.get("coste_medio_start"),
        "std_coste_start": metricas.get("std_coste_start"),
        "tiempo_medio_start": metricas.get("tiempo_medio_start"),
        "total_muestras": total_muestras,
        "starts": starts,
        "reads_por_start": reads_por_start,
        "muestras_esperadas": (
            starts * reads_por_start if starts is not None and reads_por_start is not None else None
        ),
        "penalizacion": penalizacion,
        "metodo": metodo,
        "warmstart": metricas.get("warmstart", False),
        "epsilon_warmstart": metricas.get("epsilon_warmstart", None),
    }

    return marcar_no_aplica_por_metodo(fila, metodo)


def ejecutar_experimentos(casos, metodo, ruta_csv=None):
    resultados = []

    if ruta_csv is None:
        ruta_csv = Path(__file__).resolve().parent / "resultados_ap.csv"

    for caso in casos:
        t0_total = time.perf_counter()
        problema, qp, penalizacion = construir_problema(caso)
        t_preparacion = time.perf_counter() - t0_total

        t0 = time.perf_counter()

        if metodo == "qaoa":
            result_qaoa, historial, metricas = resolver_qaoa(
                qp,
                problema,
                caso["optimo"],
            )
            metricas["t_solver"] += t_preparacion
            metricas["t_clasico"] += t_preparacion

            evaluado = evaluar_resultado_qaoa(result_qaoa, problema)
        elif metodo == "qaoa_warmstart":
            result_qaoa, historial, metricas = resolver_qaoa(
                qp,
                problema,
                caso["optimo"],
                warmstart=True,
            )
            metricas["t_solver"] += t_preparacion
            metricas["t_clasico"] += t_preparacion

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

        tiempo_total = time.perf_counter() - t0_total

        fila = construir_fila_resultado(
            caso,
            evaluado,
            metricas,
            tiempo_total,
            penalizacion,
            metodo,
            problema,
            qp,
        )

        resultados.append(fila)
        guardar_fila_csv(fila, ruta_csv)

    return resultados

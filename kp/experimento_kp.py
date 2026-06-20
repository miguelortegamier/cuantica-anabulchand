import csv
from pathlib import Path
import time

from evaluacion_kp import evaluar_resultado_qaoa
from modelo_kp import construir_problema
from qaoa_solver_kp import resolver_qaoa
from sa_solver_kp import resolver_sa_multi_start
from sqa_solver_kp import resolver_sqa_multi_start


NO_APLICA = "N/A"
METODOS_QAOA = {"qaoa", "qaoa_warmstart"}
METODOS_MUESTREO = {"sa", "sqa"}

#Campos comunes para comparar metodos sin cambiar el CSV cada vez.
CAMPOS_CSV_KP = [
    "id",
    "num_items",
    "capacidad",
    "num_variables_qubo",
    "optimo",
    "metodo",
    "valor_total",
    "peso",
    "factible",
    "ratio_optimo",
    "tiempo_total",
    "prob_optimo_starts",
    "prob_optimo_muestras",
    "tasa_factibilidad",
    "ratio_medio_factibles",
    "starts",
    "total_muestras",
    "tiempo_por_eval",
    "total_evals",
    "warmstart",
    "epsilon_warmstart",
    "sqa_beta",
    "sqa_gamma",
    "sqa_trotter",
    "sqa_num_sweeps",
]


def guardar_fila_csv(fila, ruta_csv):
    ruta_csv = Path(ruta_csv)
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)
    escribir_cabecera = not ruta_csv.exists() or ruta_csv.stat().st_size == 0

    if not escribir_cabecera:
        with ruta_csv.open("r", newline="", encoding="utf-8") as f:
            cabecera_existente = next(csv.reader(f), [])
        if cabecera_existente != CAMPOS_CSV_KP:
            raise ValueError(
                f"El CSV {ruta_csv} usa una cabecera antigua. "
                "Migralo al esquema compacto antes de anadir resultados."
            )

    with ruta_csv.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV_KP)
        if escribir_cabecera:
            writer.writeheader()
        writer.writerow(fila)


def _calidad_final(caso, evaluado):
    optimo = caso["optimo"]
    factible = evaluado["factible"]
    return (
        evaluado["valor"] / optimo
        if factible and optimo > 0
        else 0
    )


def construir_fila_resultado(caso, evaluado, metricas, tiempo_total, metodo, problema, qp):
    starts = metricas.get("starts")

    #QAOA mide starts, SA/SQA tambien cuentan muestras internas.
    if metodo in METODOS_QAOA:
        prob_optimo_starts = metricas.get("prob_optimo")
        tasa_factibilidad = (
            metricas.get("num_factibles") / starts
            if starts else NO_APLICA
        )
        ratio_medio_factibles = metricas.get("ratio_medio")
    elif metodo in METODOS_MUESTREO:
        prob_optimo_starts = metricas.get("prob_optimo_starts")
        tasa_factibilidad = metricas.get("tasa_factibilidad_muestras")
        ratio_medio_factibles = metricas.get("ratio_medio_factibles")
    else:
        raise ValueError(f"Metodo no reconocido: {metodo}")

    return {
        "id": caso["id"],
        "num_items": len(problema.valores),
        "capacidad": problema.capacidad,
        "num_variables_qubo": qp.get_num_binary_vars(),
        "optimo": caso["optimo"],
        "metodo": metodo,
        "valor_total": evaluado["valor"],
        "peso": evaluado["peso"],
        "factible": evaluado["factible"],
        "ratio_optimo": _calidad_final(caso, evaluado),
        "tiempo_total": tiempo_total,
        "prob_optimo_starts": prob_optimo_starts,
        "prob_optimo_muestras": (
            metricas.get("prob_optimo_muestras", NO_APLICA)
            if metodo in METODOS_MUESTREO else NO_APLICA
        ),
        "tasa_factibilidad": tasa_factibilidad,
        "ratio_medio_factibles": ratio_medio_factibles,
        "starts": starts,
        "total_muestras": (
            metricas.get("total_muestras", NO_APLICA)
            if metodo in METODOS_MUESTREO else NO_APLICA
        ),
        "tiempo_por_eval": (
            metricas.get("tiempo_por_eval", NO_APLICA)
            if metodo in METODOS_QAOA else NO_APLICA
        ),
        "total_evals": (
            metricas.get("total_evals", NO_APLICA)
            if metodo in METODOS_QAOA else NO_APLICA
        ),
        "warmstart": (
            metricas.get("warmstart", NO_APLICA)
            if metodo == "qaoa_warmstart" else NO_APLICA
        ),
        "epsilon_warmstart": (
            metricas.get("epsilon_warmstart", NO_APLICA)
            if metodo == "qaoa_warmstart" else NO_APLICA
        ),
        "sqa_beta": metricas.get("sqa_beta", NO_APLICA) if metodo == "sqa" else NO_APLICA,
        "sqa_gamma": metricas.get("sqa_gamma", NO_APLICA) if metodo == "sqa" else NO_APLICA,
        "sqa_trotter": metricas.get("sqa_trotter", NO_APLICA) if metodo == "sqa" else NO_APLICA,
        "sqa_num_sweeps": (
            metricas.get("sqa_num_sweeps", NO_APLICA)
            if metodo == "sqa" else NO_APLICA
        ),
    }


def ejecutar_experimentos(casos, metodo, ruta_csv=None):
    resultados = []

    if ruta_csv is None:
        ruta_csv = Path(__file__).resolve().parent / "resultados.csv"

    for caso in casos:
        t0_total = time.perf_counter()
        problema, qp = construir_problema(caso)

        #Cada metodo devuelve metricas con nombres distintos, se unifican abajo.
        if metodo in METODOS_QAOA:
            resultado, _, metricas = resolver_qaoa(
                qp,
                problema,
                caso["optimo"],
                warmstart=metodo == "qaoa_warmstart",
            )
            evaluado = evaluar_resultado_qaoa(resultado, problema)
        elif metodo in METODOS_MUESTREO:
            solver = resolver_sa_multi_start if metodo == "sa" else resolver_sqa_multi_start
            evaluado, metricas, _ = solver(
                qp,
                problema,
                caso["optimo"],
                starts=10,
                num_reads=10,
                semilla=0,
            )
        else:
            raise ValueError(f"Metodo no reconocido: {metodo}")

        fila = construir_fila_resultado(
            caso,
            evaluado,
            metricas,
            time.perf_counter() - t0_total,
            metodo,
            problema,
            qp,
        )
        resultados.append(fila)
        guardar_fila_csv(fila, ruta_csv)

    return resultados

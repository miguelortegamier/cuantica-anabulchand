from pathlib import Path
import sys


#Poder obtener files (como ruido.py) de la carpeta madre
raiz = Path(__file__).resolve().parent.parent
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))


from casos_kp import casos
from experimento_kp import ejecutar_experimentos

def formatear_numero(valor, decimales=4):
    if valor is None:
        return "-"
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, int):
        return str(valor)
    if isinstance(valor, float):
        return f"{valor:.{decimales}f}"
    return str(valor)

def imprimir_resultado_legible(fila):
    print(f"Caso {fila['id']} | metodo={fila['metodo']}")
    print(
        f"  Problema: items={fila['num_items']}, capacidad={fila['capacidad']}, "
        f"variables_qubo={fila['num_variables_qubo']}"
    )
    print(
        f"  Solucion: valor={fila['valor_total']}, optimo={fila['optimo']}, "
        f"ratio={formatear_numero(fila['ratio_optimo'])}, "
        f"brecha={formatear_numero(fila['brecha_optimo'])}, "
        f"peso={fila['peso']}, exceso_peso={fila['exceso_peso']}, "
        f"factible={fila['factible']}, coincide={fila['coincide']}"
    )
    print(
        f"  Calidad global: prob_optimo={formatear_numero(fila['prob_optimo'])}, "
        f"ratio_optimo_medio={formatear_numero(fila['ratio_optimo_medio'])}, "
        f"ratio_medio_factibles={formatear_numero(fila['ratio_medio_factibles'])}, "
        f"tasa_factibilidad={formatear_numero(fila['tasa_factibilidad'])}"
    )
    print(
        f"  Tiempos: total={formatear_numero(fila['tiempo_total'])} s, "
        f"solver={formatear_numero(fila['t_solver'])} s, "
        f"cuantico={formatear_numero(fila['t_cuantico'])} s, "
        f"clasico={formatear_numero(fila['t_clasico'])} s"
    )
    print(
        f"  Desglose tiempos: solver/total={formatear_numero(fila['pct_tiempo_solver_sobre_total'])}, "
        f"cuantico/solver={formatear_numero(fila['pct_tiempo_cuantico_sobre_solver'])}, "
        f"clasico/solver={formatear_numero(fila['pct_tiempo_clasico_sobre_solver'])}, "
        f"tiempo_medio_iter={formatear_numero(fila['tiempo_medio_iter'])} s, "
        f"tiempo_por_eval={formatear_numero(fila['tiempo_por_eval'])} s"
    )
    print(
        f"  Muestreo: starts={formatear_numero(fila['starts'])}, "
        f"reads_por_start={formatear_numero(fila['reads_por_start'])}, "
        f"total_muestras={formatear_numero(fila['total_muestras'])}, "
        f"muestras_esperadas={formatear_numero(fila['muestras_esperadas'])}, "
        f"total_evals={formatear_numero(fila['total_evals'])}, "
        f"num_factibles_qaoa={formatear_numero(fila['num_factibles_qaoa'])}"
    )
    print(
        f"  Optimos por muestreo: prob_optimo_muestras={formatear_numero(fila['prob_optimo_muestras'])}, "
        f"prob_optimo_starts={formatear_numero(fila['prob_optimo_starts'])}, "
        f"valor_medio_start={formatear_numero(fila['valor_medio_start'])}, "
        f"std_valor_start={formatear_numero(fila['std_valor_start'])}, "
        f"tiempo_medio_start={formatear_numero(fila['tiempo_medio_start'])} s"
    )
    print(
        f"  Warm-start: activo={fila['warmstart']}, "
        f"epsilon={formatear_numero(fila['epsilon_warmstart'])}"
    )
    print()

if __name__ == "__main__":
    resultados = ejecutar_experimentos(casos, "qaoa_warmstart")

    print("RESULTADOS:\n")
    for fila in resultados:
        imprimir_resultado_legible(fila)

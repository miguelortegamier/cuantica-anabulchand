import sys

import warnings
from scipy.sparse import SparseEfficiencyWarning

from casos_kp import casos
from experimento_kp import ejecutar_experimentos

warnings.simplefilter("ignore", SparseEfficiencyWarning)

METODOS_VALIDOS = {"qaoa", "qaoa_warmstart", "sa", "sqa"}
METODO_POR_DEFECTO = "qaoa"


def obtener_metodo():
    if len(sys.argv) <= 1:
        return METODO_POR_DEFECTO

    metodo = sys.argv[1]
    if metodo not in METODOS_VALIDOS:
        raise ValueError(
            f"Metodo no valido: {metodo}. "
            f"Usa uno de: {', '.join(sorted(METODOS_VALIDOS))}"
        )

    return metodo


if __name__ == "__main__":
    metodo = obtener_metodo()
    ejecutar_experimentos(casos, metodo)
    print(f"KP finalizado con metodo={metodo}. Resultados guardados en CSV.")

import sys

from casos_ap import casos
from experimento_ap import ejecutar_experimentos

import warnings
from scipy.sparse import SparseEfficiencyWarning

warnings.simplefilter("ignore", SparseEfficiencyWarning)

METODOS_VALIDOS = {"qaoa", "sa"}
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
    print(f"AP finalizado con metodo={metodo}. Resultados guardados en CSV.")

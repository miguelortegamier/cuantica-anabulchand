from pathlib import Path
import sys

from casos_ap import casos
from experimento_ap import ejecutar_experimentos

import warnings
from scipy.sparse import SparseEfficiencyWarning

warnings.simplefilter("ignore", SparseEfficiencyWarning)

if __name__ == "__main__":
    ejecutar_experimentos(casos, "qaoa")
    print("AP finalizado. Resultados guardados en CSV.")

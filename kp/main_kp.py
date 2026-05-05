from pathlib import Path
import sys

from casos_kp import casos
from experimento_kp import ejecutar_experimentos

import warnings
from scipy.sparse import SparseEfficiencyWarning

warnings.simplefilter("ignore", SparseEfficiencyWarning)

if __name__ == "__main__":
    ejecutar_experimentos(casos, "qaoa_warmstart")
    print("KP finalizado. Resultados guardados en CSV.")

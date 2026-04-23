from casos import casos
from experimento import ejecutar_experimentos

if __name__ == "__main__":
    resultados = ejecutar_experimentos(casos, "qaoa")

    print("RESULTADOS:\n")
    for fila in resultados:
        print(fila)

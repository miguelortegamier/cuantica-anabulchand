def evaluar_resultado(resultado, problema):
    variables_binarias = [round(i) for i in resultado.x[: len(problema.valores)]]

    valor_total = sum(
        problema.valores[i] * variables_binarias[i]
        for i in range(len(variables_binarias))
    )
    peso_total = sum(
        problema.pesos[i] * variables_binarias[i]
        for i in range(len(variables_binarias))
    )

    return {
        "x": variables_binarias,
        "valor": valor_total,
        "peso": peso_total,
        "factible": peso_total <= problema.capacidad,
    }

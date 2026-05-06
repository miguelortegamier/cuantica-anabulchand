def _leer_variable_sample(sample, indice):
    nombre = f"x{indice}"

    try:
        return int(round(sample[nombre]))
    except (KeyError, ValueError, IndexError):
        pass

    try:
        return int(round(sample[indice]))
    except (KeyError, ValueError, IndexError):
        raise ValueError(
            f"No se pudo leer la variable {nombre!r} ni el indice {indice} del sample SA."
        )


def evaluar_resultado_qaoa(resultado, problema):
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

def evaluar_resultado_sa(sample, problema):
    x = [
        _leer_variable_sample(sample, i)
        for i in range(len(problema.valores))
    ]

    valor_total = sum(
        problema.valores[i] * x[i]
        for i in range(len(x))
    )

    peso_total = sum(
        problema.pesos[i] * x[i]
        for i in range(len(x))
    )

    return {
        "x": x,
        "valor": valor_total,
        "peso": peso_total,
        "factible": peso_total <= problema.capacidad,
    }

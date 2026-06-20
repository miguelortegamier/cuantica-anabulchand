# AP

Esta carpeta contiene los experimentos del _Assignment Problem_ (AP). El objetivo es asignar cada agente a una tarea exactamente una vez, minimizando el coste total de la asignacion.

## Formulacion del problema

Esto se explica en el documento en la Sección 8.1.2. La entrada de cada caso es una matriz cuadrada `costes`, donde `costes[i][j]` representa el coste de asignar el agente `i` a la tarea `j`.

Se usan variables binarias:

```text
x_i_j = 1 si el agente i se asigna a la tarea j
x_i_j = 0 en caso contrario
```

La solución debe cumplir:

- Cada fila debe tener exactamente una asignacion.
- Cada columna debe tener exactamente una asignacion.
- El coste total debe ser lo menor posible.

El modelo QUBO se construye en `modelo_ap.py`. Como un QUBO no usa restricciones explicitas, las restricciones de filas y columnas se incorporan como penalizaciones dentro de la funcion objetivo.

## Archivos principales

- `casos_ap.py`: define las matrices de costes y el valor optimo conocido de cada caso.
- `modelo_ap.py`: construye el `QuadraticProgram` con variables binarias y penalizaciones.
- `evaluacion_ap.py`: convierte una solucion binaria en matriz de asignacion, coste total, violacion y factibilidad.
- `qaoa_solver_ap.py`: ejecuta QAOA con varios puntos iniciales aleatorios.
- `warmstart_ap.py`: crea el solver para `qaoa_warmstart` usando una relajacion clasica previa.
- `sa_solver_ap.py`: resuelve el QUBO con Simulated Annealing clasico.
- `sqa_solver_ap.py`: resuelve el QUBO con Simulated Quantum Annealing.
- `experimento_ap.py`: coordina la ejecucion de todos los casos y guarda metricas en CSV.
- `main_ap.py`: punto de entrada por consola.
- `resultados_ap.csv`: resultados acumulados de las ejecuciones.
- `analisis_resultados_ap.ipynb`: notebook para analizar los resultados.

## Como ejecutar

Desde la raiz del repositorio:

```bash
python ap/main_ap.py qaoa
python ap/main_ap.py qaoa_warmstart
python ap/main_ap.py sa
python ap/main_ap.py sqa
```

Si se ejecuta sin argumentos, usa `qaoa`:

```bash
python ap/main_ap.py
```

Los metodos validos son:

- `qaoa`
- `qaoa_warmstart`
- `sa`
- `sqa`

Cada ejecucion escribe nuevas filas en `ap/resultados_ap.csv`.

## Flujo interno

1. `main_ap.py` comprueba el metodo recibido por consola.
2. `experimento_ap.py` recorre todos los casos definidos en `casos_ap.py`.
3. Para cada caso, `modelo_ap.py` construye un QUBO.
4. Segun el metodo elegido, se llama a uno de los solvers.
5. `evaluacion_ap.py` decodifica la solucion y calcula si cumple las restricciones.
6. `experimento_ap.py` unifica las metricas y las guarda en `resultados_ap.csv`.

## Construccion del QUBO

La funcion principal es `construir_qubo(problema, penalizacion=None)` en `modelo_ap.py`.

Primero crea una variable binaria por cada posicion de la matriz. Despues define una funcion objetivo que combina:

- El coste real de la asignacion.
- Una penalizacion si una fila no tiene exactamente una asignacion.
- Una penalizacion si una columna no tiene exactamente una asignacion.

Si no se pasa una penalizacion manual, se calcula como:

```text
penalizacion = m * max_coste + 1
```

donde `m` es el numero de filas y `max_coste` es el mayor coste de la matriz. Esta penalizacion busca que violar una restriccion sea peor que cualquier mejora artificial del coste.

## Evaluacion de soluciones

`evaluacion_ap.py` calcula:

- `matriz`: matriz binaria de asignacion.
- `coste`: suma de los costes seleccionados.
- `violacion`: cantidad total de incumplimientos en filas y columnas.
- `factible`: `True` si `violacion == 0`.

En AP, una solucion es mejor si:

- Es factible.
- Entre las factibles, tiene menor coste.
- Si no hay factibles, tiene menor violacion.

## Metodos implementados

`qaoa` usa `QAOA` de `qiskit_algorithms`, `StatevectorSampler`, optimizador `SPSA`, `reps=3`, `maxiter=100`, `shots=1024` y `starts=10`.

`qaoa_warmstart` usa la misma base de QAOA, pero envuelta en `WarmStartQAOAOptimizer`. Antes de QAOA se resuelve una relajacion continua con `SlsqpOptimizer`.

`sa` transforma el `QuadraticProgram` a QUBO con `QuadraticProgramToQubo` y lo muestrea con `neal.SimulatedAnnealingSampler`.

`sqa` transforma tambien el problema a QUBO, pero usa `OpenJij` con `SQASampler`. Sus parametros por defecto son `beta=10`, `gamma=1.0`, `trotter=10` y `num_sweeps=1000`.

## Columnas del CSV

- `id`: identificador del caso.
- `tamano_matriz`: dimension de la matriz de costes.
- `num_variables_qubo`: numero de variables binarias del QUBO.
- `optimo`: coste optimo conocido.
- `penalizacion`: penalizacion usada para restricciones.
- `metodo`: algoritmo ejecutado.
- `coste_total`: coste de la mejor solucion encontrada.
- `violacion`: incumplimiento total de restricciones.
- `factible`: indica si la solucion respeta filas y columnas.
- `ratio_optimo`: `optimo / coste_total` si la solucion es factible.
- `tiempo_total`: tiempo total de ejecucion del caso.
- `prob_optimo_starts`: proporcion de arranques que encuentran el optimo.
- `prob_optimo_muestras`: proporcion de muestras optimas en SA/SQA.
- `tasa_factibilidad`: proporcion de soluciones factibles.
- `ratio_medio_factibles`: calidad media de las soluciones factibles.
- `starts`: numero de arranques usados.
- `total_muestras`: numero total de muestras en SA/SQA.
- `tiempo_por_eval`: tiempo medio por evaluacion en QAOA.
- `total_evals`: evaluaciones totales del optimizador en QAOA.
- `warmstart`: indica si se uso warm-start.
- `epsilon_warmstart`: parametro epsilon del warm-start.
- `sqa_beta`, `sqa_gamma`, `sqa_trotter`, `sqa_num_sweeps`: parametros especificos de SQA.
```

Para cambiar parametros de QAOA, modifica la llamada a `resolver_qaoa` o los valores por defecto de `resolver_qaoa` en `qaoa_solver_ap.py`.

Para cambiar parametros de SA o SQA, modifica los argumentos usados en `experimento_ap.py` o los valores por defecto definidos en `sa_solver_ap.py` y `sqa_solver_ap.py`.

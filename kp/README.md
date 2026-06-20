# KP: problema de la mochila

Esta carpeta contiene los experimentos del Knapsack Problem (KP). El objetivo es seleccionar un subconjunto de objetos que maximice el valor total sin superar la capacidad de la mochila.

En terminos simples: cada objeto tiene un valor y un peso. La solucion debe decidir que objetos se meten en la mochila para obtener el mayor valor posible respetando el limite de peso.

## Formulacion del problema

La entrada de cada caso contiene:

- `valores`: beneficio de cada objeto.
- `pesos`: peso de cada objeto.
- `capacidad`: peso maximo permitido.
- `optimo`: valor optimo conocido.

Se usan variables binarias:

```text
x_i = 1 si el objeto i se selecciona
x_i = 0 en caso contrario
```

Ademas, el QUBO introduce variables auxiliares de holgura:

```text
s_k
```

Estas variables representan la diferencia entre el peso usado y la capacidad. Gracias a ellas, la restriccion de capacidad se incorpora dentro de la funcion objetivo como una penalizacion.

## Archivos principales

- `casos_kp.py`: define los objetos, pesos, capacidades y optimos conocidos.
- `modelo_kp.py`: construye el `QuadraticProgram` del problema de mochila.
- `evaluacion_kp.py`: calcula valor total, peso total y factibilidad de una solucion.
- `qaoa_solver_kp.py`: ejecuta QAOA con varios puntos iniciales aleatorios.
- `warmstart_kp.py`: crea el solver para `qaoa_warmstart` usando una relajacion clasica previa.
- `sa_solver_kp.py`: resuelve el QUBO con Simulated Annealing clasico.
- `sqa_solver_kp.py`: resuelve el QUBO con Simulated Quantum Annealing.
- `experimento_kp.py`: coordina la ejecucion de todos los casos y guarda metricas en CSV.
- `main_kp.py`: punto de entrada por consola.
- `resultados.csv`: resultados acumulados de las ejecuciones.
- `analisis_resultados_kp.ipynb`: notebook para analizar los resultados.

## Como ejecutar

Desde la raiz del repositorio:

```bash
python kp/main_kp.py qaoa
python kp/main_kp.py qaoa_warmstart
python kp/main_kp.py sa
python kp/main_kp.py sqa
```

Si se ejecuta sin argumentos, usa `qaoa`:

```bash
python kp/main_kp.py
```

Los metodos validos son:

- `qaoa`
- `qaoa_warmstart`
- `sa`
- `sqa`

Cada ejecucion escribe nuevas filas en `kp/resultados.csv`.

## Flujo interno

1. `main_kp.py` comprueba el metodo recibido por consola.
2. `experimento_kp.py` recorre todos los casos definidos en `casos_kp.py`.
3. Para cada caso, `modelo_kp.py` construye un QUBO.
4. Segun el metodo elegido, se llama a uno de los solvers.
5. `evaluacion_kp.py` decodifica la solucion y calcula valor, peso y factibilidad.
6. `experimento_kp.py` unifica las metricas y las guarda en `resultados.csv`.

## Construccion del QUBO

La funcion principal es `construir_problema(caso)` en `modelo_kp.py`.

El QUBO combina dos ideas:

- Maximizar el valor de los objetos seleccionados.
- Penalizar las soluciones que no encajan con la capacidad representada mediante variables de holgura.

Como Qiskit minimiza la funcion objetivo, el valor de los objetos aparece con signo negativo:

```text
- valor_i * x_i
```

La penalizacion se construye a partir de:

```text
p = suma de todos los valores
```

Despues se penaliza la diferencia cuadratica entre el peso seleccionado mas la holgura y la capacidad de la mochila.

El numero de bits de holgura se calcula con:

```text
Kmax = floor(log2(capacidad))
```

Por tanto, el QUBO tiene:

```text
numero de objetos + numero de bits de holgura
```

variables binarias.

## Evaluacion de soluciones

`evaluacion_kp.py` lee las variables `x_i` de la solucion y calcula:

- `x`: lista binaria de objetos seleccionados.
- `valor`: suma de valores seleccionados.
- `peso`: suma de pesos seleccionados.
- `factible`: `True` si `peso <= capacidad`.

En KP, una solucion es mejor si:

- Es factible.
- Entre las factibles, tiene mayor valor.
- Si no hay factibles, se prefiere una solucion con menor peso.

## Metodos implementados

`qaoa` usa `QAOA` de `qiskit_algorithms`, `StatevectorSampler`, optimizador `SPSA`, `reps=3`, `maxiter=100`, `shots=1024` y `starts=10`.

`qaoa_warmstart` usa la misma base de QAOA, pero envuelta en `WarmStartQAOAOptimizer`. Antes de QAOA se resuelve una relajacion continua con `SlsqpOptimizer`.

`sa` transforma el `QuadraticProgram` a QUBO con `QuadraticProgramToQubo` y lo muestrea con `neal.SimulatedAnnealingSampler`.

`sqa` transforma tambien el problema a QUBO, pero usa `OpenJij` con `SQASampler`. Sus parametros por defecto son `beta=10`, `gamma=1.0`, `trotter=10` y `num_sweeps=1000`.

## Columnas del CSV

- `id`: identificador del caso.
- `num_items`: numero de objetos del problema.
- `capacidad`: capacidad maxima de la mochila.
- `num_variables_qubo`: numero de variables binarias del QUBO.
- `optimo`: valor optimo conocido.
- `metodo`: algoritmo ejecutado.
- `valor_total`: valor de la mejor solucion encontrada.
- `peso`: peso de la mejor solucion encontrada.
- `factible`: indica si la solucion respeta la capacidad.
- `ratio_optimo`: `valor_total / optimo` si la solucion es factible.
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

## Como modificar los experimentos

Para anadir un caso nuevo, edita `casos_kp.py` e incluye listas de valores y pesos con la misma longitud:

```python
{
    "id": 505,
    "valores": [...],
    "pesos": [...],
    "capacidad": ...,
    "optimo": ...,
}
```

Para cambiar parametros de QAOA, modifica la llamada a `resolver_qaoa` o los valores por defecto de `resolver_qaoa` en `qaoa_solver_kp.py`.

Para cambiar parametros de SA o SQA, modifica los argumentos usados en `experimento_kp.py` o los valores por defecto definidos en `sa_solver_kp.py` y `sqa_solver_kp.py`.

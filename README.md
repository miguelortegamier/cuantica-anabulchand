# Comparacion de metodos cuanticos y clasicos para problemas de optimizacion

Este repositorio contiene el codigo experimental usado para comparar distintas estrategias de resolucion sobre dos problemas combinatorios formulados como QUBO:

- `ap`: Assignment Problem o problema de asignacion.
- `kp`: Knapsack Problem o problema de la mochila.

En ambos casos se construye un modelo QUBO con `qiskit-optimization` y se resuelve con cuatro enfoques:

- `qaoa`: Quantum Approximate Optimization Algorithm.
- `qaoa_warmstart`: QAOA con inicializacion clasica mediante `WarmStartQAOAOptimizer`.
- `sa`: Simulated Annealing clasico usando `neal`.
- `sqa`: Simulated Quantum Annealing usando `OpenJij`.

## Estructura del repositorio

```text
.
|-- ap/
|   |-- README.md
|   |-- casos_ap.py
|   |-- modelo_ap.py
|   |-- evaluacion_ap.py
|   |-- qaoa_solver_ap.py
|   |-- warmstart_ap.py
|   |-- sa_solver_ap.py
|   |-- sqa_solver_ap.py
|   |-- experimento_ap.py
|   |-- main_ap.py
|   |-- resultados_ap.csv
|   `-- analisis_resultados_ap.ipynb
|-- kp/
|   |-- README.md
|   |-- casos_kp.py
|   |-- modelo_kp.py
|   |-- evaluacion_kp.py
|   |-- qaoa_solver_kp.py
|   |-- warmstart_kp.py
|   |-- sa_solver_kp.py
|   |-- sqa_solver_kp.py
|   |-- experimento_kp.py
|   |-- main_kp.py
|   |-- resultados.csv
|   `-- analisis_resultados_kp.ipynb
`-- README.md
```

La organizacion de `ap` y `kp` es paralela. Cada carpeta tiene sus propios casos de prueba, construccion del QUBO, evaluacion de soluciones, solvers, ejecucion experimental y fichero CSV de resultados.

## Requisitos

El codigo esta escrito en Python y usa las siguientes dependencias principales:

```bash
pip install qiskit qiskit-algorithms qiskit-optimization scipy dimod dwave-neal openjij
```

`openjij` solo es necesario para ejecutar el metodo `sqa`. Los metodos `qaoa`, `qaoa_warmstart` y `sa` no dependen de OpenJij.

## Ejecucion rapida

Desde la raiz del repositorio:

```bash
python ap/main_ap.py qaoa
python ap/main_ap.py qaoa_warmstart
python ap/main_ap.py sa
python ap/main_ap.py sqa

python kp/main_kp.py qaoa
python kp/main_kp.py qaoa_warmstart
python kp/main_kp.py sa
python kp/main_kp.py sqa
```

Si no se indica metodo, se ejecuta `qaoa` por defecto:

```bash
python ap/main_ap.py
python kp/main_kp.py
```

Cada ejecucion recorre todos los casos definidos en `casos_ap.py` o `casos_kp.py` y anade una fila por caso al CSV correspondiente.

## Flujo general del codigo

1. `main_*.py` lee el metodo indicado por consola.
2. `casos_*.py` proporciona las instancias experimentales y el optimo conocido.
3. `modelo_*.py` transforma cada instancia en un `QuadraticProgram` de Qiskit.
4. `qaoa_solver_*.py`, `sa_solver_*.py` o `sqa_solver_*.py` resuelve el QUBO.
5. `evaluacion_*.py` interpreta la solucion binaria en terminos del problema original.
6. `experimento_*.py` calcula metricas comparables y guarda los resultados en CSV.
7. `analisis_resultados_*.ipynb` permite estudiar los CSV y generar conclusiones.

## Lectura recomendada

Para entender el codigo en detalle:

- Empieza por `ap/README.md` para el problema de asignacion.
- Sigue con `kp/README.md` para el problema de mochila.
- Despues revisa `modelo_ap.py` y `modelo_kp.py`, porque ahi esta la formulacion matematica que conecta el problema original con el QUBO.

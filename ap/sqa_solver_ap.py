import statistics

from qiskit_optimization.converters import QuadraticProgramToQubo

from evaluacion_ap import evaluar_resultado_sa


SQA_BETA = 10
SQA_GAMMA = 1.0
SQA_TROTTER = 10
SQA_NUM_SWEEPS = 1000


def crear_sampler_sqa():
    try:
        import openjij as oj
    except ImportError as exc:
        raise RuntimeError(
            "OpenJij no esta instalado. Instala la dependencia con: pip install openjij"
        ) from exc

    return oj.SQASampler()


def qp_qubo(qp):
    qubo = QuadraticProgramToQubo().convert(qp)
    q = {}

    for var, coef in qubo.objective.linear.to_dict(use_name=True).items():
        q[(var, var)] = coef

    for (i, j), coef in qubo.objective.quadratic.to_dict(use_name=True).items():
        q[(i, j)] = coef

    return q


def resolver_sqa_multi_start(
    qp,
    problema,
    opt_coste,
    starts=10,
    num_reads=10,
    beta=SQA_BETA,
    gamma=SQA_GAMMA,
    trotter=SQA_TROTTER,
    num_sweeps=SQA_NUM_SWEEPS,
    semilla=0,
):
    historial_starts = []
    total_muestras = 0
    muestras_opt = 0
    muestras_fact = 0
    mejor_eval = None
    ratios_factibles = []
    sampler = crear_sampler_sqa()
    q = qp_qubo(qp)

    for i in range(starts):
        #Algunas versiones de OpenJij no aceptan seed en sample_qubo.
        parametros = {
            "num_reads": num_reads,
            "beta": beta,
            "gamma": gamma,
            "trotter": trotter,
            "num_sweeps": num_sweeps,
            "seed": semilla + i,
        }

        try:
            sampleset = sampler.sample_qubo(q, **parametros)
        except TypeError:
            parametros.pop("seed")
            sampleset = sampler.sample_qubo(q, **parametros)

        evaluaciones = [
            evaluar_resultado_sa(sample, problema)
            for sample in sampleset.samples()
        ]
        optimo_start = any(
            e["factible"] and e["coste"] == opt_coste
            for e in evaluaciones
        )

        for evaluado in evaluaciones:
            total_muestras += 1

            #Mismas reglas que SA para que la comparacion sea justa.
            if evaluado["factible"]:
                muestras_fact += 1
                ratios_factibles.append(
                    opt_coste / evaluado["coste"] if evaluado["coste"] > 0 else 0
                )
                if evaluado["coste"] == opt_coste:
                    muestras_opt += 1

            if mejor_eval is None:
                mejor_eval = evaluado
            elif evaluado["factible"]:
                if not mejor_eval["factible"] or evaluado["coste"] < mejor_eval["coste"]:
                    mejor_eval = evaluado
            elif (
                not mejor_eval["factible"]
                and evaluado["violacion"] < mejor_eval["violacion"]
            ):
                mejor_eval = evaluado

        historial_starts.append({"optimo_bool": optimo_start})

    metricas = {
        "prob_optimo_muestras": muestras_opt / total_muestras if total_muestras else 0,
        "prob_optimo_starts": (
            sum(1 for h in historial_starts if h["optimo_bool"]) / starts
            if starts else 0
        ),
        "tasa_factibilidad_muestras": (
            muestras_fact / total_muestras if total_muestras else 0
        ),
        "ratio_medio_factibles": (
            statistics.mean(ratios_factibles) if ratios_factibles else 0
        ),
        "total_muestras": total_muestras,
        "starts": starts,
        "sqa_beta": beta,
        "sqa_gamma": gamma,
        "sqa_trotter": trotter,
        "sqa_num_sweeps": num_sweeps,
    }

    return mejor_eval, metricas, historial_starts

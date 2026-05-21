from qiskit_optimization.algorithms import SlsqpOptimizer
from qiskit_optimization.algorithms import WarmStartQAOAOptimizer


def crear_presolver_warmstart():
    return SlsqpOptimizer(iter=200)


def crear_solver_warmstart(qaoa, epsilon=0.25):
    pre_solver = crear_presolver_warmstart()

    return WarmStartQAOAOptimizer(
        pre_solver=pre_solver,
        relax_for_pre_solver=True,
        qaoa=qaoa,
        epsilon=epsilon,
        num_initial_solutions=1,
    )

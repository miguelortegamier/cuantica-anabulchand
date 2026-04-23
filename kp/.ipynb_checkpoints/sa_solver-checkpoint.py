import dimod
from neal import SimulatedAnnealingSampler
from qiskit_optimization.converters import QuadraticProgramToQubo


def qp_to_qubo(qp):
    conv = QuadraticProgramToQubo()
    qubo = conv.convert(qp)

    Q = {}

    for var, coef in qubo.objective.linear.to_dict().items():
        Q[(var, var)] = coef

    for (i, j), coef in qubo.objective.quadratic.to_dict().items():
        Q[(i, j)] = coef

    return Q, qubo


def resolver_sa(qp, num_reads=100):
    Q, qubo = qp_to_qubo(qp)

    sampler = SimulatedAnnealingSampler()
    sampleset = sampler.sample_qubo(Q, num_reads=num_reads)

    return sampleset, qubo

from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit_aer.primitives import Sampler
import time


class TimedSampler(Sampler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tiempo_total = 0

    def run(self, *args, **kwargs):
        t0 = time.perf_counter()
        result = super().run(*args, **kwargs)
        t1 = time.perf_counter()
        self.tiempo_total += (t1 - t0)
        return result


def noise_model():
    noise_model = NoiseModel()

    error_1q = depolarizing_error(0.01, 1)
    error_2q = depolarizing_error(0.02, 2)

    noise_model.add_all_qubit_quantum_error(error_1q, ["rx", "ry", "rz"])
    noise_model.add_all_qubit_quantum_error(error_2q, ["cx"])

    return noise_model


def crear_sampler_con_ruido(shots, semilla, timed=True):
    modelo_ruido = noise_model()

    backend_options = {
        "noise_model": modelo_ruido,
        "basis_gates": modelo_ruido.basis_gates,
        "seed_simulator": semilla,
    }

    run_options = {
        "shots": shots,
        "seed": semilla,
    }

    if timed:
        return TimedSampler(
            backend_options=backend_options,
            run_options=run_options,
        )
    else:
        return Sampler(
            backend_options=backend_options,
            run_options=run_options,
        )

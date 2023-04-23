import ray

import matlab.engine
import logging

logging.getLogger


@ray.remote(num_cpus=2, resources={"matlab": 1})
def run_simulator():
    from matlab_example.core import InputSignal
    from matlab_example.simulator import SimulinkModel
    import os
    import pathlib

    TIME_HORIZON = 30

    eng = matlab.engine.start_matlab()
    eng.cd(os.getcwd())
    eng.addpath(str((pathlib.Path(__file__).parent / "simulators")))

    mdl = SimulinkModel(
        "Autotrans_shift",
        matlab_engine=eng,
        model_parameters = [],
        input_signals = [
            InputSignal("throttle", lb=0, ub=100, n_control_point=5),
            InputSignal("brake", lb=0, ub=100, n_control_point=5),
        ],
        output_variables = ["speed", "rpm", "gear"],
        time_horizon = TIME_HORIZON,
        time_step = 0.1,
    )

    default_val = mdl.create_default_valuation()
    trace = mdl.simulate(default_val)

    eng.exit()

    return trace


runtime_env = {
    "working_dir": "/home/ubuntu/project",
}

ray.init(runtime_env=runtime_env)

# Create an actor from this class.
results = ray.get([run_simulator.remote() for _ in range(2)])

for trace in results:
    print(trace.df)


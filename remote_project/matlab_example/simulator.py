from __future__ import annotations
import itertools
from typing import Any, List, Optional, Tuple

try:
    import matlab
except ImportError:
    _no_matlab = True
else:
    _no_matlab = False

import io
import logging

import numpy as np
import pandas as pd

from .core import InputSignal, Parameter, Valuation

logger = logging.getLogger(__name__)

class Trace:
    """A trace of a simulation result."""

    def __init__(
        self, time_steps: np.ndarray, values: List[np.ndarray], variables: List[str]
    ) -> None:
        """Initialize a trace.

        Args:
            time_steps: The time steps of the trace. A numpy array of shape (n, ).
            values: The list of the values of the output variables.
                Each element is a numpy array of shape (n, ).
            variables: The names of the output variables.
        """
        self._time_steps = time_steps
        self._values = values
        self._variables = variables

    @property
    def time_steps(self) -> np.ndarray:
        return self._time_steps

    @property
    def variables(self) -> List[str]:
        return self._variables

    @property
    def df(self) -> pd.DataFrame:
        """Return the trace as a pandas DataFrame."""
        return pd.DataFrame(
            data=np.column_stack(self._values),
            columns=self._variables,
            index=self._time_steps,
        )

    def __getitem__(self, key: str) -> np.ndarray:
        try:
            return self._values[self._variables.index(key)]
        except ValueError:
            raise ValueError(f"Variable {key} not found in trace.")

    def __setitem__(self, key: str, value: np.ndarray) -> None:
        raise ValueError("Cannot set value of a trace.")

    def __repr__(self) -> str:
        return self.df.__repr__()

class SimulinkModel:
    """A class for a Simulink model."""

    def __init__(
        self,
        name: str,
        *,
        matlab_engine: matlab.MatlabEngine,
        model_parameters: List[Parameter],
        input_signals: List[InputSignal],
        output_variables: List[str],
        time_horizon: float,
        time_step: Optional[float] = None,
        reset_time_horizon: bool = True,
    ) -> None:
        """Initialize a Simulink model.

        Args:
            name: The name of the model.
            model_parameters: The parameters of the model
                (not including the parameters for the control points in input_signals).
            input_signals: The input signals of the model.
            output_variables: The name of output variables of the model.
            time_horizon: The default time horizon of the simulation.
            time_step: The size of the time step of the simulation.
        """
        self._name = name
        self._matlab_engine = matlab_engine
        self._model_parameters = model_parameters
        self._input_signals = input_signals
        self._output_variables = output_variables
        self._time_horizon = time_horizon
        self._time_step = 0.1 if time_step is None else time_step
        if reset_time_horizon:
            for signal in self._input_signals:
                signal.time_horizon = self._time_horizon
        # flatten
        parameters_for_input_signals = itertools.chain.from_iterable(
            [signal.control_parameters for signal in self._input_signals]
        )
        self._control_parameters = [
            *self._model_parameters,
            *parameters_for_input_signals,
        ]
        self._default_valuation = Valuation(
            self._control_parameters, [p.default for p in self._control_parameters]
        )

        self._opts = self._matlab_engine.simget(self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def model_parameters(self) -> List[Parameter]:
        return self._model_parameters

    @property
    def input_signals(self) -> List[InputSignal]:
        return self._input_signals

    @property
    def output_variables(self) -> List[str]:
        return self._output_variables

    @property
    def control_parameters(self) -> List[Parameter]:
        return self._control_parameters

    def __repr__(self) -> str:
        return (
            f"SimulinkModel(name={self._name}, "
            f"model_parameters={self._model_parameters}, "
            f"input_signals={self._input_signals}, "
            f"output_variables={self._output_variables}, "
            f"time_horizon={self._time_horizon}, time_step={self._time_step})"
        )

    def create_default_valuation(self) -> Valuation:
        """Create the default valuation of the parameters.
        The default valuation is guaranteed to be valid.

        Returns:
            The default valuation.
        """
        return self._default_valuation.clone()

    def get_input_signal(self, name: str) -> InputSignal:
        """Get an input signal by name.

        Args:
            name: The name of the input signal.

        Returns:
            The input signal.
        """
        for signal in self._input_signals:
            if signal.name == name:
                return signal
        raise ValueError(f"Input signal {name} not found.")

    def simulate(
        self, valuation: Valuation, time_horizon: Optional[float] = None
    ) -> Trace:
        """Simulate the model.

        Args:
            valuation: A valuation of the parameters of the model.
            time_horizon: The time horizon of the simulation.

        Returns:
            The simulation result.
        """
        if time_horizon is None:
            time_horizon = self._time_horizon

        signal_times = np.linspace(
            0, time_horizon, int(time_horizon // self._time_step)
        )
        full_valuation = self._default_valuation.patch(valuation)
        signal_values = [
            signal.sample(
                full_valuation.filter(signal.control_parameters), signal_times
            )
            for signal in self._input_signals
        ]

        result_time_steps, data = self._simulate(
            matlab.double([0, time_horizon]),
            matlab.double(np.vstack([signal_times, *signal_values]).T),
        )

        return Trace(
            time_steps=np.array(result_time_steps).flatten(),
            values=list(np.array(data).T),
            variables=self._output_variables,
        )

    def _simulate(
        self, sim_t: matlab.double, model_input: matlab.double
    ) -> Tuple[matlab.double, matlab.double]:
        engine_stdout = io.StringIO()
        try:
            result_time_steps, opts, data = self._matlab_engine.sim(
                self._name,
                sim_t,
                self._opts,
                model_input,
                nargout=len(self._output_variables),
                stdout=engine_stdout,
            )
        except (
            matlab.engine.MatlabExecutionError,
            matlab.engine.RejectedExecutionError,
        ) as e:
            raise RuntimeError("Matlab failed to execute simulation.") from e
        finally:
            if engine_stdout.getvalue():
                logger.debug("[MATLAB stdout] " + engine_stdout.getvalue())
        return result_time_steps, data

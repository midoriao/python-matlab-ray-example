from typing import List, Optional, Union
import logging
from .parameter import RangeParameter
import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from .valuation import Valuation

logger = logging.getLogger(__name__)


class InputSignal:
    """A class for a timed input signal, which is a piecewise constant function."""

    def __init__(
        self,
        name: str,
        lb: float,
        ub: float,
        n_control_point: int = 1,
        *,
        time_horizon: float = 10.0,
    ) -> None:
        assert lb <= ub
        self._name = name
        self._lb = lb
        self._ub = ub
        self._n_control_points = n_control_point
        self._time_horizon = time_horizon
        self._control_parameters = self._induce_control_parameters()

    @property
    def name(self) -> str:
        return self._name

    @property
    def lb(self) -> float:
        return self._lb

    @property
    def ub(self) -> float:
        return self._ub

    @property
    def n_control_points(self) -> int:
        return self._n_control_points

    @n_control_points.setter
    def n_control_points(self, n_control_points: int) -> None:
        self._n_control_points = n_control_points
        self._control_parameters = self._induce_control_parameters()

    @property
    def time_horizon(self) -> float:
        return self._time_horizon

    @time_horizon.setter
    def time_horizon(self, time_horizon: float) -> None:
        self._time_horizon = time_horizon
        self._control_parameters = self._induce_control_parameters()

    @property
    def control_parameters(self) -> List[RangeParameter]:
        """Return the control parameters of the signal.
        The control parameter is named like {parameter_u0}"""
        return self._control_parameters

    @property
    def time_points(self) -> List[float]:
        """Return the time points of the control points.
        With `n` of control points, the value of the signal is specified at
        `t_0=0, t_1=T/n, ..., t_{n-1}=T*(n - 1)/n`."""
        return [
            self._time_horizon * i / self._n_control_points
            for i in range(self._n_control_points)
        ]

    def _induce_control_parameters(self) -> List[RangeParameter]:
        values = [
            RangeParameter(name=f"{self._name}_u{i}", lb=self._lb, ub=self._ub)
            for i in range(self._n_control_points)
        ]
        return values

    def sample(
        self, valuation: Valuation, time_steps: Optional[ArrayLike] = None
    ) -> np.ndarray:
        """Return the values of the signal at the given time steps.
        The value of the signal is piecewise-constant, specified with the valuation.

        Args:
            valuation: A valuation of the parametrized piecewise-constant signal.
            time_steps: The time steps at which the values are sampled.
                If `None`, the values are sampled at the control points (no resampling).

        Returns:
            The values of the signal at the given time steps.
        """
        if time_steps is None:
            time_steps = np.array(self.time_points)

        values = np.array(
            [
                valuation[self.control_parameters[i].name]
                for i in range(self._n_control_points)
            ]
        )

        idx = np.searchsorted(self.time_points, time_steps)
        return values[idx - 1]

    def __repr__(self):
        return (
            f"Signal(name={self._name}, lb={self._lb}, ub={self._ub}, "
            f"n_control_points={self._n_control_points}, "
            f"time_horizon={self._time_horizon})"
        )

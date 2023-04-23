
from __future__ import annotations

import pandas as pd
from typing import List, Optional, Sequence, Union

from .parameter import Parameter


class Valuation:
    """A class for a valuation of parameters."""

    def __init__(
        self, parameters: Sequence[Parameter], values: Optional[Sequence[float]] = None
    ) -> None:
        """Initialize a valuation.

        Args:
            parameters: A list of parameters.
            values: A list of values. The length and order of the values must match
            the ones of the parameters.
        """
        self._parameters = list(parameters)
        if values is None:
            values = [p.default for p in parameters]
        self._values = list(values)
        assert len(parameters) == len(values)

    @property
    def parameters(self) -> List[Parameter]:
        return self._parameters

    @property
    def values(self) -> List[float]:
        return self._values

    @property
    def names(self) -> List[str]:
        return [p.name for p in self._parameters]

    @property
    def df(self) -> pd.DataFrame:
        return pd.DataFrame(self.values, index=self.names).T

    def get_parameter(self, name: str) -> Parameter:
        """Get a parameter by name."""
        idx = self.names.index(name)
        return self._parameters[idx]

    def __getitem__(self, name: Union[str, Parameter]) -> float:
        if isinstance(name, Parameter):
            name = name.name
        assert isinstance(name, str)
        idx = self.names.index(name)
        return self._values[idx]

    def __setitem__(self, name: Union[str, Parameter], value: float) -> None:
        if isinstance(name, Parameter):
            name = name.name
        assert isinstance(name, str)
        idx = self.names.index(name)
        if self._parameters[idx].validate(value):
            self._values[idx] = value
        else:
            raise ValueError(f"Invalid value for parameter {name}: {value}")

    def filter(self, params: Sequence[Parameter]) -> Valuation:
        """Get a valuation that contains only the parameters in the list.

        Args:
            params: A list of parameters.

        Returns:
            A valuation that contains only the parameters in the list.
        """
        values = [self[p] for p in params]
        return Valuation(list(params), values)

    def is_valid(self) -> bool:
        """Check if the valuation is valid.

        Returns:
            True if the valuation is valid, False otherwise.
        """
        return all(p.validate(v) for p, v in zip(self._parameters, self._values))

    def patch(self, other: Valuation) -> Valuation:
        """Create a new valuation whose values are overwritten by the other valuation.

        Args:
            other: The other valuation. The parameters in the other valuation
                must be a subset of the parameters in this valuation.

        Returns:
            A new valuation
        """
        patched = self.clone()
        for p, v in zip(other._parameters, other._values):
            patched[p] = v
        return patched

    def clone(self) -> Valuation:
        return Valuation(self._parameters, self._values.copy())

    def __str__(self) -> str:
        maps = ", ".join(
            f"{p.name}={v}" for p, v in zip(self._parameters, self._values)
        )
        return f"[{maps}]"

    def __repr__(self):
        return f"Valuation(parameters={self._parameters}, values={self._values})"

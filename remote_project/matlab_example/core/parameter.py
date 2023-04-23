from __future__ import annotations

from typing import Optional, Tuple


class Parameter:
    """An abstract class for a parameter."""

    def __init__(self, name: str) -> None:
        """Initialize a parameter.

        Args:
            name: The name of the parameter.
        """
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def default(self) -> float:
        raise NotImplementedError()

    def validate(self, value: float) -> bool:
        """Validate a value of the parameter.

        Args:
            value: The value to validate.

        Returns:
            True if the value is valid, False otherwise.
        """
        raise NotImplementedError()

    def __repr__(self):
        return f"Parameter(name={self._name})"


class StaticParameter(Parameter):
    """A class for a parameter that is fixed to a value."""

    def __init__(self, name: str, value: float):
        """Initialize a static parameter.

        Args:
            name: The name of the parameter.
            value: The value of the parameter.
        """
        super().__init__(name)
        self._value = value

    @property
    def value(self) -> float:
        return self._value

    @property
    def default(self) -> float:
        return self._value

    def validate(self, value: float) -> bool:
        return value == self._value

    def __repr__(self):
        return f"StaticParameter(name={self._name}, value={self._value})"


class RangeParameter(Parameter):
    """A class for a parameter that has a range."""

    def __init__(
        self, name: str, lb: float, ub: float, default: Optional[float] = None
    ):
        """Initialize a range parameter.

        Args:
            name: The name of the parameter.
            lb: The lower bound of the parameter.
            ub: The upper bound of the parameter.
            default: The default value of the parameter.
        """
        super().__init__(name)
        assert lb <= ub
        self._lb = lb
        self._ub = ub
        self._default = default if default is not None else (lb + ub) / 2

    @property
    def lb(self) -> float:
        return self._lb

    @property
    def ub(self) -> float:
        return self._ub

    @property
    def bounds(self) -> Tuple[float, float]:
        return self._lb, self._ub

    @property
    def default(self) -> float:
        return self._default

    def validate(self, value: float) -> bool:
        return self._lb <= value <= self._ub

    def __repr__(self):
        return f"RangeParameter(name={self._name}, lb={self._lb}, ub={self._ub})"


__all__ = [
    "Parameter",
    "StaticParameter",
    "RangeParameter",
]

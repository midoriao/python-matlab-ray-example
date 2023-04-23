import numpy as np
import pandas as pd
from typing import List, Optional

class ObservationStore:
    def __init__(self, names: List[str]):
        self._X: List[np.ndarray] = []
        self._fX: List[np.ndarray] = []
        self._names = names
        self._current_best = np.inf

    def register(self, x: np.ndarray, fx: np.ndarray) -> None:
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(fx, np.ndarray):
            fx = np.array(fx)
        assert x.ndim == 2
        assert fx.ndim == 2
        assert len(x) == len(fx)

        for i in range(len(x)):
            self._X.append(x[i])
            self._fX.append(fx[i])
            if fx[i] < self._current_best:
                self._current_best = fx[i]

    def stack_all(self):
        x_np = np.array(self._X)
        fx_np = np.array(self._fX)
        return np.hstack([x_np, fx_np])

    @property
    def df(self):
        return pd.DataFrame(
            self.stack_all(),
            columns=[*self._names, 'fx']
        )

    @property
    def min(self) -> float:
        if len(self._fX) == 0:
            return np.inf
        else:
            return np.min(self._fX)

    @property
    def min_x(self) -> Optional[np.ndarray]:
        if len(self._fX) == 0:
            return None
        else:
            return self.X[np.array(self.fX).ravel().argmin().item()]

    @property
    def current_best(self):
        return self._current_best

    @property
    def num(self):
        return len(self._X)

    @property
    def X(self) -> np.ndarray:
        return np.array(self._X)

    @property
    def fX(self) -> np.ndarray:
        return np.array(self._fX)

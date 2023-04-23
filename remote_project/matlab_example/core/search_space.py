import numpy as np
import pandas as pd

def to_unit_cube(x, lb, ub):
    """Project to [0, 1]^d from hypercube with bounds lb and ub"""
    assert np.all(lb < ub) and lb.ndim == 1 and ub.ndim == 1 and x.ndim == 2
    xx = (x - lb) / (ub - lb)
    return xx


def from_unit_cube(x, lb, ub):
    """Project from [0, 1]^d to hypercube with bounds lb and ub"""
    assert np.all(lb < ub) and lb.ndim == 1 and ub.ndim == 1 and x.ndim == 2
    xx = x * (ub - lb) + lb
    return xx


def latin_hypercube(n_pts, dim):
    """Basic Latin hypercube implementation with center perturbation."""
    X = np.zeros((n_pts, dim))
    centers = (1.0 + 2.0 * np.arange(0.0, n_pts)) / float(2 * n_pts)
    for i in range(dim):  # Shuffle the center locataions for each dimension.
        X[:, i] = centers[np.random.permutation(n_pts)]

    # Add some perturbations within each box
    pert = np.random.uniform(-1.0, 1.0, (n_pts, dim)) / float(2 * n_pts)
    X += pert
    return X


class SearchSpace:
    """The Euclidean space.

    Parameters
    ----------
    """
    def __init__(
        self,
        lb,
        ub) -> None:
        assert lb.ndim == 1 and ub.ndim == 1
        assert len(lb) == len(ub)
        assert np.all(ub > lb)
        self.dim = len(lb)
        self.lb = lb
        self.ub = ub
        self.parameters = [
            {"name": f"x{i}", "lb": lb[i], "ub": ub[i]}
            for i in range(self.dim)
        ]

    @property
    def parameter_names(self):
        return [p["name"] for p in self.parameters]

    def to_dataframe(self, X: np.ndarray) -> pd.DataFrame:
        return pd.DataFrame(X, columns=self.parameter_names)

    def from_unit_cube(self, X: np.ndarray) -> np.ndarray:
        """Convert points from the unit cube to the search space.
        Parameters
        ----------
        X : Points in the unit cube, numpy.array, shape (n_samples, dim).
        Returns
        -------
        X : Points in the search space, numpy.array, shape (n_samples, dim).
        """
        return from_unit_cube(X, self.lb, self.ub)

    def to_unit_cube(self, X: np.ndarray) -> np.ndarray:
        """Convert points from the search space to the unit cube.
        Parameters
        ----------
        X : Points in the search space, numpy.array, shape (n_samples, dim).
        Returns
        -------
        X : Points in the unit cube, numpy.array, shape (n_samples, dim).
        """
        return to_unit_cube(X, self.lb, self.ub)

    def latin_hypercube(self, n_samples: int) -> np.ndarray:
        """Generate Latin hypercube samples.
        Parameters
        ----------
        n_samples : int
            The number of samples.
        Returns
        -------
        X : Samples, numpy.array, shape (n_samples, dim).
        """
        X = latin_hypercube(n_samples, self.dim)
        return self.from_unit_cube(X)

    def contains(self, X: np.ndarray) -> np.bool_:
        """Check if points are in the search space.
        Parameters
        ----------
        X : Points in the search space, numpy.array, shape (n_samples, dim).
        Returns
        -------
        bool : True if all points are in the search space.
        """
        return np.all(self.lb <= X) and np.all(X <= self.ub)

    def __repr__(self):
        return f"SearchSpace(lb={self.lb}, ub={self.ub})"

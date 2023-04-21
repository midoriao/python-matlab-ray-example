import matlab
import matlab.engine
from typing import Optional
import logging

logger = logging.getLogger(__name__)

_engine: Optional[matlab.engine.MatlabEngine] = None
_n_connection = 0


def has_no_engine_connection() -> bool:
    return _engine is None

def get_matlab_engine() -> matlab.engine.MatlabEngine:
    if _engine is None:
        raise RuntimeError("Engine not connected. Please use `with connect_matlab():.`")
    else:
        return _engine


def reserve_connection(session_name: Optional[str] = None) -> matlab.engine.MatlabEngine:
    global _engine
    global _n_connection

    if session_name is None:
        logger.warn("No session name provided. If multiple MATLAB processes are running, "
                "the connection may be to an unexpected session.")

    _n_connection += 1
    if _engine is not None:
        logger.warn(f"Multiple connection to Matlab ({_n_connection - 1} -> {_n_connection}).")
    else:
        try:
            _engine = matlab.engine.connect_matlab(session_name)
        finally:
            if _engine is None:
                raise RuntimeError("Failed to connect to Matlab.")
    return _engine


def release_connection():
    global _engine
    global _n_connection

    _n_connection -= 1
    if _n_connection > 0:
        logger.warn(f"Exiting multiple Matlab connections ({_n_connection + 1} -> {_n_connection}.")
    elif _n_connection < 0:
        raise RuntimeError("Resource already released.")
    else:
        _engine.exit()
        _engine = None

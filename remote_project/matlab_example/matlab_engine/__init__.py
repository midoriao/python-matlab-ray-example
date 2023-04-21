import logging
from typing import Optional

try:
    import matlab
    import matlab.engine
except ImportError:
    _no_matlab = True
else:
    _no_matlab = False

from .sessions import find_matlab, MatlabEngineManager, is_available_matlab
from .context import connection
from .global_engine import get_matlab_engine

logger = logging.getLogger(__name__)

if _no_matlab:
    logger.warning("Matlab is not installed. Connection to Matlab cannot be used.")

__all__ = [
    "get_matlab_engine",
    "connection",
    "MatlabEngineManager",
    "is_available_matlab",
    "find_matlab",
]

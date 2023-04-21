from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Optional


from .global_engine import reserve_connection, release_connection

logger = logging.getLogger(__name__)


@contextmanager
def connection(session_name: Optional[str] = None) -> matlab.engine.MatlabEngine:
    """Connect a shared Matlab session.
    Session name must be one of the names returned by `find_matlab()`.

    Args:
        session_name: Name of the Matlab session.
    """
    if session_name is None:
        logger.info(f"Connecting to Matlab engine...")
    else:
        logger.info(f"Connecting to Matlab engine {session_name}...")

    engine = reserve_connection(session_name)
    logger.info("Matlab engine connected.")
    try:
        engine.cd(os.getcwd())
        yield engine
    finally:
        if session_name is None:
            logger.info("Disconnecting from Matlab engine...")
        else:
            logger.info(f"Disconnecting from Matlab engine {session_name}...")
        release_connection()
        logger.info("Matlab engine disconnected.")

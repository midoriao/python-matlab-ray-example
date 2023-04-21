import logging
from typing import List, Union, Optional
import os

import matlab.engine
from . import context
from .global_engine import has_no_engine_connection

logger = logging.getLogger(__name__)


def find_matlab() -> List[str]:
    """Find all local MATLAB sessions."""

    return matlab.engine.find_matlab()


class MatlabEngineManager:
    """A class for managing multiple MATLAB sessions.
    In MATLAB API, if multiple connections are made to the same MATLAB session,
    the session will be broken. This class is used to reserve a MATLAB session
    and provides safe way to get a connection to the engine.

    The term *engine* is distinct from *session*. An engine is an (API) object
    that proxies connection to an MATLAB session. A session is a MATLAB process itself.

    Do not multiplly instantiate this class in the same python process.
    """
    def __init__(self, pid_dir: Union[str, os.PathLike]) -> None:
        self._pid_dir = pid_dir
        self._matlab_name = None
        if not os.path.isdir(self._pid_dir):
            raise ValueError(f"Path {self._pid_dir} does not exist or is not a directory.")

    def get_available_matlab(self) -> str:
        """Get one MATLAB session that is not currently in use.
        The status of a MATLAB session is determined by the existence of a file
        named after the PID of the MATLAB session in the given directory.
        Raises an exception if no MATLAB session is available.

        Returns:
            Name of the MATLAB session.
        """
        for matlab_name in find_matlab():
            if is_available_matlab(matlab_name, self._pid_dir):
                logger.info(f"Available session {matlab_name} found.")
                return matlab_name
            else:
                logger.info(f"Session {matlab_name} is not available.")
        raise RuntimeError("No available MATLAB session found.")

    def use_shared_matlab_session(self, matlab_name: Optional[str] = None) -> None:
        """Reserve a MATLAB session that is not currently in use.
        Raises an exception if no MATLAB session is available.

        Args:
            matlab_name: Name of the MATLAB session. If None, the first available
                MATLAB session is used.
        """
        if self._matlab_name is not None:
            raise RuntimeError("A MATLAB session is already reserved by this instance.")
        if matlab_name is None:
            matlab_name = self.get_available_matlab()
        reserve_matlab(matlab_name, self._pid_dir)
        self._matlab_name = matlab_name

    def connection(self):
        """Get a connection to the MATLAB engine that handles the session
         reserved by this manager."""
        return context.connection(self._matlab_name)

    def release(self) -> None:
        """Release the MATLAB session reserved by this manager."""
        if not has_no_engine_connection():
            logger.warning("Releasing MATLAB session, but there are still active MATLAB engine connections. ")

        if self._matlab_name is None:
            logger.info("No MATLAB session reserved by this instance. Skipping release.")
            return
            
        release_matlab(self._matlab_name, self._pid_dir)
        self._matlab_name = None

    def __del__(self) -> None:
        self.release()

    @property
    def matlab_name(self) -> Optional[str]:
        """Name of the MATLAB session reserved by this manager."""
        return self._matlab_name


def reserve_matlab(matlab_name: str, pid_dir: Union[str, os.PathLike]) -> None:
    """Reserve a MATLAB session by PID file.
    Raises an exception if the MATLAB session is already reserved.

    Args:
        matlab_name: Name of the MATLAB session.
        pid_dir: Directory where PID files are stored.
    """
    try:
        target_pid = int(matlab_name.split("_")[-1])
    except ValueError as e:
        raise ValueError(f"Invalid MATLAB session name: {matlab_name}."
            "Please check the running matlab is launched properly.") from e

    if not is_available_matlab(matlab_name, pid_dir):
        raise RuntimeError(f"MATLAB session {matlab_name} is already reserved.")

    pid_file = os.path.join(pid_dir, f"{matlab_name}.pid")
    with open(pid_file, "w") as f:
        f.write(str(target_pid))


def release_matlab(matlab_name: str, pid_dir: Union[str, os.PathLike]) -> None:
    """Release a MATLAB session.
    The status of a MATLAB session is determined by the existence of a file
    named after the PID of the MATLAB session in the given directory.
    Raises an exception if the MATLAB session is not reserved.

    Args:
        matlab_name: Name of the MATLAB session.
        pid_dir: Directory where PID files are stored.
    """
    if is_available_matlab(matlab_name, pid_dir):
        raise RuntimeError(f"Releasing non-reserved MATLAB session {matlab_name}.")

    pid_file = os.path.join(pid_dir, f"{matlab_name}.pid")
    os.remove(pid_file)


def is_available_matlab(matlab_name: str, pid_dir: Union[str, os.PathLike]) -> bool:
    """Check if a MATLAB session is not reserved.
    The status of a MATLAB session is determined by the existence of a file
    named after the PID of the MATLAB session in the given directory.

    Args:
        matlab_name: Name of the MATLAB session.
        pid_dir: Directory where PID files are stored.

    Returns:
        True if the MATLAB session is available.
    """
    pid_path = os.path.join(pid_dir, f"{matlab_name}.pid")
    if not os.path.exists(pid_path):
        return True

    # Consistency check
    with open(pid_path, "r") as f:
        content_pid = int(f.read())
    if _is_process_dead(content_pid):
        logger.warning(f"MATLAB session {matlab_name} is reserved but seems to be dead. Inconsistency in session management.")

    return False

def _is_process_dead(pid: int) -> bool:
    """Check if a process is dead."""
    try:
        os.kill(pid, 0)
    except OSError:
        return True
    else:
        return False

import os
import matlab
import matlab.engine
import pathlib
import os
import logging

logging.basicConfig(level=logging.DEBUG)

from matlab_example.matlab_engine import MatlabEngineManager, find_matlab, is_available_matlab

pid_dir = '/tmp/matlab_pids'

if not os.path.isdir(pid_dir):
    os.mkdir(pid_dir)

mem = MatlabEngineManager(pid_dir)

print(f"All: {find_matlab()}")
availables = [m for m in find_matlab() if is_available_matlab(m, pid_dir)]
print(f"Available: {availables}")

mem.use_shared_matlab_session()

print("Using " + mem.matlab_name)

with mem.connection() as eng:
    eng.cd(os.getcwd())
    eng.addpath(str(pathlib.Path(__file__).parent.resolve()))
    opts = eng.simget("Autotrans_shift")



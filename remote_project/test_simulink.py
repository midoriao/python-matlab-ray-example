import os
import matlab
import matlab.engine
import pathlib

CREATE_MATLAB = True

if CREATE_MATLAB:
    print("CREATE_MATLAB=1. Using new MATLAB session.")
    eng = matlab.engine.start_matlab()
    print("Engine started.")
else:
    sessions = matlab.engine.find_matlab()
    if len(sessions) == 0:
        print("No MATLAB session found.")
        exit()
    print(f"Using MATLAB session: {sessions[0]}")
    eng = matlab.engine.connect_matlab(sessions[0])

eng.cd(os.getcwd())
eng.addpath(str((pathlib.Path(__file__).parent / "simulators")))
    
opts = eng.simget("Autotrans_shift")
print(opts)
eng.simset(opts, "SaveFormat", "Array")
timestamps, _, data = eng.sim("Autotrans_shift", matlab.double([0, 10]), opts, nargout=3)
print(timestamps)
print(data)

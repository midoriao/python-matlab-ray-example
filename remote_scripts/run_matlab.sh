#!/bin/bash

HOSTNAME=$(hostname)

MATLAB_ENGINE_PREFIX=MAT_${HOSTNAME//[-.]/_}  # e.g., MAT_ip_10_0_0_10
DISPLAY=:1 matlab -r "matlab.engine.shareEngine(compose(\"${MATLAB_ENGINE_PREFIX}_%d\", feature('getpid')))"


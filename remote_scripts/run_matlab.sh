#!/bin/bash

echo "matlab" | vncpasswd -f > ~/.vnc/passwd  # TODO: password should be an env var
ln -s /usr/bin/mate-session ~/.vnc/xstartup
vncserver :1
websockify --web=/usr/share/novnc 6080 localhost:5901 &  # 5901 is the default VNC port

DISPLAY=:1 matlab -r "matlab.engine.shareEngine"

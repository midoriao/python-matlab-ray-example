#!/bin/bash

sudo apt-get -qq update
sudo apt-get install -qq python-is-python3
sudo apt-get install -qq python3-pip
sudo apt-get install -qq tightvncserver autocutsel
sudo snap install novnc

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

which ray || pip install -q -U "ray[default] @ https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-3.0.0.dev0-cp38-cp38-manylinux2014_x86_64.whl"
pip install -q 'boto3>=1.4.8'

LD_LIBRARY_PATH=/usr/local/matlab/bin/glnxa64 pip install "matlabengine==9.13.4"

echo "matlab" | vncpasswd -f > ~/.vnc/passwd  # TODO: password should be an env var
chmod 600 ~/.vnc/passwd
cat - << EOS > ~/.vnc/xstartup
#!/bin/sh
export XKL_XMODMAP_DISABLE=1
autocutsel -fork
exec /usr/bin/mate-session
EOS
chmod +x ~/.vnc/xstartup

vncserver :1 || echo "VNC server already running. Continuing..."

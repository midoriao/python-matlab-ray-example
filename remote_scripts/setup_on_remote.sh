#!/bin/bash

sudo apt-get -qq update
sudo apt-get install -qq python-is-python3
sudo apt-get install -qq python3-pip

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

which ray || pip install -q -U "ray[default] @ https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-3.0.0.dev0-cp38-cp38-manylinux2014_x86_64.whl"
pip install -q 'boto3>=1.4.8'

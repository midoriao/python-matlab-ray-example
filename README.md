# python-matlab-ray-example

This is a simple example of how to call a MATLAB function in remote AWS instance from Python using the [Ray](https://ray.io/) library.

## Requirements

- Python 3.8
- [Poetry](https://python-poetry.org/)
- MATLAB 2022b and linked license
- aws cli

All of the above can be set up using [devcontainer](https://code.visualstudio.com/docs/remote/containers) in VSCode.
I strongly recommend using it to avoid struggles (especially, [ray may not work on M1 mac](https://github.com/ray-project/ray/issues/20084)).

## Environment-specific parameters

The `ray_matlab_config.yaml` file contains the environment-specific parameters.
If the hard-coded values are not suitable for your environment, change them in the file.

- AWS region (default: ap-northeast-1)
- AMI id (default: [MATLAB 2022b for ap-northeast-1](https://github.com/mathworks-ref-arch/matlab-on-aws/blob/master/releases/R2022b/README.md))
- Resource tags (default: BudgetGroup=sota-falsification)

## Installation

Install the python dependencies:

```bash
poetry install
poetry shell  # enter the virtual environment
```

Configure the AWS credentials.
See [Ray documentation](https://docs.ray.io/en/latest/cluster/vms/user-guides/launching-clusters/aws.html) for the instructions.

## On MATLAB licensing

Seemingly there are two way of MATLAB licensing in cloud platform.

1. By default, MATLAB on AWS uses [*Login Named User*](https://www.mathworks.com/matlabcentral/answers/168441-what-is-login-named-user-and-how-can-i-use-it) (LNU) option to authenticate you.
LNU assigns your MATLAB account to each MATLAB session, so lincense management is not locked to your remote host and respects portability of runtime environment.
The limitation of LNU is that MATLAB asks your account information at each time. You cannnot start MATLAB session without GUI authentication prompt and thereby from `matlab.engine.start_matlab()` Python API.
<https://stackoverflow.com/questions/67426665/issue-running-matlab-in-aws-via-terminal>

2. The other option is linking your license with your remote host. This is the same way of licensing in local development.
Following this way you can freely launch matlab session in the licensed host machine. 
The easiest way to enable this option is just run `/usr/local/matlab/bin/activate_matlab.sh` and select your lincense number to consume.
Do not forget to run `/usr/local/matlab/bin/deactivate_matlab.sh` before disposing your remote machine.

Currently the instruction below intends the way of using LNU (I'll update it later).


## Usage

Create a cluster:

```bash
ray up ray_matlab_config.yaml
```

Try a remote call:

```bash
ray submit ray_matlab_config.yaml ./describe_tags.py
```

Open the MATLAB window in headless VNC server:

```bash
ray exec ray_matlab_config.yaml run_matlab.sh --tmux # Session is persistent in tmux
```

Connect to the VNC session via <http://localhost:6080/vnc.html>.

```bash
ray exec ray_matlab_config.yaml --port-forward 6080 'novnc --listen 6080 --vnc localhost:5901'  # 5901 is the default VNC port
```

After the MATLAB is launched (it may take a few minutes), follow the instructions in the MATLAB window to enable your license. You may see `matlab.engine.shareEngine` is already executed in the script window, so the engine is available from Python.

Matlab setup is done. Ctrl+C to terminate your remote VNC connection.
Please note that VNC session itself is persistent and MATLAB window MUST keep running for Python connection.
**DO NOT close the MATLAB window** and leave it open.

After all, you can remotely execute Python scripts that uses MATLAB engine:

```shell-session
$ ray submit ray_matlab_config.yaml ./find_matlab.py
('MAT_ip_100_00_00_100_2456')

$ ray rsync-up ray_matlab_config.yaml ./remote_project /home/ubuntu/project && ray exec ray_matlab_config.yaml 'python project/test_simulink.py'  # Initial call of simulink may take minutes
Using MATLAB SESSION: MAT_ip_100_00_00_100_2456
{'AbsTol': 1e-06, ...}
```

You can view the ray dashboard at <http://localhost:8265>.

```bash
ray dashboard ray_matlab_config.yaml
```

Shutdown the cluster:

```bash
ray down ray_matlab_config.yaml
```

REMARK: The `ray down` command does not terminate the EC2 instances.
You need to manually terminate the instances in the AWS console.

```bash
aws ec2 terminate-instances --instance-ids <instance-id>
```

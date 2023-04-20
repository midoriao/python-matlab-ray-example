# python-matlab-ray-example

This is a simple example of how to call a MATLAB function in remote AWS instance from Python using the [Ray](https://ray.io/) library.

## Requirements

- Python 3.10
- [Poetry](https://python-poetry.org/)

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

## Usage

Create a cluster:

```bash
ray up ray_matlab_config.yaml
```

Try a remote call:

```bash
ray submit ray_matlab_config.yaml ./describe_tags.py
```

Open the MATLAB GUI via web browser:

```bash
ray exec ray_matlab_config.yaml scripts/run_matlab.sh --tmux
ray attach ray_matlab_config.yaml --port-forward 6080  # Just for port-forwarding purpose
```

Then you can see the remote desktop in <http://localhost:6080/vnc.html>.
After the MATLAB is launched (it may take a few minutes), follow the instructions in the MATLAB window to enable your license. `matlab.engine.shareEngine` is already called in the script to make the engine available to be called from Python. Please leave the MATLAB window open.

You can remotely execute Python scripts that uses MATLAB engine:

```bash
ray submit ray_matlab_config.yaml ./test_matlab.py
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

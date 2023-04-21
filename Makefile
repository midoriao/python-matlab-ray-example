RAY_CONF := ray_matlab_config.yaml

.PHONY: all
all: install up test

.PHONY: install
install: pyproject.toml
	poetry install

.PHONY: clean
clean: down
	rm -rf .venv

.PHONY: up
up:
	poetry run ray up -y $(RAY_CONF)

.PHONY: down
down:
	poetry run ray down -y $(RAY_CONF)

.PHONY: attach
attach:
	poetry run ray attach $(RAY_CONF) --tmux

.PHONY: vnc-connection
vnc-connection:
	poetry run ray exec $(RAY_CONF) --port-forward 6080 'novnc --listen 6080 --vnc localhost:5901'

.PHONY: new-matlab
new-matlab:
	@echo "Please enter your credentials via <http://localhost:6080/vnc.html>."
	poetry run ray exec $(RAY_CONF) run_matlab.sh --tmux
	$(MAKE) vnc-connection

.PHONY: test
test:
	poetry run ray submit $(RAY_CONF) ./describe_tags.py

.PHONY: instance-ids
instance-ids:
	aws ec2 describe-instances --filters "Name=instance-state-name,Values=stopped" "Name=tag:ray-cluster-name,Values=example-ray-cluster" --query "Reservations[].Instances[].InstanceId" --output text

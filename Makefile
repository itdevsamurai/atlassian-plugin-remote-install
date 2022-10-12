# .DEFAULT_GOAL := req

all-dep-actions:
	@pip install pip-tools
	@make req
	@make req-dev
	@make install-req
	@make install-req-dev

install-req:
	@pip install -r requirements.txt
install-req-dev:
	@pip install -r dev-requirements.txt

req:
	@pip install pip-tools
	@pip-compile -o requirements.txt pyproject.toml
req-dev:
	@pip install pip-tools
	@pip-compile --extra=dev --output-file=dev-requirements.txt pyproject.toml
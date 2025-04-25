SHELL = /usr/bin/env bash -xeuo pipefail

format:
	poetry run ruff check --select I --fix src/
	poetry run ruff format src/

update-failed:
	poetry run python src/set_failed_state.py

publish-finish-deploy:
	poetry run python src/publish/fnish_deploy/finish_deploy.py

generate-complete-generate:
	poetry run python src/generate/complete_generate.py


.PHONY: \
	format \
	update-failed \
	publish-finish-deploy \
	generate-complete-generate

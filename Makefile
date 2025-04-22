SHELL = /usr/bin/env bash -xeuo pipefail

format:
	poetry run ruff check --select I --fix src/
	poetry run ruff format src/

update-failed:
	poetry run python src/set_failed_state.py


.PHONY: \
	format \
	update-failed

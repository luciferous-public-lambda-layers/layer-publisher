SHELL = /usr/bin/env bash -xeuo pipefail
PYTHONPATH = ./src

format:
	poetry run ruff check --select I --fix src/
	poetry run ruff format src/

update-failed:
	poetry run python src/set_failed_state.py

publish-start-publish:
	poetry run python src/publish/start_publish.py

publish-finish-publish:
	poetry run python src/publish/finish_publish.py

generate-start-generate:
	poetry run python src/generate/start_generate.py

generate-complete-generate:
	poetry run python src/generate/complete_generate.py



.PHONY: \
	format \
	update-failed \
	publish-start-publish \
	publish-finish-publish \
	generate-start-generate \
	generate-complete-generate

SHELL = /usr/bin/env bash -xeuo pipefail

format:
	poetry run ruff check --select I --fix src/
	poetry run ruff format src/

update-failed:
	poetry run python src/set_failed_state.py

publish-start-deploy:
	poetry run python src/publish/start_deploy.py

publish-finish-deploy:
	poetry run python src/publish/finish_deploy.py

generate-start-generate:
	poetry run python src/generate/start_generate.py

generate-complete-generate:
	poetry run python src/generate/complete_generate.py



.PHONY: \
	format \
	update-failed \
	publish-start-deploy \
	publish-finish-deploy \
	generate-start-generate \
	generate-complete-generate

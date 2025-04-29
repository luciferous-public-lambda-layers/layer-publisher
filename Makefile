SHELL = /usr/bin/env bash -xeuo pipefail

format:
	poetry run ruff check --select I --fix src/
	poetry run ruff format src/

update-failed:
	poetry run python src/layer_publisher/set_failed_state.py

publish-start-publish:
	poetry run python src/layer_publisher/publish/start_publish.py

publish-finish-publish:
	poetry run python src/layer_publisher/publish/finish_publish.py

generate-start-generate:
	poetry run python src/layer_publisher/generate/start_generate.py

generate-complete-generate:
	poetry run python src/layer_publisher/generate/complete_generate.py

test:
	poetry run python src/layer_publisher/publish/test.py

.PHONY: \
	format \
	update-failed \
	publish-start-publish \
	publish-finish-publish \
	generate-start-generate \
	generate-complete-generate

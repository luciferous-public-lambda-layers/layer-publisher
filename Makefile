SHELL = /usr/bin/env bash -xeuo pipefail

format:
	poetry run ruff check --select I --fix src/
	poetry run ruff format src/

update-failed:
	poetry run python src/layer_publisher/set_failed_state.py

publish-start-publish:
	poetry run python src/layer_publisher/publish/start_publish.py

publish-publish-before-publish:
	poetry run python src/layer_publisher/publish/publish/before_publish.py

publish-publish-after-publish:
	poetry run python src/layer_publisher/publish/publish/after_publish.py

publish-finish-publish:
	poetry run python src/layer_publisher/publish/finish_publish.py

generate-start-generate:
	poetry run python src/layer_publisher/generate/start_generate.py

generate-complete-generate:
	poetry run python src/layer_publisher/generate/complete_generate.py

.PHONY: \
	format \
	update-failed \
	publish-start-publish \
	publish-publish-before-publish \
	publish-publish-after-publish \
	publish-finish-publish \
	generate-start-generate \
	generate-complete-generate

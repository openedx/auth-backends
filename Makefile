.PHONY: clean quality requirements test upgrade check_keywords

clean:
	coverage erase
	rm -rf .tox
	find . -name '*.pyc' -delete

quality:
	tox -e quality

requirements:  ## install development environment requirements
	uv sync --group dev

test:
	tox

upgrade: ## update the uv.lock to use the latest releases satisfying our constraints
	uv run --with edx-lint edx_lint write_uv_constraints pyproject.toml
	uv lock --upgrade

check_keywords: ## Scan the Django models in all installed apps in this project for restricted field names
	tox -e check_keywords

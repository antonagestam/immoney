.PHONY: requirements
requirements: export UV_CUSTOM_COMPILE_COMMAND='make requirements'
requirements:
	@uv pip compile \
		--all-extras \
		--generate-hashes \
		--strip-extras \
		--upgrade \
		--output-file=requirements.txt \
		pyproject.toml

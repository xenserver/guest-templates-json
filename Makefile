JSON_FILES := $(shell find json -name '*.json')
LINT_OPTIONS ?= --forbid duplicate-keys

.PHONY: check
check: lint-json
	python ./check.py

.PHONY: lint-json
lint-json: $(JSON_FILES)
	jsonlint $(LINT_OPTIONS) $^

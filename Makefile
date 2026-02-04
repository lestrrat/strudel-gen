STRUDEL_DOCS ?= ../strudel-docs

.PHONY: data clean

data: ## Regenerate compressed reference data from strudel-docs
	python3 scripts/generate-data.py "$(STRUDEL_DOCS)"

clean: ## Remove generated data
	rm -f data/functions.jsonl data/sounds.jsonl data/mini-notation.jsonl

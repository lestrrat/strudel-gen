STRUDEL_DOCS ?= ../strudel-docs

.PHONY: data idioms clean

data: ## Regenerate compressed reference data from strudel-docs
	python3 scripts/generate-data.py "$(STRUDEL_DOCS)"

idioms: ## Compile idioms from data/idioms/*.strudel to data/idioms.jsonl
	python3 scripts/generate-idioms.py

clean: ## Remove generated data
	rm -f data/functions.jsonl data/sounds.jsonl data/mini-notation.jsonl data/idioms.jsonl

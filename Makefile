STRUDEL_DOCS ?= ../strudel-docs

.PHONY: all data idioms anti-patterns snippets functions-index rewrites clean

all: data idioms anti-patterns snippets functions-index rewrites ## Build everything

data: ## Regenerate compressed reference data from strudel-docs
	python3 scripts/generate-data.py "$(STRUDEL_DOCS)"

idioms: ## Compile idioms from data/idioms/*.strudel to data/idioms.jsonl
	python3 scripts/generate-idioms.py

anti-patterns: ## Compile anti-patterns from data/anti-patterns/*.yaml to data/anti-patterns.jsonl
	python3 scripts/generate-anti-patterns.py

snippets: ## Index snippets from snippets/*.strudel to data/snippets.jsonl
	python3 scripts/generate-snippets.py

functions-index: data ## Build category index from data/functions.jsonl
	python3 scripts/generate-functions-index.py

rewrites: ## Merge mini-notation rewrites into existing mini-notation.jsonl (no strudel-docs needed)
	python3 scripts/merge-mini-notation-rewrites.py

clean: ## Remove generated data
	rm -f data/functions.jsonl data/sounds.jsonl data/mini-notation.jsonl data/idioms.jsonl data/anti-patterns.jsonl data/snippets.jsonl data/functions-index.jsonl

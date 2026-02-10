---
name: strudel-annotate
description: Annotates Strudel code by breaking method chains onto separate lines and adding inline comments explaining each function call, using the data/ reference files.
argument-hint: <strudel code or path to .strudel file> (optional — defaults to currently active buffer)
---

# Strudel Annotator — Code Explainer

You are an expert Strudel live-coder. Your job is to take existing Strudel code and produce an annotated version: each chained method call on its own line with an inline comment explaining what it does. All explanations must be grounded in the reference data, not guessed.

## User's input

$ARGUMENTS

## Your approach

### Phase 1 — Obtain the code

1. If the user provided a file path (e.g., `snippets/foo.strudel`), read the file.
2. If they pasted code directly, use that.
3. **If no argument was provided**, use the `mcp__ide__getDiagnostics` tool (with no `uri` argument) to discover open files, or check for `<system-reminder>` messages that mention the user opened a file. Use the **most recent / currently active** `.strudel` file as the source. The active buffer is the one the user most recently interacted with — prefer the file mentioned in the latest `<system-reminder>` over earlier ones.
4. If none of the above apply, ask the user what to annotate.

Record whether the source came from a file (and which file). Identify all method chains and `register()` blocks that need annotation.

### Phase 2 — Look up every function (mandatory)

**This is mandatory. Never skip lookups. Never rely on your own knowledge of what a function does.**

For every function and method in the code:

1. **Grep** for `"name":"<fn>"` in `data/functions.jsonl`. Read the `desc`, `params`, and `examples` fields.
2. If the exact name isn't found, search for it as a **synonym** — Grep for `"<fn>"` more broadly in `data/functions.jsonl` and check the `synonyms` arrays.
3. For any sounds referenced, Grep for the sound name in `data/sounds.jsonl` to confirm it exists and understand what it is.
4. If a function is defined via `register()` within the same file or snippets, note that it is a custom registration and describe it based on its implementation.
5. **Last resort — Strudel source code:** Only consult the Strudel source tree if the data files don't have the answer. Check the `STRUDEL_SRC` environment variable for the source path. If it is not set, ask the user.

### Phase 3 — Annotate the code

Reformat the code following these rules:

- **One chained call per line.** Break `a.b().c().d()` into separate lines with proper indentation.
- **Inline comments.** Add a short `//` comment at the end of each line explaining what that specific call does. Keep comments concise (aim for under 60 characters) but precise. Use the description from `data/functions.jsonl` as the basis — do not invent explanations.
- **Preserve structure.** Do not change the logic, variable names, or behavior of the code. Only reformat and add comments.
- **Nested chains.** If a method argument itself contains a chain (e.g., `reify(x).mul(120)` inside `.penv()`), annotate that inner chain too, either inline if short or broken out with indentation if complex.
- **register() blocks.** For custom `register()` calls, annotate both the parameter list and the body chain.
- **Preserve existing comments.** Keep any block comments (e.g., `// Laser/zap sound effect...`) that describe the overall purpose. Only add to them, don't remove or rewrite them.

### Phase 4 — Verify

Before presenting:
- Confirm every annotation is backed by a lookup in `data/functions.jsonl` or `data/sounds.jsonl`.
- If a function was not found in the data files, explicitly note this in the comment (e.g., `// fill() — not in reference data; appears to fill silent gaps`).
- Ensure the reformatted code is functionally identical to the original.

### Phase 5 — Write the result

**If the source came from a file**, write the annotated code back to that same file in-place using the Edit or Write tool. Then briefly confirm what was done and list any functions not found in the reference data.

**If the source was pasted code** (not from a file), present the annotated code in a fenced code block. Include a brief note listing any functions that were **not found** in the reference data, if any.

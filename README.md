# IBTAC Lexical Analyzer (Python)

Python implementation of the open-ended IBTAC lexer assignment. The project
tokenizes IBTAC source files while resolving every ambiguity from the spec,
and includes a short report plus regression inputs under `tests/`.

## Features
- Two identifier forms: standard (`[_A-Za-z][_A-Za-z0-9_]*`) and the required
  student-prefixed variant starting with `139`.
- Exact keyword recognition for `if`, `else`, `while`, `return`, `func`.
- Flexible numeric literals: integers, floats, leading/trailing dots, and
  exponent forms (e.g., `.5`, `1.`, `1.2e-3`).
- Dollar-delimited strings (`$...$`) with multi-line support.
- Operators and punctuation include both `!=` and `<>` for not-equal.
- Comment handling for `//` and `/* ... */` plus dedicated errors for malformed
  constructs (unterminated string/comment, nested comments, malformed numbers,
  invalid symbols).

See `report.md` for the full write-up covering every design decision,
trade-off, and grading artifact.

## Requirements
- Python 3.9+ (dataclasses imported from stdlib; no third-party packages).

## Quick Start
```bash
# Show tokens for a single input
python3 lexer.py tests/07_name_and_id.ib

# JSON output (useful for diffing)
python3 lexer.py tests/07_name_and_id.ib --json
```

The CLI prints either a fixed-width table (`type`, `lexeme`, `line:column`) or,
with `--json`, a structured array of token dictionaries, which is used to
capture regressions in `tests/actual_results.json`.

## Project Layout
- `lexer.py` – core lexer, CLI entry point, and token dataclass.
- `tests/` – sample IBTAC programs plus golden outputs (`expected.tsv`,
  `actual_results.json`) covering identifiers, keywords, numeric edge cases,
  multi-line strings, operators, and error conditions.
- `report.md` – narrative submission (conflict analysis, DFA sketches,
  verification steps, run instructions).
- `LICENSE` – upstream license (MIT by default, adjust if needed).

## Testing
The project ships ready-made `.ib` fixtures that exercise both success and
failure cases. Run them ad hoc:
```bash
for file in tests/*.ib; do
    echo "== $file =="
    python3 lexer.py "$file" || true   # keep going on intentional failures
done
```
`tests/actual_results.json` records reference JSON outputs; regenerate it after
changing the lexer to keep automated comparisons in sync.

## Design Decisions
A concise summary of the highest-risk choices:
- Multi-line `$` strings remain valid until another `$` is seen.
- Nested block comments are rejected immediately to highlight ambiguous
  constructs.
- The literal `139` alone is accepted as `NUMBER`, while `139foo` surfaces as
  the required student-prefixed identifier form.

Rationale, alternatives considered, and diagrams live in `report.md` (§2–§7).

## License
See `LICENSE` for distribution terms. Contributions should match that license.


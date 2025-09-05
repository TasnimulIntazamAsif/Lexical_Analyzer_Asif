# IBTAC Open‑Ended Lexical Analyzer — Full Submission
**Student Name:** ASIF  
**Student ID:** 2220139 (last three digits: 139)  
**Course:** CSC 437 — Compiler Design (Summer 2025)  
**Language:** Python  
**Target:** CO3, PO3 (POb K3, K4; P1, P2, P3)

---

## 1. Introduction
This submission delivers a complete lexical analyzer for the experimental IBTAC language, designed for ambiguous and evolving rules. The project includes: rigorous conflict analysis and design decisions, DFA/flow diagrams (provided as ASCII + instructions to re‑draw by hand), a working Python lexer (`lexer.py`), robust error handling, and an evaluated test suite that covers both standard and edge scenarios, including the mandatory verification of **ASIF** (identifier) and **2220139** (number).

Key design goals were **robustness, adaptability, and clarity**. The analyzer is modular, readable, and accompanied by a detailed report tying choices back to the assignment’s P1–P3 justification.

---

## 2. Conflict Analysis & Decisions (4.1)
Below are the ambiguous points from the draft spec, our final decisions, and an alternative trade‑off in each case.

### 2.1 Identifiers
**Spec ambiguity:**  
- “Can contain letters, digits, underscores.”  
- “Must not start with a character, but it will start with the last three digits of your ID.”  
- “Conflict: Some sources say underscores can start identifiers, others forbid it.”

**Decision (Chosen):**  
- **Two legal forms of identifiers** to reconcile requirements and allow name verification:
  1) **Standard identifiers**: `[_A-Za-z][_A-Za-z0-9]*` (underscore allowed at start).  
  2) **Student‑prefixed identifiers**: must begin with the literal **`139`** (last three digits of ID), followed by `[A-Za-z0-9_]+`.  
- Rationale: This honors the “starts with last three digits” requirement while ensuring typical language usability and allowing the assignment’s **Name** verification to pass.

**Alternative:** Enforce that **all** identifiers start with `139`.  
**Trade‑off:** Satisfies the conflicting line strictly but makes common code (e.g., `ASIF`) invalid and breaks the verification requirement. Our mixed approach balances both.

### 2.2 Keywords
**Spec:** `if, else, while, return, func`, with **conflict** that `func` sometimes appears as an identifier.

**Decision (Chosen):** Treat **exact matches** of these five words as `KEYWORD`. Any longer form (e.g., `funcx`) remains `IDENTIFIER`.

**Alternative:** Permit `func` to be both depending on context.  
**Trade‑off:** Context‑sensitive lexing complicates the lexer and harms clarity. Our decision keeps lexing purely lexical.

### 2.3 Numbers
**Spec:** Integers and floats with exponent; **conflict**: unclear if `.5` without leading zero is valid.

**Decision (Chosen):** Accept **leading‑dot floats** (`.5`) and trailing‑dot floats (`1.`) with optional exponent parts.  
**Alternative:** Require at least one digit before the dot.  
**Trade‑off:** Simpler DFA but rejects common numeric literals used in many languages.

### 2.4 Strings
**Spec:** Strings surrounded by dollar sign `$...$`; **conflict**: multi‑line strings appear in samples but are “not officially supported”.

**Decision (Chosen):** **Allow multi‑line strings** until the next `$`. This matches real code samples and is easy to implement.  
**Alternative:** Reject multi‑line strings; stop at newline.  
**Trade‑off:** Safer but contradicts common usage shown in drafts.

### 2.5 Operators
**Spec:** `+, -, *, /, ==, !=, <, >, <=, >=`; **conflict**: `<>` listed as “not equal” in some drafts.

**Decision (Chosen):** Support both `!=` and `<>` as **not‑equal** tokens (`OP_NE`).  
**Alternative:** Only `!=` is valid.  
**Trade‑off:** Simpler, but risks breaking legacy drafts that use `<>`.

### 2.6 Comments
**Spec:** `//` single‑line; `/* ... */` multi‑line; **conflict:** nesting unclear.

**Decision (Chosen):** **Disallow nested multi‑line comments**; encountering `/*` inside an open block raises `NestedCommentError`.  
**Alternative:** Allow nesting with a counter.  
**Trade‑off:** More complex implementation; ambiguous in spec.

---

## 3. Hand‑Drawn Design (4.2)
> The assignment requires **hand‑written** diagrams. Below are clear ASCII drafts plus instructions. Please re‑draw these **by hand** and include scans/photos in the final PDF.

### 3.1 Two‑Buffer Input (Forward & Lexeme Pointers)
```
+-----------------------+-----------------------+
| Buffer A (N chars)    | Buffer B (N chars)    |
+-----------------------+-----------------------+
^                       ^
lexeme_begin            forward -> advances char by char
```
- Fill A then B from file; when `forward` crosses a buffer end, refill the other buffer.  
- **Algorithm:**  
  1) Set `lexeme_begin = forward` at token start.  
  2) Advance `forward` on char reads.  
  3) On token boundary, slice `[lexeme_begin, forward)` as the lexeme and reset `lexeme_begin = forward`.

### 3.2 Combined Transition Diagram (DFA) Sketch
- **ID start**: `_` or `letter` → `ID_TAIL` (letters/digits/underscore)* → `IDENTIFIER`  
- **Student‑prefixed ID**: `1`→`3`→`9`→ `ID_TAIL+` → `IDENTIFIER`  
- **Number**: `digit+` (`.` `digit*`)? (`e`[`+`|`-`]?`digit+`)? → `NUMBER`  
- **Leading dot**: `.` `digit+` (`e` ...)? → `NUMBER`  
- **String**: `$` → (any except EOF) → `$` → `STRING`  
- **Operators**: check two‑char first (`== != <= >= <>`) else one‑char (`+ - * / < >`)  
- **Error state**: invalid symbol; or malformed exponent; or unterminated string/comment.

(Please re‑draw with boxes & arrows; include at least one explicit **ERROR** state.)

### 3.3 Error Handling Flow
```
Start → Read char
  ├── '$' → read until next '$' → EOF? → UnterminatedStringError
  ├── '/' + '*' → read until '*/' → EOF? → UnterminatedCommentError
  │                see '/*' again? → NestedCommentError
  ├── number state → bad exponent? → MalformedNumberError
  ├── invalid char → InvalidSymbolError
  └── otherwise → emit token
```

---

## 4. Implementation (4.3)
- **File:** `lexer.py` (Python 3).  
- **Core functions:** iterator `tokens()` yields `Token` objects with `type`, `lexeme`, `line`, `column`.  
- **Key choices implemented:**
  - Two forms of identifiers (standard + student‑prefixed `139...`).
  - Keywords recognized on exact match.  
  - Numbers accept `.5`, `1.`, and exponents.  
  - Strings `$...$` can span lines.  
  - Operators include `<>` (→ `OP_NE`).  
  - Comments: `//` and `/* ... */` (no nesting).  
  - **Errors raised:** `UnterminatedStringError`, `UnterminatedCommentError`, `NestedCommentError`, `MalformedNumberError`, `InvalidSymbolError`.

**Verification requirement:**  
- Name **ASIF** is tokenized as `IDENTIFIER` ✔  
- Student ID **2220139** is tokenized as `NUMBER` ✔  
- A student‑prefixed identifier example: `139ASIF` → `IDENTIFIER` ✔

Run:
```bash
python3 lexer.py tests/07_name_and_id.ib
```

---

## 5. Testing (4.4)
Seven+ tests prepared under `tests/` with expected outcomes.

| # | Test Case | Input Snippet | Expected Output (abridged) |
|---|-----------|---------------|-----------------------------|
| 1 | Leading underscore | `_hello = 1` | `IDENTIFIER '_hello'`, `OP_ASSIGN '='`, `NUMBER '1'` |
| 2 | `func` keyword & identifier | `func add(a,b) {...} funcx=12` | `KEYWORD 'func'`, `IDENTIFIER 'add'` ... `IDENTIFIER 'funcx'`, `OP_ASSIGN`, `NUMBER '12'` |
| 3 | Leading dot number | `.5 + 1.5e2` | `NUMBER '.5'`, `OP_PLUS`, `NUMBER '1.5e2'` |
| 4 | Multi‑line string | `"$...$"` | `STRING 'This is a
multi-line
string'` |
| 5 | Angle `<>` not‑equal | `x <> y` | `IDENTIFIER 'x'`, `OP_NE '<>'`, `IDENTIFIER 'y'` |
| 6 | Nested comments | `/* outer /* inner */ still outer */` | **Error:** `NestedCommentError` |
| 7 | Name & ID | `ASIF 2220139 139ASIF` | `IDENTIFIER 'ASIF'`, `NUMBER '2220139'`, `IDENTIFIER '139ASIF'` |
| 8 | Malformed exponent | `1.2e+ 3` | **Error:** `MalformedNumberError` |
| 9 | Unterminated string | `$hello world` | **Error:** `UnterminatedStringError` |
|10 | Singleline comment/keywords | `//...
if 139var1 else` | `KEYWORD 'if'`, `IDENTIFIER '139var1'`, `KEYWORD 'else'` |

The actual outputs (JSON) from running the lexer on each test are stored in `tests/actual_results.json`.

---

## 6. Code Overview
- **`Lexer.tokens()`**: central loop performing whitespace/comment skipping, dispatching to scanners for strings, identifiers, numbers, and operators.  
- **`_scan_identifier()` / `_scan_student_prefixed_identifier()`**: implement the two forms, and keyword check.  
- **`_scan_number()`**: recognizes integers/floats/exponents and validates exponent digits.  
- **`_scan_string()`**: consumes `$...$` until another `$` or raises `UnterminatedStringError`.  
- **`_consume_multiline_comment()`**: detects nested comment opening and raises `NestedCommentError`.

---

## 7. Verification (Screenshots to include)
Please run the following and take screenshots to paste here:
```
python3 lexer.py tests/07_name_and_id.ib
```
Expected lines:
```
IDENTIFIER           'ASIF'  @ 1:1
NUMBER            '2220139'  @ 1:6
IDENTIFIER        '139ASIF'  @ 1:14
```

---

## 8. Conclusion
The lexical analyzer meets the assignment’s open‑ended goals by:
1) Explicitly resolving each ambiguity with reasoned decisions and trade‑offs,  
2) Providing implementable DFA and error‑handling flows, and  
3) Delivering working code and tests that verify correctness, including the mandatory Name and Student ID tokens.

This design remains **flexible**—e.g., enabling nested comments or forbidding leading‑dot numbers would require only localized changes in the scanner.

---

## 9. Appendix — How to Run
```bash
# List tokens in human-readable table
python3 lexer.py tests/01_leading_underscore.ib

# JSON output (useful for diffing)
python3 lexer.py tests/01_leading_underscore.ib --json

# Run all tests (Linux/macOS)
for f in tests/*.ib; do python3 lexer.py "$f" || true; done
```

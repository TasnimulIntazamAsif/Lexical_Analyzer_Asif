#!/usr/bin/env python3
# IBTAC Lexical Analyzer (Open-Ended) — Python implementation
# Student: ASIF
# ID: 2220139  (last three digits: "139")
# Decision summary (see report.md for details):
# - Identifiers: two allowed forms
#   (A) Standard: start with letter or underscore, then letters/digits/_
#   (B) Student-prefixed: start with literal "139" then letters/digits/_
# - Keywords: {if, else, while, return, func} with exact match; longer forms remain identifiers
# - Numbers: integers, floats, and exponent forms. Accepts leading-dot floats like ".5"
# - Strings: delimited by dollar sign $...$; multi-line strings are allowed (by design decision)
# - Operators: +, -, *, /, ==, !=, <, >, <=, >=, and "<>" (treated as not-equal)
# - Comments: // single-line; /* ... */ multi-line (no nesting allowed)
# - Error handling: malformed numbers, unterminated strings/comments, invalid symbols, nested comments
# - Verification: must recognize "ASIF" as IDENTIFIER and "2220139" as NUMBER (or IDENTIFIER if prefixed form). We choose NUMBER.

from dataclasses import dataclass
from typing import List, Optional, Iterator, Tuple

# -----------------------
# Token definitions
# -----------------------

@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    column: int

    def __repr__(self):
        return f"Token(type={self.type}, lexeme={self.lexeme!r}, line={self.line}, column={self.column})"

KEYWORDS = {"if", "else", "while", "return", "func"}

WHITESPACE = {' ', '\t', '\r'}

# -----------------------
# Lexer implementation
# -----------------------

class LexerError(Exception):
    pass

class UnterminatedStringError(LexerError):
    pass

class UnterminatedCommentError(LexerError):
    pass

class NestedCommentError(LexerError):
    pass

class MalformedNumberError(LexerError):
    pass

class InvalidSymbolError(LexerError):
    pass

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.length = len(source)
        self.index = 0
        self.line = 1
        self.col = 1

    # Utility: peek current and lookahead characters
    def _current(self) -> str:
        if self.index >= self.length:
            return '\0'
        return self.source[self.index]

    def _peek(self, k: int=1) -> str:
        pos = self.index + k
        if pos >= self.length:
            return '\0'
        return self.source[pos]

    def _advance(self) -> str:
        ch = self._current()
        self.index += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self._current() == expected:
            self._advance()
            return True
        return False

    def tokens(self) -> Iterator[Token]:
        while True:
            self._skip_whitespace_and_comments()
            ch = self._current()
            if ch == '\0':
                break

            start_line, start_col = self.line, self.col

            # Strings: $...$
            if ch == '$':
                yield self._scan_string(start_line, start_col)
                continue

            # Identifiers (two forms): standard or "139" prefixed
            if ch.isalpha() or ch == '_':
                yield self._scan_identifier(start_line, start_col)
                continue
            if ch == '1' and self._peek() == '3' and self._peek(2) == '9':
                yield self._scan_student_prefixed_identifier(start_line, start_col)
                continue

            # Numbers (including .5 leading dot)
            if ch.isdigit() or (ch == '.' and self._peek().isdigit()):
                yield self._scan_number(start_line, start_col)
                continue

            # Operators & punctuation
            two = ch + self._peek()
            if two in ('==', '!=', '<=', '>=', '<>'):
                ttype = {
                    '==': 'OP_EQ',
                    '!=': 'OP_NE',
                    '<=': 'OP_LE',
                    '>=': 'OP_GE',
                    '<>': 'OP_NE'
                }[two]
                self._advance(); self._advance()
                yield Token(ttype, two, start_line, start_col)
                continue

            if ch in '+-*/<>(){}[],;':
                tmap = {
                    '+': 'OP_PLUS',
                    '-': 'OP_MINUS',
                    '*': 'OP_STAR',
                    '/': 'OP_SLASH',
                    '<': 'OP_LT',
                    '>': 'OP_GT',
                    '(': 'LPAREN',
                    ')': 'RPAREN',
                    '{': 'LBRACE',
                    '}': 'RBRACE',
                    '[': 'LBRACKET',
                    ']': 'RBRACKET',
                    ',': 'COMMA',
                    ';': 'SEMICOLON',
                }
                self._advance()
                yield Token(tmap[ch], ch, start_line, start_col)
                continue

            # Single char '='
            if ch == '=':
                self._advance()
                yield Token('OP_ASSIGN', '=', start_line, start_col)
                continue

            # Unknown
            raise InvalidSymbolError(f"Invalid symbol {ch!r} at line {start_line}, column {start_col}")

    def _skip_whitespace_and_comments(self):
        while True:
            ch = self._current()
            # whitespace
            if ch in WHITESPACE or ch == '\n':
                self._advance()
                continue

            # comments
            if ch == '/':
                if self._peek() == '/':  # single-line
                    # consume till end of line
                    while self._current() not in ('\n', '\0'):
                        self._advance()
                    continue  # newline will be consumed on next loop
                elif self._peek() == '*':  # multiline
                    self._advance()  # '/'
                    self._advance()  # '*'
                    self._consume_multiline_comment()
                    continue

            break

    def _consume_multiline_comment(self):
        depth = 1
        while True:
            ch = self._current()
            if ch == '\0':
                raise UnterminatedCommentError(f"Unterminated comment starting before line {self.line}, column {self.col}")
            if ch == '/' and self._peek() == '*':
                # nesting not allowed — report error
                raise NestedCommentError(f"Nested comment found at line {self.line}, column {self.col}")
            if ch == '*' and self._peek() == '/':
                self._advance(); self._advance()
                depth -= 1
                if depth == 0:
                    return
            else:
                self._advance()

    def _scan_string(self, start_line, start_col) -> Token:
        # consume opening $
        self._advance()
        lex = []
        while True:
            ch = self._current()
            if ch == '\0':
                raise UnterminatedStringError(f"Unterminated string starting at line {start_line}, column {start_col}")
            if ch == '$':
                self._advance()
                break
            # allow escape of $ via $$? Not specified; keep simple: only terminating $ ends string
            lex.append(self._advance())
        return Token('STRING', ''.join(lex), start_line, start_col)

    def _scan_identifier(self, start_line, start_col) -> Token:
        lex = [self._advance()]
        while True:
            ch = self._current()
            if ch.isalnum() or ch == '_':
                lex.append(self._advance())
            else:
                break
        text = ''.join(lex)
        if text in KEYWORDS:
            return Token('KEYWORD', text, start_line, start_col)
        return Token('IDENTIFIER', text, start_line, start_col)

    def _scan_student_prefixed_identifier(self, start_line, start_col) -> Token:
        # starts with '1''3''9', then at least one [A-Za-z0-9_]
        lex = [self._advance(), self._advance(), self._advance()]
        if not (self._current().isalnum() or self._current() == '_'):
            # treat "139" alone as a NUMBER (permissive), otherwise invalid identifier
            return Token('NUMBER', '139', start_line, start_col)
        while True:
            ch = self._current()
            if ch.isalnum() or ch == '_':
                lex.append(self._advance())
            else:
                break
        text = ''.join(lex)
        return Token('IDENTIFIER', text, start_line, start_col)

    def _scan_number(self, start_line, start_col) -> Token:
        # number: int | float | float with exponent
        # forms: 123, 123.45, .5, 1., 1e10, 1.2e-3
        i = self.index
        saw_digit = False
        saw_dot = False
        saw_exp = False

        def is_digit(c): return c.isdigit()

        # integer part (optional if starts with '.')
        if self._current().isdigit():
            saw_digit = True
            while self._current().isdigit():
                self._advance()

        # fractional
        if self._current() == '.':
            saw_dot = True
            self._advance()
            if self._current().isdigit():
                saw_digit = True
                while self._current().isdigit():
                    self._advance()

        # exponent
        if self._current() in ('e', 'E'):
            saw_exp = True
            self._advance()
            if self._current() in ('+', '-'):
                self._advance()
            if not self._current().isdigit():
                raise MalformedNumberError(f"Malformed exponent at line {start_line}, column {start_col}")
            while self._current().isdigit():
                self._advance()

        text = self.source[i:self.index]
        # sanity check: at least one digit somewhere
        if not saw_digit:
            raise MalformedNumberError(f"Malformed number at line {start_line}, column {start_col}")
        return Token('NUMBER', text, start_line, start_col)

def tokenize(source: str) -> List[Token]:
    return list(Lexer(source).tokens())

def main():
    import argparse, sys, json
    parser = argparse.ArgumentParser(description="IBTAC Lexer (ASIF 2220139)")
    parser.add_argument("file", help="Source file to tokenize")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        src = f.read()

    try:
        toks = tokenize(src)
        if args.json:
            out = [t.__dict__ for t in toks]
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            for t in toks:
                print(f"{t.type:<12} {t.lexeme!r:>20}  @ {t.line}:{t.column}")
    except LexerError as e:
        print(f"[LEXER ERROR] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

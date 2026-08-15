import re
import os
import sys
import argparse
from typing import NamedTuple
from time import sleep


class Token(NamedTuple):
    type: str
    value: str
    line: int


TOKENS: list[tuple[str, str]] = [
    ("FORBIDDEN", r"\bif|for|def|else|match|case\b"),
    ("WHILST", r"\bwhilst\b"),
    ("WHILSTF", r"\bwhilstf\b"),
    ("WHILE", r"\bwhile\b"),
    ("PRINT", r"\bprint\b"),
    ("SLEEP", r"\bsleep\b"),
    ("BREAK", r"\bbreak\b"),
    ("NUMBER", r"\b\d+\b"),
    ("STRING", r'"[^"]*"'),
    ("IDENT", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("ASSIGN", r"="),
    ("OP", r"==|!=|<=|>=|\+|\-|\*|/|<|>"),
    ("LEFTPARENC", r"\{"),
    ("LEFTPARENS", r"\["),
    ("LEFTPAREN", r"\("),
    ("RIGHTPARENC", r"\}"),
    ("RIGHTPARENS", r"\]"),
    ("RIGHTPAREN", r"\)"),
    ("COLON", r":"),
    ("SEMICOLON", r";"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]

MATCH_ENGINE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKENS)
)

TICK_DELAY: float = 0.05


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transpile Whilst (.wlst) source files into Python (.py)."
    )

    parser.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="Path to the input .wlst file"
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default=None,
        help="Path to the output .py file",
    )

    args = parser.parse_args()
    
    if not os.path.isfile(args.file):
        print(f"Error: Input file '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(args.file, "r") as file:
        fileData: str = file.read()
    with open(args.output, "w") as file:
        file.write(parse(lex(fileData)))
    
    print(f"Transpiled successfully: '{args.file}' -> '{args.output}'")


def lex(fileData: str) -> list[str]:
    tokens: list[Token] = []
    lineNumber: int = 1

    for match in MATCH_ENGINE.finditer(fileData):
        kind: str = match.lastgroup
        value: str = match.group()

        if kind == "FORBIDDEN":
            raise SyntaxError(
                f"\n[LINE {lineNumber}] WHILST ERROR: 'Greed of Convenience' Detected!\n"
                f"--> You tried using '{value}'. '{value}' does not exist here.\n"
                f"--> There are no shortcuts. EVERY control flow must be a 'whilst' loop!"
            )
        elif kind == "NEWLINE":
            lineNumber += 1
            continue
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise SyntaxError(f"Syntax error, failed to recognize symbol: {value}.")

        tokens.append(Token(kind, value, lineNumber))

    return tokens


def parse(tokenized: list[Token]) -> str:
    parsedString = ""
    indent = 0
    newLine = False

    for token in tokenized:
        if newLine and token.type not in "RIGHTPARENC":
            parsedString += "    " * indent
            newLine = False

        if token.type in (
            "LEFTPAREN",
            "RIGHTPAREN",
            "NUMBER",
            "IDENT",
            "PRINT",
            "STRING",
        ):
            parsedString += token.value
        elif token.type in ("OP", "ASSIGN"):
            parsedString += f" {token.value} "
        elif token.type == "SEMICOLON":
            parsedString += "\n"
            newLine = True
        elif token.type == "LEFTPARENC":
            parsedString += ":\n"
            indent += 1
            newLine = True
        elif token.type == "RIGHTPARENC":
            indent = max(0, indent - 1)
            newLine = True
        elif token.type in ("WHILST", "WHILE"):
            parsedString += "while"

    return parsedString


if __name__ == "__main__":
    main()

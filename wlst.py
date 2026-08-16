import argparse
import os
import re
import sys
from typing import NamedTuple


class Token(NamedTuple):
    type: str
    value: str
    line: int


TOKENS: list[tuple[str, str]] = [
    ("FORBIDDEN", r"\b(if|for|def|else|match|case)\b"),
    ("WHILSTF", r"\bwhilstf\b"),
    ("WHILST", r"\bwhilst\b"),
    ("WHILE", r"\bwhile\b"),
    ("PRINT", r"\bprint\b"),
    ("SLEEP", r"\bsleep\b"),
    ("BREAK", r"\bbreak\b"),
    ("NUMBER", r"\b\d+\b"),
    ("STRING", r'"[^"]*"'),
    ("IDENT", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("ASSIGN", r"="),
    ("OP", r"not|==|!=|<=|>=|\+|\-|\*|/|<|>|\-=|\+=|/=|\*="),
    ("NOT", r"!"),
    ("COMMA", r","),
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
        help="Path to the input .wlst file",
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

    outputPath = args.output
    if not outputPath:
        baseName, _ = os.path.splitext(args.file)
        outputPath = f"{baseName}.py"

    with open(args.file, "r") as file:
        fileData: str = file.read()

    try:
        tokenStream = lex(fileData)
        pythonCode = parse(tokenStream)

        with open(outputPath, "w") as file:
            file.write(pythonCode)

        print(f"Transpiled successfully: '{args.file}' -> '{outputPath}'")

    except SyntaxError as err:
        print(err, file=sys.stderr)
        sys.exit(1)


def lex(fileData: str) -> list[Token]:
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
            raise SyntaxError(
                f"[LINE {lineNumber}] Syntax error: Unrecognized symbol '{value}'."
            )

        tokens.append(Token(kind, value, lineNumber))

    return tokens


def parse(tokenized: list[Token]) -> str:
    funcLines: list[str] = []
    mainLines: list[str] = []

    i = 0
    n = len(tokenized)
    indentLevel = 0
    blockStack: list[tuple[str, int]] = []
    newLine = True

    def emit(text: str):
        nonlocal newLine
        target = (
            funcLines
            if (blockStack and blockStack[0][0] == "whilstf")
            else mainLines
        )

        if newLine and text != "\n":
            target.append("    " * indentLevel)
            newLine = False

        target.append(text)

    while i < n:
        tok = tokenized[i]

        if tok.type == "WHILSTF":
            i += 1
            funcName = tokenized[i].value
            i += 2

            parenDepth = 1
            argGroups: list[list[Token]] = [[]]

            while i < n and parenDepth > 0:
                t = tokenized[i]
                if t.type == "LEFTPAREN":
                    parenDepth += 1
                    argGroups[-1].append(t)
                elif t.type == "RIGHTPAREN":
                    parenDepth -= 1
                    if parenDepth > 0:
                        argGroups[-1].append(t)
                elif t.type == "COMMA" and parenDepth == 1:
                    argGroups.append([])
                else:
                    argGroups[-1].append(t)
                i += 1

            condTokens = argGroups[0] if argGroups else []
            paramGroups = argGroups[1:] if len(argGroups) > 1 else []

            condStr = "".join(
                f" {t.value} " if t.type in ("OP", "ASSIGN") else t.value
                for t in condTokens
            ).strip()
            if not condStr:
                condStr = "True"

            # Extract parameters: include identifiers in condition + extra param groups
            paramsList: list[str] = []
            paramSet: set[str] = set()

            for t in condTokens:
                if t.type == "IDENT" and t.value not in paramSet and t.value not in ("True", "False"):
                    paramsList.append(t.value)
                    paramSet.add(t.value)

            for pg in paramGroups:
                pStr = "".join(t.value for t in pg).strip()
                if pStr and pStr not in paramSet:
                    paramsList.append(pStr)
                    paramSet.add(pStr)

            paramsStr = ", ".join(paramsList)

            if i < n and tokenized[i].type == "LEFTPARENC":
                i += 1

            funcLines.append(f"def {funcName}({paramsStr}):\n")
            funcLines.append(f"    while {condStr}:\n")

            blockStack.append(("whilstf", 2))
            indentLevel += 2
            newLine = True
            continue

        elif tok.type in ("WHILST", "WHILE"):
            # Check if next token is '{' (conditionless infinite whilst loop)
            if i + 1 < n and tokenized[i + 1].type == "LEFTPARENC":
                emit("while True")
            else:
                emit("while ")
            i += 1

        elif tok.type == "LEFTPARENC":
            emit(":\n")
            indentLevel += 1
            blockStack.append(("whilst", 1))
            newLine = True
            i += 1

        elif tok.type == "RIGHTPARENC":
            if blockStack:
                bType, delta = blockStack.pop()
                if bType == "whilst":
                    emit("time.sleep(TICK_DELAY)\n")
                indentLevel = max(0, indentLevel - delta)
            else:
                indentLevel = max(0, indentLevel - 1)
            newLine = True
            i += 1

        elif tok.type == "SEMICOLON":
            emit("\n")
            newLine = True
            i += 1

        elif tok.type == "PRINT":
            emit("print")
            i += 1

        elif tok.type == "SLEEP":
            emit("time.sleep")
            i += 1

        elif tok.type in ("OP", "ASSIGN"):
            emit(f" {tok.value} ")
            i += 1

        elif tok.type == "COMMA":
            emit(", ")
            i += 1

        else:
            emit(tok.value)
            i += 1

    outputCode = "import time\n\n"
    outputCode += f"TICK_DELAY = {TICK_DELAY}\n\n"

    if funcLines:
        outputCode += "# Functions\n" + "".join(funcLines) + "\n"

    if mainLines:
        outputCode += "".join(mainLines)

    return outputCode


if __name__ == "__main__":
    main()
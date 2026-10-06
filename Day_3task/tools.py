
"""A simple calculator tool for the Agentic AI task."""

import ast
import operator

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.Pow: operator.pow,
}


def evaluate(node):
    """Safely evaluate basic arithmetic expressions."""

    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = evaluate(node.left)
        right = evaluate(node.right)
        return OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](evaluate(node.operand))

    raise ValueError("Unsupported mathematical expression")


def calculator(expression: str) -> str:
    """Calculate an arithmetic expression and return the result as text."""

    try:
        result = evaluate(ast.parse(expression, mode="eval").body)
        return str(result)
    except Exception as error:
        return f"Calculator error: {error}"


if __name__ == "__main__":
    print("Test 1:", calculator("(12000 + 18000) * 0.9"))
    print("Test 2:", calculator("12000 + 18000 + 15000 + 4500"))
    print("Test 3:", calculator("2 ** 10"))
    print("Test 4:", calculator("import os"))

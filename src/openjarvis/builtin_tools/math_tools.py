import ast
import math
from collections.abc import Callable

from openjarvis.tools import tool

_ConvFactor = float | Callable[[float], float]

UNIT_CONVERSIONS: dict[str, _ConvFactor] = {
    "m_to_km": 0.001,
    "km_to_m": 1000,
    "ft_to_m": 0.3048,
    "m_to_ft": 3.28084,
    "mi_to_km": 1.60934,
    "km_to_mi": 0.621371,
    "kg_to_lb": 2.20462,
    "lb_to_kg": 0.453592,
    "c_to_f": lambda x: x * 9 / 5 + 32,
    "f_to_c": lambda x: (x - 32) * 5 / 9,
}

class SafeEvaluator(ast.NodeVisitor):
    def visit_BinOp(self, node):
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        self.generic_visit(node)

    def visit_Constant(self, node):
        if not isinstance(node.value, (int, float, complex)):
            raise ValueError(f"Invalid constant: {node.value}")

    def visit_Name(self, node):
        if node.id not in {"pi", "e"}:
            raise ValueError(f"Name not allowed: {node.id}")

    def visit_Module(self, node):
        self.generic_visit(node)

    def visit_Expr(self, node):
        self.generic_visit(node)

    def visit_Expression(self, node):
        self.generic_visit(node)

    def generic_visit(self, node):
        allowed = {
            ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Module, ast.Expr,
            ast.Expression, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
            ast.Mod, ast.Pow, ast.UAdd, ast.USub
        }
        if type(node) not in allowed:
            raise ValueError(f"Operation not allowed: {type(node).__name__}")
        super().generic_visit(node)

@tool()
def evaluate_expression(expression: str) -> str:
    """Safely evaluate a mathematical expression.

    Args:
        expression: Mathematical expression with +, -, *, /, //, %, ** (e.g., "2**10 + 1").

    Returns:
        Numeric result as a string.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        SafeEvaluator().visit(tree)

        env = {"pi": math.pi, "e": math.e}
        result = eval(compile(tree, "<string>", "eval"), {"__builtins__": {}}, env)
        return str(result)
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units of measurement.

    Args:
        value: Numeric value to convert.
        from_unit: Source unit.
        to_unit: Target unit.

    Returns:
        Converted value as a string.

    Examples:
        convert_units(5, "km", "m") -> "5000.0"
        convert_units(32, "f", "c") -> "0.0"
    """
    key = f"{from_unit}_to_{to_unit}"

    if key not in UNIT_CONVERSIONS:
        available = ", ".join(sorted(set(k.split("_to_")[0] for k in UNIT_CONVERSIONS)))
        return f"Error: Conversion '{key}' not found. Available: {available}"

    factor = UNIT_CONVERSIONS[key]
    result = factor(value) if callable(factor) else value * factor

    return str(result)

@tool()
def solve_equation(equation: str, variable: str = "x") -> str:
    """Solve a polynomial or linear equation symbolically.

    Args:
        equation: Equation string (e.g., "x**2 - 4 = 0" or "2*x + 3 = 7").
        variable: Variable name to solve for (default "x").

    Returns:
        Solution(s) as a string.
    """
    try:
        import sympy
    except ImportError:
        return "Error: sympy not installed. Install with: pip install sympy"

    try:
        expr = sympy.sympify(equation)
        var = sympy.Symbol(variable)
        solutions = sympy.solve(expr, var)

        if not solutions:
            return "No solutions found."
        return str(solutions)
    except Exception as e:
        return f"Error solving equation: {e}"

@tool()
def prime_factorize(n: int) -> list[int]:
    """Factorize an integer into its prime factors.

    Args:
        n: Positive integer to factorize.

    Returns:
        List of prime factors in ascending order.
    """
    if n < 2:
        return []

    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1

    if n > 1:
        factors.append(n)

    return factors

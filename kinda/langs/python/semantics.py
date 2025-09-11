# kinda/core/semantics.py

import random

env = {}


def evaluate(expr):
    """Safely evaluate an expression with proper error handling."""
    # Basic validation to prevent some dangerous constructs
    if not isinstance(expr, str):
        print(f"[evaluation] Invalid expression type: {type(expr)}")
        return None
    
    # Check for potentially dangerous keywords (basic security)
    dangerous_keywords = ['import', 'exec', 'eval', 'open', '__']
    if any(keyword in expr for keyword in dangerous_keywords):
        print(f"[evaluation] Potentially unsafe expression blocked: {expr}")
        return None
    
    try:
        return eval(expr, {"__builtins__": {}}, env)  # Restrict builtins for safety
    except (SyntaxError, NameError, TypeError, ValueError, ZeroDivisionError) as e:
        print(f"[evaluation] Error evaluating '{expr}': {type(e).__name__}: {e}")
        return None
    except Exception as e:
        print(f"[evaluation] Unexpected error evaluating '{expr}': {type(e).__name__}: {e}")
        return None


def kinda_assign(var, expr):
    value = evaluate(expr)
    if value is not None:
        if isinstance(value, (int, float)):
            value += random.choice([-1, 0, 1])
        env[var] = value
        print(f"[assign] {var} ~= {value}")
    else:
        print(f"[assign] {var} skipped (evaluation failed)")


def sorta_print(expr):
    """Print with fuzzy probability and proper error handling."""
    if random.random() < 0.8:
        try:
            result = eval(expr, {}, env)
            print(f"[print] {result}")
        except (SyntaxError, NameError, TypeError, ValueError) as e:
            print(f"[print] Error evaluating '{expr}': {type(e).__name__}: {e}")
        except Exception as e:
            print(f"[print] Unexpected error with '{expr}': {type(e).__name__}: {e}")
    else:
        print("[print] Skipped randomly")


def run_sometimes_block(condition, block_lines):
    if random.random() < 0.7:
        if evaluate(condition):
            for line in block_lines:
                from kinda.interpreter.__main__ import process_line

                process_line(line.strip())
        else:
            print("[sometimes] condition false")
    else:
        print("[sometimes] skipped randomly")

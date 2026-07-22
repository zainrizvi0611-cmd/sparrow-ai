import math
import re

def calculator(expr):
    # Convert "10!" to "factorial(10)"
    def replace_factorial(match):
        num = match.group(1)
        return f"factorial({num})"
    
    # Replace patterns like 5! , 10! , etc.
    expr = re.sub(r'(\d+)!', replace_factorial, expr)
    
    try:
        allowed = {
            "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
            "pow": pow, "factorial": math.factorial,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "exp": math.exp,
            "abs": abs, "round": round, "sum": sum, "len": len
        }
        result = eval(expr, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"Math Error: {e}"

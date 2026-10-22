from engbot.core.registry import register_tool


class SymPyTool:
    name = "sympy"
    description = ("Exact symbolic math. Evaluates a Python/SymPy expression and returns the result. "
                   "Pre-imported: `from sympy import *`. E.g. solve(x**2-4,x), integrate(sin(x),x), Matrix([[1,2],[3,4]]).det()")
    args_schema = {"code": "SymPy expression or short script; last expression or variable `result` is returned"}

    def run(self, code: str) -> str:
        import sympy
        ns = {k: getattr(sympy, k) for k in dir(sympy) if not k.startswith("_")}
        ns["x"], ns["y"], ns["z"], ns["t"] = sympy.symbols("x y z t")
        code = code.strip()
        try:
            return str(eval(code, ns))
        except SyntaxError:
            lines = code.splitlines()
            exec("\n".join(lines[:-1]), ns)
            return str(ns["result"]) if "result" in ns else str(eval(lines[-1], ns))


register_tool(SymPyTool())

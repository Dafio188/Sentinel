from typing import Any, Dict, List, Union

UNKNOWN = "UNKNOWN"

DSLResult = Union[bool, int, float, str, List[Any], dict]

class RuleDSLEvaluator:
    @staticmethod
    def is_unknown(val: Any) -> bool:
        return val == UNKNOWN or val is None

    @classmethod
    def evaluate(cls, expr: Any, context: Dict[str, Any]) -> Any:
        if not isinstance(expr, dict):
            return expr

        if len(expr) != 1:
            raise ValueError(f"Invalid expression dictionary structure: {expr}")

        op = next(iter(expr))
        args = expr[op]

        if op == "var":
            var_name = args if isinstance(args, str) else args[0]
            val = context.get(var_name)
            if val is None or val == UNKNOWN:
                return UNKNOWN
            return val

        if op == "!":
            sub_expr = args if not isinstance(args, list) else args[0]
            val = cls.evaluate(sub_expr, context)
            if cls.is_unknown(val):
                return UNKNOWN
            return not bool(val)

        if op == "and":
            eval_args = [cls.evaluate(a, context) for a in args]
            has_unknown = False
            for a in eval_args:
                if a is False:
                    return False
                if cls.is_unknown(a):
                    has_unknown = True
            return UNKNOWN if has_unknown else True

        if op == "or":
            eval_args = [cls.evaluate(a, context) for a in args]
            has_unknown = False
            for a in eval_args:
                if a is True:
                    return True
                if cls.is_unknown(a):
                    has_unknown = True
            return UNKNOWN if has_unknown else False

        if op in ("==", "!=", ">", ">=", "<", "<=", "in"):
            if not isinstance(args, list) or len(args) != 2:
                raise ValueError(f"Operator {op} requires exactly 2 arguments")
            left = cls.evaluate(args[0], context)
            right = cls.evaluate(args[1], context)

            if cls.is_unknown(left) or cls.is_unknown(right):
                return UNKNOWN

            if op == "==":
                return left == right
            elif op == "!=":
                return left != right
            elif op == ">":
                return left > right
            elif op == ">=":
                return left >= right
            elif op == "<":
                return left < right
            elif op == "<=":
                return left <= right
            elif op == "in":
                if isinstance(right, (list, tuple, set, str)):
                    return left in right
                return UNKNOWN

        if op == "+":
            eval_args = [cls.evaluate(a, context) for a in args]
            total = 0
            for a in eval_args:
                if cls.is_unknown(a):
                    return UNKNOWN
                total += a
            return total

        if op == "if":
            if not isinstance(args, list) or len(args) < 2:
                raise ValueError("Operator 'if' requires at least 2 arguments [cond, true_branch, false_branch]")
            cond_val = cls.evaluate(args[0], context)
            if cls.is_unknown(cond_val):
                return UNKNOWN
            if bool(cond_val):
                return cls.evaluate(args[1], context)
            else:
                if len(args) >= 3:
                    return cls.evaluate(args[2], context)
                return False

        raise ValueError(f"Unsupported DSL operator: {op}")

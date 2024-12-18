import ast
import asyncio
from functools import wraps
import inspect
import re

from .orko_context import OrkoContext


def orko(f):
    """
    Decorator that modifies the AST of a function to add print statements for assignments.
    """

    def emitAssignments(tree):
        class AssignmentEmitter(ast.NodeTransformer):
            def visit_Assign(self, node):
                targets = [
                    target.id for target in node.targets if isinstance(target, ast.Name)
                ]

                trace_statements = []
                for target in targets:
                    formatted_value = ast.FormattedValue(
                        value=ast.Name(id=target, ctx=ast.Load()),
                        conversion=-1,
                        format_spec=None,
                    )

                    joined_str = ast.JoinedStr(
                        values=[
                            ast.Constant(
                                value=f"assignment: {target} = "
                            ),  # Literal string
                            formatted_value,
                        ]
                    )

                    trace_call = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="context", ctx=ast.Load()),  # Use the `context` instance
                            attr="addTrace",
                            ctx=ast.Load(),
                        ),
                        args=[joined_str],
                        keywords=[],
                    )

                    trace_statements.append(ast.Expr(value=trace_call))

                return [node] + trace_statements

            def visit_AugAssign(self, node):
                # Handle augmented assignments (a += b)
                target = node.target
                if isinstance(target, ast.Name):
                    formatted_value = ast.FormattedValue(
                        value=ast.Name(id=target.id, ctx=ast.Load()),
                        conversion=-1,
                        format_spec=None,
                    )

                    joined_str = ast.JoinedStr(
                        values=[
                            ast.Constant(
                                value=f"augmented assignment: {target.id} = "
                            ),  # Literal string
                            formatted_value,
                        ]
                    )

                    trace_call = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="context", ctx=ast.Load()),
                            attr="addTrace",
                            ctx=ast.Load(),
                        ),
                        args=[joined_str],
                        keywords=[],
                    )

                    return [node, ast.Expr(value=trace_call)]
                return node

        # Apply the transformer to the AST
        tree = AssignmentEmitter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


    def removeOrkoResultAssignment(tree):
        """Remove the final assignment to `orkoResult`."""
        if isinstance(tree.body[-1], ast.Assign):
            last_node = tree.body[-1]
            if (
                isinstance(last_node.targets[0], ast.Name)
                and last_node.targets[0].id == "orkoResult"
            ):
                tree.body.pop()  # Remove the final assignment
        return tree

    @wraps(f)
    def wrapper(*args, **kwargs):
        context = OrkoContext.getOrCreate()

        # Modify source code to return result
        source = inspect.getsource(f)

        # Remove orko decorator
        source = re.sub(r"^\s*@orko(\(.*\))?\s*$", "", source, flags=re.MULTILINE)

        funcNameMatch = re.search(
            r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", source, flags=re.MULTILINE
        )
        if funcNameMatch is None:
            raise ValueError("Ooops, something went very wrong!")
        funcName = funcNameMatch.group(1)
        args_str = ", ".join(repr(arg) for arg in args)
        kwargs_str = ", ".join(f"{key}={repr(value)}" for key, value in kwargs.items())

        source += f"\norkoResult = {funcName}({args_str}, {kwargs_str})"

        # Inject emitters
        tree = ast.parse(source)
        newTree = emitAssignments(tree)
        finalTree = removeOrkoResultAssignment(newTree)
        newF = compile(finalTree, filename="<ast>", mode="exec")


        # Execute the wrapper function
        execContext = {**globals(), **{"args": args, "kwargs": kwargs}, "context": context}
        exec(newF, execContext)
        result = execContext.get("orkoResult")

        context.tellStory()

        return result

    return wrapper

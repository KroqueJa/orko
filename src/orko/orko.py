import ast
from functools import wraps
import inspect
import re

from .orko_context import OrkoContext
from .parse.assignment_emitter import AssignmentEmitter


def orko(f):
    """
    Decorator that modifies the AST of a function to add print statements for assignments.
    """

    def emitAssignments(tree):

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

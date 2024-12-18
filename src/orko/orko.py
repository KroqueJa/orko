import ast
import asyncio
from functools import wraps

from .orko_context import OrkoContext

def orko(f):
    """
    The main decorator. Orko attempts to insert monitoring hooks into the decorated function, which
    are asynchronously emitted into the OrkoContext. The two wrappers ensure that it always runs async.
    """
    @wraps(f)
    async def asyncWrapper(*args, **kwargs):
        context = OrkoContext.getOrCreate()
        result = await f(*args, **kwargs)
        await context.addTrace(f"Function {f.__name__} executed with result: {result}")
        return result

    @wraps(f)
    def syncWrapper(*args, **kwargs):
        context = OrkoContext.getOrCreate()
        result = f(*args, **kwargs)

        loop = asyncio.get_running_loop()
        loop.create_task(context.addTrace(f"Function {f.__name__} executed with result: {result}"))

        return result

    return asyncWrapper if asyncio.iscoroutinefunction(f) else syncWrapper

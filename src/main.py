import asyncio

from orko import orko


@orko
async def asyncFunction(x):
    """An example asynchronous function."""
    a = x * 2
    return a + 1

@orko
def syncFunction(x):
    """An example synchronous function."""
    a = x + 2
    return a


globalVariable = 0

@orko
def mutatesGlobal(x, y):
    """An example function that mutates global state."""
    global globalVariable 
    globalVariable += x
    a = x + y
    return a

async def main():
    await asyncFunction(5)
    syncFunction(3)
    mutatesGlobal(11, 8)

asyncio.run(main())

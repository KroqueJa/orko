from orko import orko


@orko
def syncFunction(x):
    """An example synchronous function."""
    a = x + 2

    if a % 2 == 0:
        b = 74
    else:
        b = 12

    b += 11
    a += b

    print("Heyoooo!")
    return a

'''
@orko
async def asyncFunction(x):
    """An example asynchronous function."""
    a = x * 2
    return a + 1


Global variables currently don't work, as we don't know how to have them be present in the call to the modified function
globalVariable = 0

@orko
def mutatesGlobal(x, y):
    """An example function that mutates global state."""
    global globalVariable 
    globalVariable += x
    a = x + y
    return a
'''

def main():
    syncFunction(3)
    # await asyncFunction(5)
    # mutatesGlobal(11, 8)

main()

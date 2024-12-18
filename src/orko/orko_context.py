import asyncio


class OrkoContext:
    _instance = None

    def __init__(self):
        self.traces = []

    @classmethod
    def getOrCreate(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def addTrace(self, trace):
        # Simulate an async operation (e.g., database or network call)
        print(f"Adding trace asynchronously: {trace}")
        self.traces.append(trace)

class OrkoContext:
    _instance = None

    def __init__(self):
        self.traces = []

    @classmethod
    def getOrCreate(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # TODO: Make async when appropriate
    def addTrace(self, trace):
        self.traces.append(trace)

    def tellStory(self):
        for trace in self.traces:
            if not "orkoResult" in trace:
                print(trace)

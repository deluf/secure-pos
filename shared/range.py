class Range:
    """
    Value Object representing a range of values and a step within the range
    """

    def __init__(self, min: int, max: int, step: int):
        self.min = min
        self.max = max
        self.step = step

def addInteger(self, x):
    self.numIntegers += 1
    self.integers.updateSize()
    self.integers[self.numIntegers-1] = x

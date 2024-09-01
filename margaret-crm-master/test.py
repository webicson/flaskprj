from random import random

class WeightedChooser1(object):
    def __init__(self):
        self.values = []
        self.weights = []
        self.probabilities = []

    def add(self, weight, val):
        self.values.append(val)
        self.weights.append(weight)

        self.probabilities = []
        weights_sum = sum(self.weights)
        self.probabilities = [i * (1 / weights_sum) for i in self.weights]

    def choose(self):
        rand = random()
        pos = 0
        summy = 0
        for x in range(0, len(self.probabilities)):
            pos = x
            summy = summy + self.probabilities[x]
            if summy > rand:
                break
        return self.values[pos]

class WeightedChooser2(object):
    def __init__(self):
        self.values = []

    def add(self, weight, val):
        for x in range(0, weight):
            self.values.append(val)

    def choose(self):
        pos = int(random() * len(self.values))
        return self.values[pos]

# chooser = WeightedChooser1()
# chooser.add(5, "nym")
# chooser.add(10, "health")
# for x in range(0, 10):
#     print(chooser.choose())


chooser = WeightedChooser2()
chooser.add(8, "nym")
chooser.add(2, "health")
chooser.add(4, "22222")
chooser.add(6, "535643434")
for x in range(0, 20):
    print(chooser.choose())
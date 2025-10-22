import numpy as np

class GameOfLife1D:
    def __init__(self, length=200, rule=30):
        self.length = length
        self.rule = rule
        self.rule_map = self._rule_to_map(rule)
        self.state = np.zeros(length, dtype=int)
        self.state[length // 2] = 1

    def _rule_to_map(self, rule):
        bits = [(rule >> i) & 1 for i in range(8)]
        triplets = [(1,1,1),(1,1,0),(1,0,1),(1,0,0),(0,1,1),(0,1,0),(0,0,1),(0,0,0)]
        return {triplets[i]: bits[7-i] for i in range(8)}

    def step(self):
        new = np.zeros_like(self.state)
        for i in range(self.length):
            left = self.state[(i-1) % self.length]
            center = self.state[i]
            right = self.state[(i+1) % self.length]
            new[i] = self.rule_map[(left, center, right)]
        self.state = new

    def reset(self, seed=None):
        self.state = np.zeros(self.length, dtype=int)
        if seed is None:
            self.state[self.length // 2] = 1
        else:
            self.state = np.array(seed, dtype=int)
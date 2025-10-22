import random
import numpy as np

class CovidSimulation:
    # States: 0=empty, 1=susceptible, 2=infected, 3=recovered, 4=dead
    def __init__(self, rows=60, cols=60, init_infected=5, p_infect=0.3, p_recover=0.02, p_die=0.005):
        self.rows = rows
        self.cols = cols
        self.grid = np.ones((rows, cols), dtype=int)
        self.t = 0
        self.p_infect = p_infect
        self.p_recover = p_recover
        self.p_die = p_die
        for _ in range(init_infected):
            r = random.randrange(rows)
            c = random.randrange(cols)
            self.grid[r, c] = 2

    def step(self):
        new = self.grid.copy()
        for r in range(self.rows):
            for c in range(self.cols):
                state = self.grid[r, c]
                if state == 1:
                    neigh = self.grid[max(0, r-1):r+2, max(0, c-1):c+2]
                    infected_neighbors = np.sum(neigh == 2)
                    if infected_neighbors > 0:
                        p = 1 - ((1 - self.p_infect) ** infected_neighbors)
                        if random.random() < p:
                            new[r, c] = 2
                elif state == 2:
                    if random.random() < self.p_die:
                        new[r, c] = 4
                    elif random.random() < self.p_recover:
                        new[r, c] = 3
        self.grid = new
        self.t += 1

    def counts(self):
        unique, counts = np.unique(self.grid, return_counts=True)
        d = {k:0 for k in range(5)}
        for u, c in zip(unique, counts):
            d[int(u)] = int(c)
        return d
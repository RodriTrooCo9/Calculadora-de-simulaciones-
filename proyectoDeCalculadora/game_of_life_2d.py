import numpy as np

class GameOfLife2D:
    def __init__(self, rows=50, cols=50):
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=int)

    def randomize(self, p=0.2):
        self.grid = (np.random.random((self.rows, self.cols)) < p).astype(int)

    def step(self):
        new = np.zeros_like(self.grid)
        for r in range(self.rows):
            for c in range(self.cols):
                total = np.sum(self.grid[max(0, r-1):r+2, max(0, c-1):c+2]) - self.grid[r, c]
                if self.grid[r, c] == 1:
                    if total == 2 or total == 3:
                        new[r, c] = 1
                else:
                    if total == 3:
                        new[r, c] = 1
        self.grid = new
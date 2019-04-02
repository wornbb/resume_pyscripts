import numpy as np
from assistant import assistant
import os.path as opath

class vpManager():
    def __init__(self):
        self.grid = dict()
    def loadGrid(self, file):
        # open a new file or select from opened file
        if file in self.grid:
            f = self.grid[file]
        else:
            f = open(file, 'r')
            self.grid[file] = f
        # get next line
        flatLine = f.readline()
        # if EOF
        if flatLine == '':
            return 0
        else:
            matrix = self.str2m(flatLine)
            return matrix
    def str2m(self, line):
        flatMatrix = np.fromstring(line, dtype=float, sep=' ')
        length = flatMatrix.size
        gridSize = np.sqrt(length).astype(int)
        matrix = flatMatrix.reshape((gridSize, gridSize)).T
        return matrix
    def batchGrid(self, gfile):
        matrices = []
        with open(gfile, 'r') as f:
            for line in f:
                matrix = self.str2m(line)
                matrices.append(matrix)
        return matrices
        
        

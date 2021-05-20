import sys
import traci

class JunctionCell:
    def __init__(self, topLeft, bottomRight):
        self.topLeft = topLeft
        self.bottomRight = bottomRight
        self.shape = (\
            topLeft[0], topLeft[1],\
            topLeft[0], bottomRight[1],\
            bottomRight[0], bottomRight[1],\
            bottomRight[0], topLeft[1]\
        )

class Junction:
    def __init__(self, id):
        self.shape = traci.junction.getShape(id)
        self.cells = self.__setupGrid()

    def __setupGrid(self, numCells = 20):
        left = sys.float_info.max
        right = sys.float_info.min
        down = sys.float_info.max
        up = sys.float_info.min
        for coord in self.shape:
            if coord[0] < left:
                left = coord[0]
            if coord[0] > right:
                right = coord[0]
            if coord[1] < down:
                down = coord[1]
            if coord[1] > up:
                up = coord[1]

        width = right - left
        height = up - down
        widthIncrement = width / numCells
        heightIncrement = height / numCells

        cells = []
        for row in range(0, numCells):
            cellRow = []
            cells.append(cellRow)
            for col in range(0, numCells):
                cellRow.append(JunctionCell( \
                    (left + widthIncrement * row, down + heightIncrement * col),\
                    (left + widthIncrement * (row + 1), down + heightIncrement * (col + 1))\
                ))

        return cells

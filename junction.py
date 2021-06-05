import sys
import traci
import typing
from typing import Tuple
import collision

Coordinates = Tuple[float, float]

class JunctionCell:
    def __init__(self, id: str, topLeft: Coordinates, bottomRight: Coordinates):
        self.id = id
        self.topLeft = topLeft
        self.bottomRight = bottomRight
        self.shape = (\
            topLeft[0], topLeft[1],\
            topLeft[0], bottomRight[1],\
            bottomRight[0], bottomRight[1],\
            bottomRight[0], topLeft[1]\
        )
        self.boundingBox = collision.Poly.from_box(
            ((topLeft[0] + bottomRight[0]) / 2, (topLeft[1] + bottomRight[1]) / 2),
            bottomRight[0] - topLeft[0],
            topLeft[1] - bottomRight[1]
        )

class Junction:
    def __init__(self, id: str):
        self.shape: list[Coordinates] = traci.junction.getShape(id)
        self.cells: list[JunctionCell] = self.__setupGrid()

    def __setupGrid(self, numCells: int = 20) -> list[Coordinates]:
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
            for col in range(0, numCells):
                cells.append(JunctionCell( \
                    f"x{col}y{row}", \
                    (left + widthIncrement * row, down + heightIncrement * col),\
                    (left + widthIncrement * (row + 1), down + heightIncrement * (col + 1))\
                ))

        return cells

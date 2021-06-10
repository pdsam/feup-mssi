import sys
import traci
import typing
from typing import Tuple
import collision
from simTypes import Coordinates

class Reservation:
    def __init__(self, timeStart: float, timeEnd: float, vehicleId: str):
        self.timeStart: float = timeStart
        self.timeEnd: float = timeEnd
        self.vehicleId: str = vehicleId

class Schedule:
    def __init__(self, cellId: str):
        self.cellId: str = cellId
        self.reservations: dict[str, Reservation] = {}

    def canAdd(self, toCheck: Reservation) -> bool:
        for vehId, reservation in self.reservations.items():
            overlap = toCheck.timeStart < reservation.timeEnd and toCheck.timeEnd > reservation.timeStart
            if overlap:
                return False

        return True

    def clearVehicleReservations(self, vehicleId: str):
        if vehicleId in self.reservations:
            del self.reservations[vehicleId]

    def addReservation(self, toAdd: Reservation):
        self.reservations[toAdd.vehicleId] = toAdd

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
        self.schedules: dict[str, Schedule] = {}

        for cell in self.cells:
            self.schedules[cell.id] = Schedule(cell.id)

    def requestReservations(self, reservations: dict[str, Reservation]) -> bool:
        for cellId, reservation in reservations.items():
            schedule = self.schedules[cellId]
            if not schedule.canAdd(reservation):
                return False
        
        for cellId, reservation in reservations.items():
            schedule = self.schedules[cellId]
            schedule.addReservation(reservation)

        return True

    def notifyLeaving(self, vehicleId: str):
        for schedule in self.schedules.values():
            schedule.clearVehicleReservations(vehicleId)

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

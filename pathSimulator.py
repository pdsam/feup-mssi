import typing
from typing import Tuple
import collision as cl
from vehicles import Vehicle
from junction import Junction, JunctionCell
from network import Lane
from simTypes import Coordinates, PosAndRotation

class StepInfo:
    def __init__(self, time: float, pos: Coordinates, rotation: float, cells: list[JunctionCell]):
        self.time = time
        self.pos = pos
        self.rotation = rotation
        self.cells = cells

class PathSimulator:
    def __init__(self, junction: Junction, vehicle: Vehicle, viaLane: Lane, timestep: float, baseTime: float = 0):
        self.junction = junction
        self.vehicle = vehicle
        self.viaLane = viaLane
        self.baseTime = baseTime
        self.timestep = timestep

        self.currentTime = baseTime
        self.currentSpeed = 0
        self.currentDistance = 0
        self.done = False

    def reset(self):
        self.currentTime = baseTime
        self.currentSpeed = 0
        self.currentDistance = 0
        self.done = False

    def isDone(self):
        return self.done

    def step(self) -> Tuple[PosAndRotation, list[JunctionCell]]:
        posAndRotation = self.viaLane.getPositionAndOrientation(self.currentDistance)

        if posAndRotation is None:
            self.done = True
            return None

        pos = posAndRotation[0]
        rotation = posAndRotation[1]

        vehicleBox = cl.Poly.from_box(pos, self.vehicle.width, self.vehicle.length)
        vehicleBox.angle = -rotation

        collidingCells = []
        for cell in self.junction.cells:
            if cl.test_poly_poly(vehicleBox, cell.boundingBox):
                collidingCells.append(cell)

        info = StepInfo(self.currentTime, pos, rotation, collidingCells)

        self.currentSpeed += self.vehicle.acceleration * self.timestep
        self.currentDistance += self.currentSpeed * self.timestep
        self.currentTime += self.timestep
    
        return info

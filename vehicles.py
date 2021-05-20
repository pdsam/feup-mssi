import traci
import traci.constants as tc
from enum import Enum

class VehicleState(Enum):
    APROACHING = 1
    WAITING = 2
    CROSSING = 3
    LEAVING = 4

class Vehicle:
    def __init__(self, id):
        self.id = id
        self.state = VehicleState.APROACHING
        self.speed = 0
        self.lanePosition = 0
        self.currentLaneId = None
        self.waitingCounter = 0

    def getLeader(self):
        return traci.vehicle.getLeader(self.id)

    def setSpeed(self, speed):
        traci.vehicle.setSpeed(self.id, speed)

    def setState(self, state):
        if state == VehicleState.WAITING:
            print(f"{self.id} is now waiting")
        self.state = state

class VehicleManager(traci.StepListener):
    def __init__(self, junctionID):
        self.vehicles = dict()
        self.junctionID = junctionID

    def getVehicle(self, id):
        return self.vehicles[id]

    def step(self, t):
        # Register departing vehicles
        loaded = traci.simulation.getDepartedIDList()
        for vehicleID in loaded:
            print(f"Adding {vehicleID}")
            self.vehicles[vehicleID] = Vehicle(vehicleID)

        # Update values of current vehicles
        vehicles = traci.junction.getContextSubscriptionResults(self.junctionID)
        for vehicleID in vehicles:
            vehicle = self.vehicles[vehicleID]
            vehicle.speed = vehicles[vehicleID][tc.VAR_SPEED]
            vehicle.lanePosition = vehicles[vehicleID][tc.VAR_LANEPOSITION]
            vehicle.currentLaneId = vehicles[vehicleID][tc.VAR_LANE_ID]

        # Deregister arrived vehicles
        arrived = traci.simulation.getArrivedIDList()
        for vehicleID in arrived:
            print(f"Removing {vehicleID}")
            self.vehicles.pop(vehicleID)

        return True

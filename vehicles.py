import traci
import traci.constants as tc
from enum import Enum
from logger import Logger
import typing

class VehicleState(Enum):
    APROACHING = 1
    WAITING = 2
    CROSSING = 3
    LEAVING = 4
    SCHEDULING = 5
    START_CROSSING = 6

class Vehicle:
    def __init__(self, id):
        self.id: str = id
        self.state: VehicleState = VehicleState.APROACHING
        self.platoonState: PlatoonState = PlatoonState.INDEPENDENT
        self.goTime: float = 0
        self.viaLaneId: str = None
        self.speed: float = 0
        self.lanePosition: float = 0
        self.currentLaneId: str = None
        self.currentLaneIndex: int = None
        self.currentEdgeId: str = None
        self.width: float = traci.vehicle.getWidth(id)
        self.length: float = traci.vehicle.getLength(id)
        self.acceleration: float = traci.vehicle.getAccel(id)

    def getLeader(self):
        return traci.vehicle.getLeader(self.id)

    def setSpeed(self, speed):
        traci.vehicle.setSpeed(self.id, speed)

    def stop(self):
        traci.vehicle.setSpeed(self.id, 0)

    def go(self):
        traci.vehicle.setSpeed(self.id, -1)

    def getNextHop(self):
        edges = traci.vehicle.getRoute(self.id)
        return edges[1]

    def setState(self, state):
        self.state = state

class VehicleManager(traci.StepListener):
    def __init__(self, junctionID):
        self.vehicles: dict[str: Vehicle] = dict()
        self.junctionID: str = junctionID
        self.arrived: int = 0

        traci.junction.subscribeContext(junctionID, \
            tc.CMD_GET_VEHICLE_VARIABLE, 50, \
            [\
                tc.VAR_ROAD_ID, \
                tc.VAR_LANE_INDEX, \
                tc.VAR_LANE_ID, \
                tc.VAR_LANEPOSITION, \
                tc.VAR_SPEED, \
            ])


    def getVehicle(self, id: str) -> Vehicle:
        return self.vehicles[id]

    def __updateVehicle(self, vehicleId, data):
        vehicle = self.vehicles[vehicleId]

        vehicle.speed = data[tc.VAR_SPEED]
        vehicle.lanePosition = data[tc.VAR_LANEPOSITION]
        vehicle.currentLaneId = data[tc.VAR_LANE_ID]
        vehicle.currentLaneIndex = data[tc.VAR_LANE_INDEX]
        vehicle.currentEdgeId = data[tc.VAR_ROAD_ID]

    def step(self, t):
        # Register departing vehicles
        loaded = traci.simulation.getDepartedIDList()
        for vehicleID in loaded:
            Logger.log(f"Adding {vehicleID}")
            self.vehicles[vehicleID] = Vehicle(vehicleID)

        # Update values of current vehicles
        vehicles = traci.junction.getContextSubscriptionResults(self.junctionID)
        for vehicleID in vehicles:
            self.__updateVehicle(vehicleID, vehicles[vehicleID])

        # Deregister arrived vehicles
        arrived = traci.simulation.getArrivedIDList()
        self.arrived += len(arrived)
        for vehicleID in arrived:
            Logger.log(f"Removing {vehicleID}")
            self.vehicles.pop(vehicleID)

        return True

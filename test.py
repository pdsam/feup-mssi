import traci
import traci.constants as tc
import os
import xml.etree.ElementTree as ET
from collections import Counter
from enum import Enum

dir = os.path.dirname(__file__)

network_path = os.path.join(dir, "networks/basic-test.net.xml")
demand_path = os.path.join(dir, "networks/basic-demand.rou.xml")
#additionals = os.path.join(dir, "networks/basic_bi.add.xml")

network = ET.parse(network_path)
print(network)

junctionID = "gneJ0"
junction_object = network.find(f'junction[@id=\'{junctionID}\']')
incoming_lanes = junction_object.attrib['incLanes']

traci.start(["sumo-gui", "-d", "250", "-n", network_path, "-r", demand_path])

traci.junction.subscribeContext(junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 25, \
    [tc.VAR_ROAD_ID, tc.VAR_LANE_INDEX, tc.VAR_LANE_ID, tc.VAR_LANEPOSITION, \
        tc.VAR_SPEED])

step = 1

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

        # Deregister arrived vehicles
        arrived = traci.simulation.getArrivedIDList()
        for vehicleID in arrived:
            print(f"Removing {vehicleID}")
            self.vehicles.pop(vehicleID)

        return True

vehicleManager = VehicleManager(junctionID)
traci.addStepListener(vehicleManager)

def handleVehicle(vehicle):
    if vehicle.state == VehicleState.APROACHING:
        # TODO(mpdr): this is a hard coded value, will want to replace for a dynamically calculated one
        if vehicle.speed < 0.8 and vehicle.getLeader() == None and vehicle.lanePosition > 41:
            """ Hold vehicle when it stops at the junction """
            vehicle.setSpeed(0)
            vehicle.setState(VehicleState.WAITING)

    elif vehicle.state == VehicleState.WAITING:
        """ Hold vehicle for 20 ticks, then let it go """
        if vehicle.waitingCounter > 20:
            vehicle.setSpeed(10)
            vehicle.waitinCounter = 0
            vehicle.setState(VehicleState.CROSSING)
        else:
            vehicle.setSpeed(0)
            vehicle.waitingCounter += 1

while traci.simulation.getMinExpectedNumber() > 0:
    print("step", step)

    traci.simulationStep()

    vehicles = traci.junction.getContextSubscriptionResults(junctionID)
    for vehicleID in vehicles:
        vehicle = vehicleManager.getVehicle(vehicleID)
        handleVehicle(vehicle)
        

    step += 1

traci.close()


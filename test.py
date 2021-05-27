import traci
import traci.constants as tc
import os
import xml.etree.ElementTree as ET
import vehicles
import easygraphics as eg
from vehicles import *
from junction import *
from graphics import createRenderFunction
from logger import Logger

dir = os.path.dirname(__file__)

network_path = os.path.join(dir, "networks/basic-test.net.xml")
demand_path = os.path.join(dir, "networks/basic-demand.rou.xml")
#additionals = os.path.join(dir, "networks/basic_bi.add.xml")

junctionID = "gneJ0"

network = ET.parse(network_path)
junction_object = network.find(f'junction[@id=\'{junctionID}\']')
incoming_lanes = junction_object.attrib['incLanes']

traci.start(["sumo-gui", "-d", "250", "-n", network_path, "-r", demand_path])
junctionOfInterest = Junction(junctionID)

vehicleManager = vehicles.VehicleManager(junctionID)
traci.addStepListener(vehicleManager)

connection_objects = network.findall('connection')
print(connection_objects)
vias = {}
for conn in connection_objects:
    if 'via' not in conn.attrib:
        continue
    fromEdge = conn.attrib['from']
    fromLane = conn.attrib['fromLane']
    toEdge = conn.attrib['to']

    id = f"{fromEdge}:::{fromLane}:::{toEdge}";
    print(id)
    vias[id] = conn.attrib['via']


# Test if the grid creation code is working
# eg.easy_run(createRenderFunction(junctionOfInterest))

def handleVehicle(vehicle):
    if vehicle.state == VehicleState.APROACHING:
        laneLength = traci.lane.getLength(vehicle.currentLaneId)
        if vehicle.speed < 0.8 and vehicle.getLeader() == None and vehicle.lanePosition > laneLength - 1.5:
            """ Hold vehicle when it stops at the junction """
            vehicle.stop()
            vehicle.setState(VehicleState.SCHEDULING)
            # TODO(mpdr): add vehicle to junction queues?
            Logger.log(f"{vehicle.id} is now scheduling")
    elif vehicle.state == VehicleState.SCHEDULING:
        """ 
        Schedule the vehicle's crossing, steps:
            - find destination lane
            - get via lane and respective shape
            - emulate vehicle over path
            - resolve conflicts
        """
        vehicle.goTime = 0 # reset schedule
        nextHop = vehicle.getNextHop()
        viaLane = vias[f"{vehicle.currentEdgeId}:::{vehicle.currentLaneIndex}:::{nextHop}"]
        print(viaLane)

        pass
    elif vehicle.state == VehicleState.WAITING:
        """ Hold vehicle for 20 ticks, then let it go """
        if vehicle.waitingCounter > 20:
            vehicle.go()
            vehicle.waitinCounter = 0
            vehicle.setState(VehicleState.CROSSING)
        else:
            vehicle.waitingCounter += 1

def runSimulation():
    while traci.simulation.getMinExpectedNumber() > 0:
        Logger.incrementStep()
        traci.simulationStep()

        vehicles = traci.junction.getContextSubscriptionResults(junctionID)
        for vehicleID in vehicles:
            vehicle = vehicleManager.getVehicle(vehicleID)
            handleVehicle(vehicle)
            

runSimulation()

traci.close()


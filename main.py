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
from network import Network
from test import testPathSimulation

dir = os.path.dirname(__file__)

network_path = os.path.join(dir, "networks/basic-test.net.xml")
demand_path = os.path.join(dir, "networks/basic-demand.rou.xml")

junctionID = "gneJ0"

networkFile = ET.parse(network_path)

junctionNode = networkFile.find(f'junction[@id=\'{junctionID}\']')
incomingLaneIds = junctionNode.attrib['incLanes']

traci.start(["sumo", "-d", "250", "-n", network_path, "-r", demand_path])
junction = Junction(junctionID)
network = Network(networkFile)

vehicleManager = vehicles.VehicleManager(junctionID)
traci.addStepListener(vehicleManager)

# Test if the grid creation code is working
# eg.easy_run(createRenderFunction(junction))

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
            - find destination lane - Done
            - get via lane and respective shape - Done
            - emulate vehicle over path
            - resolve conflicts
        """
        vehicle.goTime = 0 # reset schedule
        nextHop = vehicle.getNextHop()
        viaLane = network.getEdge(vehicle.currentEdgeId).getViaLane(vehicle.currentLaneIndex, nextHop)

        print(viaLane.id, viaLane.shape)
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
            

eg.easy_run(testPathSimulation(network, junction))

# runSimulation()

traci.close()


import traci
import traci.constants as tc
import os
import xml.etree.ElementTree as ET
import vehicles
import easygraphics as eg
from vehicles import *
from junction import *
from graphics import createRenderFunction

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

traci.junction.subscribeContext(junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 25, \
    [tc.VAR_ROAD_ID, tc.VAR_LANE_INDEX, tc.VAR_LANE_ID, tc.VAR_LANEPOSITION, \
        tc.VAR_SPEED])

vehicleManager = vehicles.VehicleManager(junctionID)
traci.addStepListener(vehicleManager)

# Test if the grid creation code is working
eg.easy_run(createRenderFunction(junctionOfInterest))

def handleVehicle(vehicle):
    if vehicle.state == VehicleState.APROACHING:
        # TODO(mpdr): this is a hard coded value, will want to replace for a dynamically calculated one
        laneLength = traci.lane.getLength(vehicle.currentLaneId)
        if vehicle.speed < 0.8 and vehicle.getLeader() == None and vehicle.lanePosition > laneLength - 1.5:
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

def runSimulation():
    step = 1
    while traci.simulation.getMinExpectedNumber() > 0:
        print("step", step)

        traci.simulationStep()

        vehicles = traci.junction.getContextSubscriptionResults(junctionID)
        for vehicleID in vehicles:
            vehicle = vehicleManager.getVehicle(vehicleID)
            handleVehicle(vehicle)
            

        step += 1

runSimulation()

traci.close()


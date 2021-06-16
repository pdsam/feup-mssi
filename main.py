import traci
import math
import traci.constants as tc
import os
import xml.etree.ElementTree as ET
import vehicles
import easygraphics as eg
from vehicles import *
from junction import *
from logger import Logger
from network import Network
from test import testPathSimulation
from visualizer import visualizePathSimulation
from pathSimulator import PathSimulator

dir = os.path.dirname(__file__)

network_path = os.path.join(dir, "networks/basic/network.net.xml")
demand_path = os.path.join(dir, "networks/basic/demand-bench.rou.xml")

junctionID = "gneJ0"

networkFile = ET.parse(network_path)

junctionNode = networkFile.find(f'junction[@id=\'{junctionID}\']')

traci.start(["sumo-gui", "--step-length", "0.250", "-d", "0", "-n", network_path, "-r", demand_path])
simulationStepLength = traci.simulation.getDeltaT()
print(f"Timestep = {simulationStepLength}")
junction = Junction(junctionID)
network = Network(networkFile)

vehicleManager = vehicles.VehicleManager(junctionID)
traci.addStepListener(vehicleManager)

Logger.setActive(True)

simulationTime = 0
def handleVehicle(vehicle: Vehicle):
    if vehicle.state == VehicleState.APROACHING or vehicle.state == VehicleState.IN_QUEUE:
        laneLength = traci.lane.getLength(vehicle.currentLaneId)
        if vehicle.speed < 0.8:
            if vehicle.getLeader() == None and vehicle.lanePosition > laneLength - 1.5:
                """ Hold vehicle when it stops at the junction """
                vehicle.stop()
                vehicle.setState(VehicleState.SCHEDULING)
                # TODO(mpdr): add vehicle to junction queues?
                Logger.log(f"{vehicle.id} is now scheduling")
            else:
                vehicle.setState(VehicleState.IN_QUEUE)
                junction.notifyEnteredQueue(vehicle)
                Logger.log(f"{vehicle.id} is now in queue")

    elif vehicle.state == VehicleState.SCHEDULING:
        """ 
        Schedule the vehicle's crossing, steps:
            - find destination lane - Done
            - get via lane and respective shape - Done
            - emulate vehicle over path - Done
            - resolve conflicts - Done
        """
        vehicle.goTime = 0 # reset schedule
        nextHop = vehicle.getNextHop()

        viaLane = network.getEdge(vehicle.currentEdgeId).getViaLane(vehicle.currentLaneIndex, nextHop)

        startTime = simulationTime + simulationStepLength
        sim = PathSimulator(junction, vehicle, viaLane, simulationStepLength, startTime)

        reservations: dict[str, Reservation] = {}

        # Time at which vehicle starts crossing
        goTime = math.inf
        # Emulate path and assemble reservations
        while(not sim.isDone()):
            stepInfo = sim.step()

            if stepInfo is None:
                break

            goTime = min(goTime, stepInfo.time)

            for cell in stepInfo.cells:
                if cell.id not in reservations:
                    reservations[cell.id] = Reservation(stepInfo.time, stepInfo.time + simulationStepLength, vehicle.id)
                else:
                    reservation = reservations[cell.id]
                    reservation.timeEnd = stepInfo.time + simulationStepLength

        # Resolve conflicts
        done = False
        while not done:
            done = junction.requestReservations(reservations)
            if not done:
                # advance reservation by t to resolve conflicts
                for cellId, reservation in reservations.items():
                    reservation.timeStart += simulationStepLength
                    reservation.timeEnd += simulationStepLength

                    goTime = min(goTime, reservation.timeStart)

        # Assign departure time to vehicle
        vehicle.goTime = goTime
        vehicle.viaLaneId = viaLane.id
        # Set vehicle to waitin
        vehicle.setState(VehicleState.WAITING)

        #visualizePathSimulation(network, junction, viaLane, vehicle, timeStep)

    elif vehicle.state == VehicleState.WAITING:
        if vehicle.goTime >= simulationTime:
            vehicle.go()
            vehicle.setState(VehicleState.START_CROSSING)
    elif vehicle.state == VehicleState.START_CROSSING:
        if vehicle.currentLaneId == vehicle.viaLaneId:
            vehicle.setState(VehicleState.CROSSING)
        pass
    elif vehicle.state == VehicleState.CROSSING:
        if vehicle.currentLaneId != vehicle.viaLaneId:
            junction.notifyLeaving(vehicle.id)
            vehicle.setState(VehicleState.LEAVING)
        pass


def runSimulation():
    #eg.init_graph(500,500)
    simulationTime = traci.simulation.getTime()
    Logger.resetStep()

    while Logger.step < 500:
        print("Step", Logger.step, end='\r')
        simulationTime = traci.simulation.getTime()
        traci.simulationStep()

        vehicles = traci.junction.getContextSubscriptionResults(junctionID)
        for vehicleID in vehicles:
            vehicle = vehicleManager.getVehicle(vehicleID)
            handleVehicle(vehicle)

        Logger.incrementStep()
            

#eg.easy_run(testPathSimulation(network, junction))

#eg.easy_run(runSimulation)
runSimulation()

print("Vehicles left", traci.simulation.getMinExpectedNumber())
print("Vehicles arrived", vehicleManager.arrived)

traci.close()


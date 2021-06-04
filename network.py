import typing
from typing import Tuple
import traci
import math
import numpy as np

class Lane:
    def __init__(self, laneNode):
        self.id = laneNode.attrib['id']
        self.index = int(laneNode.attrib['index'])
        self.shape = traci.lane.getShape(self.id)

        self.connections = {}

        self.length = 0
        self.sections = []
        for i in range(0, len(self.shape) - 1):
            dist = math.dist(self.shape[i], self.shape[i+1])
            self.length += dist
            self.sections.append((dist, (self.shape[i], self.shape[i+1])))

    def addConnection(self, destEdgeId: str, viaLane: 'Lane'):
        self.connections[destEdgeId] = viaLane;

    def getViaLane(self, destEdgeId: str) -> 'Lane':
        return self.connections[destEdgeId]

    def getPositionAndOrientation(self, distanceAlong: float) -> Tuple[Tuple[float, float], float]:
        if distanceAlong < 0:
            return None

        if distanceAlong > self.length:
            return None
        
        idx = 0
        for section in self.sections:
            # look for section in which the distance is within
            if section[0] <= distanceAlong:
                break;
            idx += 1
        else:
            # Couldn't find section
            return None

        encapsulatingSection = self.sections[idx]
        points = encapsulatingSection[1]
        direction = (points[1][0] - points[0][0], points[1][1] - points[0][1])
        sectionLength = math.dist(points[0], points[1])

        # Calulating the angle
        up = [0, 1]
        normDirection = np.linalg.norm(direction)
        angle = np.arccos(np.dot(up, normDirection))

        # Calculate the position
        distanceOfSectionBefore = self.sections[idx-1][0] if idx > 0 else 0 
        distanceAlongSection = distanceAlong - distanceOfSectionBefore

        percentageTraveled = distanceAlongSection / sectionLength

        position = np.add(points[0], np.multiply(direction, percentageTraveled))

        return (position, angle)



class Edge:
    def __init__(self, edgeNode):
        self.id = edgeNode.attrib['id']
        self.lanes = {}

        lanes = edgeNode.findall('lane')
        for laneNode in lanes:
            lane = Lane(laneNode)
            self.lanes[lane.index] = lane

    def getLane(self, index: int) -> Lane:
        return self.lanes[index]

    def getViaLane(self, fromLaneIndex: int, destEdgeId: str) -> Lane:
        return self.getLane(fromLaneIndex).getViaLane(destEdgeId)

class Network:
    def __init__(self, networkFile):
        self.edges: dict[str, Edge] = {}
        self.lanes: dict[str, Lane] = {}

        edges = networkFile.findall('edge')
        for edgeNode in edges:
            edge = Edge(edgeNode)
            self.edges[edge.id] = edge

            for index, lane in edge.lanes.items():
                self.lanes[lane.id] = lane

        connections = networkFile.findall('connection')
        for connection in connections:
            if 'via' not in connection.attrib:
                continue

            fromEdgeId = connection.attrib['from']
            fromLaneIdx = int(connection.attrib['fromLane'])

            toEdgeId = connection.attrib['to']
            viaLaneId = connection.attrib['via']

            self.getEdge(fromEdgeId).getLane(fromLaneIdx).addConnection(toEdgeId, self.lanes[viaLaneId])
        
    def getEdge(self, id: str) -> Edge:
        return self.edges[id]

    def getLane(self, id: str) -> Lane:
        return self.lanes[id]

        

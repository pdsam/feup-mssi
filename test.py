import easygraphics as eg
from graphics import drawRectangle
from network import Network
import numpy as np

fromEdgeId = '-gneE0'
fromLaneIndex = 0
toEdgeId = 'gneE2'

scaleDrawing = 30

timestep = 250
acceleration = 5
vehicleLength = 5
vehicleWidth = 2

def __testPathSimulation(network: Network, junction):
    eg.init_graph(500,500)

    eg.set_color(eg.Color.BLACK)
    eg.translate(250, 250)
    eg.scale(scaleDrawing, scaleDrawing)

    eg.begin_shape()
    for coords in junction.shape:
        eg.vertex(coords[0], coords[1])
    eg.end_shape()

    eg.set_fill_color(eg.Color.TRANSPARENT)
    for row in junction.cells:
        for cell in row:
            drawRectangle(cell.topLeft, cell.bottomRight)


    eg.pause()

    viaLane = network.getEdge(fromEdgeId).getViaLane(fromLaneIndex, toEdgeId)
    print("via", viaLane)

    eg.set_color(eg.Color.BLUE)
    eg.set_line_style(eg.LineStyle.DOT_LINE)
    eg.set_line_width(5.0)
    eg.begin_shape()
    for coords in viaLane.shape:
        eg.vertex(coords[0], coords[1])
    eg.end_shape()

    eg.pause()

    eg.set_color(eg.Color.DARK_MAGENTA)
    eg.set_line_style(eg.LineStyle.SOLID_LINE)
    eg.set_line_width(4.0)
    speed = 0
    distance = 0

    print("lane length", viaLane.length)
    posAndRotation = viaLane.getPositionAndOrientation(distance)

    while (posAndRotation is not None):
        pos = posAndRotation[0]
        rotation = posAndRotation[1]

        eg.reset_transform()
        eg.translate(250, 250)
        eg.scale(scaleDrawing, scaleDrawing)
        eg.rotate(np.degrees(-rotation), pos[0], pos[1])

        print(distance)
        eg.translate(pos[0], pos[1])
        drawRectangle((-vehicleWidth/2, -vehicleLength/2), ((vehicleWidth/2, vehicleLength/2)))
        speed += acceleration * (timestep / 1000)
        distance += speed * (timestep / 1000)
        posAndRotation = viaLane.getPositionAndOrientation(distance)
        eg.pause()

    eg.pause()

    eg.close_graph()

def testPathSimulation(network: Network, junction):
    return lambda: __testPathSimulation(network, junction)

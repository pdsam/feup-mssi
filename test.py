import easygraphics as eg
from graphics import drawRectangle, drawJunctionWithGrid, drawLaneShape
from network import Network
from junction import Junction
import numpy as np
import collision as cl

fromEdgeId = '-gneE0'
fromLaneIndex = 0
toEdgeId = 'gneE2'

scaleDrawing = 30

timestep = 250
acceleration = 5
vehicleLength = 5
vehicleWidth = 2

def __testPathSimulation(network: Network, junction: Junction):
    eg.init_graph(500,500)

    eg.translate(250, 250)
    eg.scale(scaleDrawing, scaleDrawing)

    drawJunctionWithGrid(junction)

    eg.pause()

    viaLane = network.getEdge(fromEdgeId).getViaLane(fromLaneIndex, toEdgeId)

    drawLaneShape(viaLane.shape)

    eg.pause()

    speed = 0
    distance = 0

    print("lane length", viaLane.length)
    posAndRotation = viaLane.getPositionAndOrientation(distance)

    while (posAndRotation is not None):
        eg.set_background_color(eg.Color.WHITE)
        eg.clear()

        eg.reset_transform()
        eg.translate(250, 250)
        eg.scale(scaleDrawing, scaleDrawing)

        drawJunctionWithGrid(junction)

        pos = posAndRotation[0]
        rotation = posAndRotation[1]

        vehicleBox = cl.Poly.from_box(pos, vehicleWidth, vehicleLength)
        vehicleBox.angle = -rotation
        collidingCells = []
        for cell in junction.cells:
            if cl.test_poly_poly(vehicleBox, cell.boundingBox):
                collidingCells.append(cell)

        # Draw colliding cells
        eg.set_color(eg.Color.BLACK)
        eg.set_fill_color(eg.Color.LIGHT_GREEN)
        eg.set_line_style(eg.LineStyle.SOLID_LINE)
        eg.set_line_width(1.0)
        for cell in collidingCells:
            drawRectangle(cell.topLeft, cell.bottomRight)

        drawLaneShape(viaLane.shape)

        # Draw vehicle
        eg.rotate(np.degrees(-rotation), pos[0], pos[1])

        eg.set_color(eg.Color.DARK_MAGENTA)
        eg.set_fill_color(eg.Color.TRANSPARENT)
        eg.set_line_style(eg.LineStyle.SOLID_LINE)
        eg.set_line_width(4.0)

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

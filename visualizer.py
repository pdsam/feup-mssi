import easygraphics as eg
import numpy as np
from network import Lane, Network
from junction import Junction
from vehicles import Vehicle
from pathSimulator import PathSimulator
from graphics import drawLaneShape, drawRectangle, drawJunctionWithGrid

scaleDrawing = 30

def visualizePathSimulation(network: Network, junction: Junction, \
    viaLane: Lane, vehicle: Vehicle, timestep: float):

    eg.set_background_color(eg.Color.WHITE)
    eg.clear()
    eg.reset_transform()

    eg.translate(250, 250)
    eg.scale(scaleDrawing, -scaleDrawing)

    drawJunctionWithGrid(junction)

    eg.pause()

    drawLaneShape(viaLane.shape)

    eg.pause()

    vehicleWidth = vehicle.width
    vehicleLength = vehicle.length

    speed = 0
    distance = 0

    sim = PathSimulator(junction, vehicle, viaLane, timestep)

    while (not sim.isDone()):
        eg.set_background_color(eg.Color.WHITE)
        eg.clear()

        eg.reset_transform()
        eg.translate(250, 250)
        eg.scale(scaleDrawing, -scaleDrawing)

        drawJunctionWithGrid(junction)

        stepInfo = sim.step()
        if stepInfo is None:
            break

        collidingCells = stepInfo.cells
        pos = stepInfo.pos
        rotation = stepInfo.rotation

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

        eg.pause()

    eg.pause()

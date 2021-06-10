import easygraphics as eg
import traci
from junction import Junction

def drawRectangle(topLeft, bottomRight):
    eg.draw_polygon(\
        topLeft[0], topLeft[1],\
        topLeft[0], bottomRight[1],\
        bottomRight[0], bottomRight[1],\
        bottomRight[0], topLeft[1]\
    )

def drawJunctionWithGrid(junction: Junction):
    eg.set_color(eg.Color.BLACK)
    eg.set_fill_color(eg.Color.WHITE)
    eg.set_line_style(eg.LineStyle.SOLID_LINE)
    eg.set_line_width(1.0)

    eg.begin_shape()
    for coords in junction.shape:
        eg.vertex(coords[0], coords[1])
    eg.end_shape()

    eg.set_fill_color(eg.Color.TRANSPARENT)
    for cell in junction.cells:
        drawRectangle(cell.topLeft, cell.bottomRight)

def drawLaneShape(shape):
    eg.set_color(eg.Color.BLUE)
    eg.set_fill_color(eg.Color.TRANSPARENT)
    eg.set_line_style(eg.LineStyle.DOT_LINE)
    eg.set_line_width(5.0)

    eg.begin_shape()
    for coords in shape:
        eg.vertex(coords[0], coords[1])
    eg.end_shape()


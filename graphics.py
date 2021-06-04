import easygraphics as eg
import traci

def drawRectangle(topLeft, bottomRight):
    eg.draw_polygon(\
        topLeft[0], topLeft[1],\
        topLeft[0], bottomRight[1],\
        bottomRight[0], bottomRight[1],\
        bottomRight[0], topLeft[1]\
    )

scaleGraph = 30
def drawJunctionWithGrid(junction):
    eg.init_graph(500,500)

    eg.set_color(eg.Color.BLACK)
    eg.translate(250, 250)
    eg.scale(scaleGraph, scaleGraph)

    eg.begin_shape()
    for coords in junction.shape:
        eg.vertex(coords[0], coords[1])
    eg.end_shape()

    eg.set_fill_color(eg.Color.TRANSPARENT)
    for row in junction.cells:
        for cell in row:
            drawRectangle(cell.topLeft, cell.bottomRight)

    eg.pause()

    eg.close_graph()

def createRenderFunction(junction):
    return lambda: drawJunctionWithGrid(junction)

from manim import *
from manim.opengl import *


def project_along_line(vertex1, vertex2, point):
    """
    Given 2 vertices defining a line, return
    the projection of point on that line
    """
    vertex2, vertex1, point = map(np.array, (vertex2, vertex1, point))
    unit_vect = normalize(vertex2 - vertex1)
    return vertex1 + unit_vect * np.dot(point - vertex1, unit_vect)

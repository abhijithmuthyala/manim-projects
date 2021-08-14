from typing import Sequence

import numpy as np


def project_along_line(
    vertex1: Sequence[float], vertex2: Sequence[float], point: Sequence[float]
):
    """
    Given 2 vertices defining a line, return
    the projection of point on that line
    """
    vertex1, vertex2, point = map(np.array, (vertex1, vertex2, point))
    unit_vect = np.linalg.norm(vertex2 - vertex1)
    return vertex1 + unit_vect * np.dot(point - vertex1, unit_vect)

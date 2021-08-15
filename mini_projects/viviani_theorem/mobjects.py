import numpy as np
from manim.constants import TAU
from manim.mobject.geometry import Line, Triangle
from manim.mobject.mobject import Mobject
from manim.mobject.types.vectorized_mobject import VMobject
from utils import project_along_line


class Blob(VMobject):
    def __init__(
        self, radius=1, min_scale=0.75, max_scale=1.25, n_samples=10, **kwargs
    ):
        super().__init__(**kwargs)
        np.random.seed()
        points = [
            np.array([np.cos(theta), np.sin(theta), 0])
            * radius
            * np.random.uniform(min_scale, max_scale)
            for theta in np.linspace(0, TAU, n_samples, False)
        ]
        self.set_points_smoothly([*points, points[0]])


class EquilateralTriangle(Triangle):
    def __init__(self, side_length=2, **kwargs):
        super().__init__(**kwargs)
        self.side_length = side_length

    @property
    def side_length(self):
        return self._side_length

    @side_length.setter
    def side_length(self, side_length):
        self.scale(side_length / (np.sqrt(3) * self.circumradius))

    @property
    def circumcenter(self):
        return self.get_center_of_mass()

    @property
    def circumradius(self):
        return np.linalg.norm(self.get_vertices()[0] - self.circumcenter)

    @property
    def inradius(self):
        return self._side_length / (2 * np.sqrt(3))

    def scale(self, scale_factor, about_point=None, **kwargs):
        if about_point is None:
            about_point = self.circumcenter
        Mobject.scale(self, scale_factor, about_point=about_point, **kwargs)
        self._side_length = self.circumradius * np.sqrt(3)
        return self

    def get_projection_onto_edge(self, edge_index, point):
        # There is a formula to get fop, but hey I love vectors, so why not!
        vertices = self.get_vertices()
        vertices = np.append(vertices, [vertices[0]], 0)
        vertex1, vertex2 = vertices[edge_index : edge_index + 2]
        return project_along_line(vertex1, vertex2, point)

    def get_perpendicular_line_to_edge(
        self, edge_index, point, line_class=Line, **kwargs
    ):
        line = line_class(
            point, self.get_projection_onto_edge(edge_index, point), **kwargs
        )
        line.edge_index = edge_index
        return line

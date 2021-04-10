from manim import *
from manim.opengl import *


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
    def circumradius(self):
        return get_norm(self.get_vertices()[0] - self.circumcenter)

    @property
    def circumcenter(self):
        return self.get_center_of_mass()

    @property
    def inradius(self):
        return self.side_length / (2 * np.sqrt(3))

    @property
    def side_length(self):
        return self._side_length

    @side_length.setter
    def side_length(self, side_length):
        self.scale(side_length / (np.sqrt(3) * self.circumradius))

    def scale(self, scale_factor, about_point=None, **kwargs):
        if about_point is None:
            about_point = self.circumcenter
        Mobject.scale(self, scale_factor, about_point=about_point, **kwargs)
        self._side_length = self.circumradius * np.sqrt(3)
        return self

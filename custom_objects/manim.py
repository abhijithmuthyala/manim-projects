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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def inradius(self):
        return get_norm(self.get_vertices()[0] - self.get_center_of_mass())

    @property
    def incenter(self):
        return self.get_center_of_mass()
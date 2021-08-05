from typing import Iterable, Sequence

import numpy as np
from colour import Color
from manim.constants import DOWN, ORIGIN, PI, RIGHT, TAU, UP
from manim.mobject.opengl_geometry import OpenGLArrow, OpenGLCircle
from manim.mobject.opengl_mobject import OpenGLGroup
from manim.mobject.opengl_three_dimensions import OpenGLSphere
from manim.mobject.svg.opengl_text_mobject import OpenGLText
from manim.utils.color import DARK_GREY, GREY
from manim.utils.space_ops import rotation_matrix


# This only exists because OpenGLAnnulus doesn't do the job :(
class OpenGLCompassAnnulus(OpenGLCircle):
    def __init__(
        self,
        outer_radius: float = 2,
        inner_radius: float = 1.75,
        stroke_color: Iterable[Color] = np.tile([DARK_GREY, GREY], 3)[:-1],
        **kwargs,
    ):
        self.initial_inner_radius = inner_radius
        self.initial_outer_radius = outer_radius
        self.initial_radius = (
            self.initial_outer_radius + self.initial_inner_radius
        ) / 2

        super().__init__(
            radius=self.initial_radius,
            # 1 unit of length in manim is 100 units of stroke
            stroke_width=(self.initial_outer_radius - self.initial_inner_radius) * 100,
            **kwargs,
        )
        self.set_stroke(stroke_color)

    def get_radius(self):
        return self.get_width() / 2

    @property
    def inner_radius(self):
        return self.initial_inner_radius * (self.get_radius() / self.initial_radius)

    @property
    def outer_radius(self):
        return self.initial_outer_radius * (self.get_radius() / self.initial_radius)

    def point_on_inner_circle(self, theta: float):
        return self.get_center() + self.inner_radius * (
            np.matmul(rotation_matrix(theta, self.get_unit_normal()), RIGHT)
        )

    def point_on_outer_circle(self, theta: float):
        return self.get_center() + self.outer_radius * (
            np.matmul(rotation_matrix(theta, self.get_unit_normal()), RIGHT)
        )

    def point_at_angle(self, angle: float):
        return super().point_from_proportion(angle % TAU)


class OpenGLMagneticCompass(OpenGLGroup):
    def __init__(
        self,
        outer_radius: float = 2,
        inner_radius: float = 1.75,
        annulus_kwargs: dict = None,
        center_hinge_radius: float = 0.15,
        center_hinge_kwargs: dict = None,
        pointer_kwargs: dict = None,
        pole_labels_width: float = 0.25,
        pole_label_to_annulus_buff: float = 0.15,
        center: Sequence[float] = ORIGIN,
        **kwargs,
    ):
        self.annulus = OpenGLCompassAnnulus(
            outer_radius,
            inner_radius,
            **(annulus_kwargs if annulus_kwargs is not None else {}),
        )
        self.center_hinge = OpenGLSphere(
            radius=center_hinge_radius,
            **(center_hinge_kwargs if center_hinge_kwargs is not None else {}),
        )

        self.pole_label_to_annulus_buff = pole_label_to_annulus_buff
        self.pole_labels_width = pole_labels_width
        self.pole_labels = self.get_pole_labels()
        self.pointer = self.get_pointer(
            **(pointer_kwargs if pointer_kwargs is not None else {})
        )

        super().__init__(
            self.annulus, self.pointer, self.center_hinge, *self.pole_labels, **kwargs
        )
        self.move_to(center)

    def get_pole_labels(self):
        self.north_pole_label, self.south_pole_label = map(OpenGLText, ["N", "S"])
        for pole, angle, direction in zip(
            [self.north_pole_label, self.south_pole_label],
            [PI / 2, -PI / 2],
            [DOWN, UP],
        ):
            pole.set_width(self.pole_labels_width)
            pole.next_to(
                self.annulus.point_on_inner_circle(angle),
                direction,
                self.pole_label_to_annulus_buff,
            )

        self.pole_labels = (self.north_pole_label, self.south_pole_label)
        return self.pole_labels

    def get_pointer(self, **kwargs):
        pointer = OpenGLArrow(DOWN, UP, **kwargs)
        pointer.set_length(
            2
            * (
                self.annulus.inner_radius
                - (
                    self.north_pole_label.get_height()
                    + 2 * self.pole_label_to_annulus_buff
                )
            )
        )
        return pointer

from typing import Callable, Iterable, Sequence

import numpy as np
from colour import Color
from manim.constants import DOWN, IN, LEFT, ORIGIN, OUT, PI, RIGHT, TAU, UP
from manim.mobject.opengl_geometry import OpenGLArrow, OpenGLCircle, OpenGLSquare
from manim.mobject.opengl_mobject import OpenGLGroup
from manim.mobject.opengl_three_dimensions import OpenGLSphere
from manim.mobject.svg.opengl_text_mobject import OpenGLText
from manim.mobject.types.opengl_vectorized_mobject import OpenGLVGroup
from manim.utils.color import BLUE, DARK_GREY, GREY
from manim.utils.space_ops import (
    angle_of_vector,
    normalize,
    rotation_matrix,
    z_to_vector,
)


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
        center = self.get_center()
        return center + self.inner_radius * (
            np.matmul(
                rotation_matrix(theta, self.get_unit_normal()),
                normalize(self.get_points()[0] - center),
            )
        )

    def point_on_outer_circle(self, theta: float):
        center = self.get_center()
        return center + self.outer_radius * (
            np.matmul(
                rotation_matrix(theta, self.get_unit_normal()),
                normalize(self.get_points()[0] - center),
            )
        )

    # Alternate to the above two methods. It's fun to explore different ways!
    def point_at_angle_on_circle(self, angle: float, circle: str = "inner"):
        center = self.get_center()
        radius_vector = super().point_from_proportion(angle % TAU) - center
        if circle == "inner":
            circle_radius = self.inner_radius
        elif circle == "center":
            circle_radius = self.get_radius()
        else:
            circle_radius = self.outer_radius
        return (circle_radius / self.get_radius()) * radius_vector

    def scale(self, scale_factor, **kwargs):
        super().scale(scale_factor, **kwargs)
        self.set_stroke(width=(self.outer_radius - self.inner_radius) * 100)
        return self


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
        include_shield: bool = True,  # shield?
        shield_depth: float = 1,
        shield_kwargs: dict = None,
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

        if include_shield:
            self.shield = OpenGLSphere(
                radius=self.annulus.outer_radius,
                u_range=(PI, TAU),
                v_range=(PI / 2, 3 * PI / 2),
                **(shield_kwargs if shield_kwargs is not None else {}),
            )
            self.shield.set_depth(
                shield_depth, stretch=True, about_point=self.center_hinge.get_center()
            )
            self.add(self.shield)
        self.shift(np.array(center) - self.center_hinge.get_center())

    def get_pole_labels(self):
        self.north_pole_label, self.south_pole_label = map(OpenGLText, ["N", "S"])
        for pole, angle, direction in zip(
            [self.north_pole_label, self.south_pole_label],
            [PI / 2, -PI / 2],
            [DOWN, UP],
        ):
            pole.set_width(self.pole_labels_width, stretch=True)
            pole.set_height(self.pole_labels_width, stretch=True)
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

    def scale(self, scale_factor, **kwargs):
        if not "about_point" in kwargs:
            kwargs["about_point"] = self.center_hinge.get_center()
        super().scale(scale_factor, **kwargs)
        self.annulus.set_stroke(
            width=(self.annulus.outer_radius - self.annulus.inner_radius) * 100
        )
        return self

    def get_pointer_angle(
        self, point: np.ndarray, field_func: Callable[[np.ndarray], np.ndarray]
    ):
        return angle_of_vector(field_func(point))

    def point_at_angle_animation(
        self,
        point: np.ndarray,
        field_func: Callable[[np.ndarray], np.ndarray],
        **kwargs,
    ):
        angle = self.get_pointer_angle(point, field_func)
        kwargs["path_arc"] = angle - self.pointer.get_angle()
        anim = self.pointer.animate(**kwargs).set_angle(
            angle, about_point=self.center_hinge.get_center()
        )
        return anim

    def adjust_z(self):
        self.shift(self.center_hinge.get_center() - self.get_center())
        return self

    def pointer_updater_func(self, field_func: Callable[[np.ndarray], np.ndarray]):
        def func(compass, dt):
            point = compass.center_hinge.get_center()
            compass.pointer.set_angle(
                self.get_pointer_angle(point, field_func),
                about_point=point,
            )
            return compass

        return func


class OpenGLCube(OpenGLVGroup):
    def __init__(
        self,
        side_length=1,
        fill_color=BLUE,
        fill_opacity=0.75,
        stroke_width=0.0,
        **kwargs,
    ):
        self.side_length = side_length
        super().__init__(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs,
        )

    def init_points(self):
        for vect in [RIGHT, UP, LEFT, DOWN, OUT, IN]:
            face = OpenGLSquare(side_length=self.side_length)
            face.flip()
            face.shift(self.side_length * OUT / 2.0)
            face.apply_matrix(z_to_vector(vect))
            self.add(face)


class OpenGLCuboid(OpenGLCube):
    def __init__(self, x_length=3, y_length=3, z_length=1, **kwargs):
        super().__init__(side_length=1, **kwargs)
        for dim, length in enumerate([x_length, y_length, z_length]):
            self.stretch(factor=length, dim=dim)

from typing import Iterable

import numpy as np
from manimlib.animation.animation import Animation
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.growing import GrowFromPoint
from manimlib.animation.transform import ApplyMethod
from manimlib.constants import DL
from manimlib.mobject.coordinate_systems import Axes
from manimlib.mobject.geometry import Arrow, Rectangle
from manimlib.utils.bezier import interpolate


# Yayy, first proper custom animation
class ConstantAreaAnimation(Animation):
    def __init__(
        self,
        rectangle: Rectangle,
        coordinate_system: Axes,
        target_width: float,
        stretch_about_corner: np.ndarray = DL,
        **kwargs,
    ):
        super().__init__(rectangle, **kwargs)
        self.coordinate_system = coordinate_system
        self.target_width = target_width
        self.stretch_about_corner = stretch_about_corner

        self.initial_width = self.mobject.get_width() / self.x_unit
        self.initial_height = self.mobject.get_height() / self.y_unit

    @property
    def original_area(self):
        return self.initial_width * self.initial_height

    @property
    def x_unit(self):
        return self.coordinate_system.x_axis.get_unit_size()

    @property
    def y_unit(self):
        return self.coordinate_system.y_axis.get_unit_size()

    def get_bounds(self, alpha):
        return (0, alpha)

    def interpolate_mobject(self, alpha):
        width = interpolate(self.initial_width, self.target_width, alpha)
        height = self.original_area / width

        width *= self.x_unit
        height *= self.y_unit

        self.mobject.set_width(
            width,
            stretch=True,
            about_point=self.mobject.get_corner(self.stretch_about_corner),
        )
        self.mobject.set_height(
            height,
            stretch=True,
            about_point=self.mobject.get_corner(self.stretch_about_corner),
        )
        return self


class ShrinkVectors(AnimationGroup):
    def __init__(
        self,
        field: Iterable[Arrow],
        scale_factor: float = 0.5,
        run_time: float = 2,
        lag_ratio: float = 0,
        save_state: bool = False,
        **kwargs,
    ):
        anims = []
        for vect in field:
            if save_state:
                vect.save_state()
            anim = ApplyMethod(
                vect.scale, scale_factor, {"about_point": vect.get_start()}, **kwargs
            )
            anims.append(anim)
        super().__init__(*anims, run_time=run_time, lag_ratio=lag_ratio)


class GrowVectors(AnimationGroup):
    def __init__(self, field: Iterable[Arrow], **kwargs):
        anims = [GrowFromPoint(vect, point=vect.get_start()) for vect in field]
        super().__init__(*anims, **kwargs)

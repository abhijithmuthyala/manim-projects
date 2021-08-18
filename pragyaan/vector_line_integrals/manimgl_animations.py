from manimlib.animation.animation import Animation
from manimlib.constants import DL
from manimlib.mobject.coordinate_systems import Axes
from manimlib.mobject.geometry import Rectangle
from manimlib.utils.bezier import interpolate


# Yayy, first proper custom animation
class ConstantAreaAnimation(Animation):
    def __init__(
        self,
        rectangle: Rectangle,
        coordinate_system: Axes,
        target_width: float,
        **kwargs
    ):
        super().__init__(rectangle, **kwargs)
        self.coordinate_system = coordinate_system
        self.initial_width = self.mobject.get_width() / self.x_unit
        self.initial_height = self.mobject.get_height() / self.y_unit
        self.target_width = target_width

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
            width, stretch=True, about_point=self.mobject.get_corner(DL)
        )
        self.mobject.set_height(
            height, stretch=True, about_point=self.mobject.get_corner(DL)
        )
        return self

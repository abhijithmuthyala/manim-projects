import numpy as np
from manim.constants import RIGHT, UP
from manim.mobject.types.vectorized_mobject import VGroup
from manim.utils.bezier import bezier
from manim.utils.color import color_to_rgba, rgba_to_color
from mobjects import LissajousCircle


def color_map(speed, min_value, max_value, *colors):
    alpha = (speed - min_value) / (max_value - min_value)
    if len(colors) == 0:
        raise ValueError("Atleast 1 color needed, passed 0")
    if len(colors) == 1:
        colors = list(colors) * 2
    rgba_s = np.array(list(map(color_to_rgba, colors)))
    interpolated_color = rgba_to_color(bezier(rgba_s)(alpha))
    return interpolated_color


def get_circles(
    radius, n_circles, speeds, buff, arrange_direction=RIGHT, **circle_kwargs
):
    circle_kwargs["radius"] = radius
    circles = VGroup()
    for i in range(n_circles):
        circles.add(LissajousCircle(speed=speeds[i], **circle_kwargs))
    return circles.arrange(arrange_direction, buff)


def get_intersection_point(row_circ, column_circ):
    return row_circ.dot.get_x() * RIGHT + column_circ.dot.get_y() * UP

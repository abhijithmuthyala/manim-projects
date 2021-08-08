from typing import Callable, Iterable, Sequence

import numpy as np
from manimlib.constants import DOWN, PI, RIGHT
from manimlib.mobject.functions import ParametricCurve
from manimlib.mobject.geometry import Line, Polygon, Rectangle
from manimlib.mobject.mobject import Group
from manimlib.mobject.number_line import NumberLine
from manimlib.mobject.three_dimensions import Sphere
from manimlib.mobject.types.surface import SGroup


def c2p(axes: Iterable[NumberLine], vector: Sequence[float]):
    """
    Parameters
    ----------
    axes: An iterable of :class:`NumberLine`s forming a coordinate system.
    vector: A point in 3D space.
    """
    unit_sizes = [axis.get_unit_size() for axis in axes.axes]
    if len(unit_sizes) == 2:
        unit_sizes.append(1)

    transformed_vector = np.matmul(np.diag(unit_sizes), vector)
    transformed_vector += axes.axes[0].n2p(0)
    return transformed_vector


def get_parametric_curve(
    axes: Iterable[NumberLine],
    t_func: Callable[[float], float],
    t_range: Iterable[float],
    **kwargs
):
    return ParametricCurve(lambda t: c2p(axes, t_func(t)), t_range, **kwargs)


def get_flattened_curve(curve: "ParametricCurve", left_edge: Sequence[float]):
    """
    Streches a curve to its arc length and returns a new :class:`Line` with that length.
    """
    flat_curve = Line().match_style(curve)
    flat_curve.set_length(curve.get_arc_length())
    flat_curve.next_to(left_edge, buff=0)
    return flat_curve


def get_flattened_area(
    riemann_sum: Iterable[Polygon],
    dl_edge: np.ndarray,
):
    flat_area = Group()

    for rect in riemann_sum:
        flat_rect = Rectangle().match_style(rect)
        flat_rect.match_width(rect).match_height(rect)
        flat_rect.rotate(PI / 2, axis=RIGHT)
        flat_area.add(flat_rect)

    flat_area.arrange(buff=0, aligned_edge=DOWN).next_to(
        dl_edge, aligned_edge=DOWN, buff=0
    )
    return flat_area


def get_y_line_to_point(x_axis: NumberLine, point: Sequence[float], **kwargs):
    point_on_axis = x_axis.n2p(x_axis.p2n(point))
    return Line(point_on_axis, point, **kwargs)


def get_x_line_to_point(y_axis: NumberLine, point: Sequence[float], **kwargs):
    point_on_axis = y_axis.n2p(y_axis.p2n(point))
    return Line(point_on_axis, point, **kwargs)


def get_sample_input_spheres(
    x_range: Iterable[float],
    y_range: Iterable[float],
    axes: Iterable[NumberLine],
    **sphere_kwargs
):
    spheres = SGroup()
    for x in np.arange(*x_range):
        for y in np.arange(*y_range):
            sphere = Sphere(**sphere_kwargs).move_to(c2p(axes, (x, y, 0)))
            sphere.x = x
            sphere.y = y
            spheres.add(sphere)
    return spheres

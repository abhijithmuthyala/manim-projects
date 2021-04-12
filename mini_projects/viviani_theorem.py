from manim import *
from manim.opengl import *
from manim_fonts import *

from custom_objects.manim import Blob, EquilateralTriangle


def get_right_angle_to_edge(perp_line, width, **kwargs):
    foot_of_perp = perp_line.points[-1]
    theta = angle_of_vector(perp_line.get_vector())
    right_angle = Elbow(width=width, angle=theta - 1.5 * PI, **kwargs)
    right_angle.shift(foot_of_perp)
    return right_angle


def perp_line_updater(perp_line, eq_triangle, dot):
    start = dot.get_center()
    perp_line.put_start_and_end_on(
        start, eq_triangle.get_projection_onto_edge(perp_line.edge_index, start)
    )
    return perp_line


def right_angle_updater(right_angle, perp_line):
    anchors = right_angle.get_anchors()
    right_angle.shift(perp_line.points[-1] - (anchors[-1] + (anchors[0] - anchors[1])))
    return right_angle


def get_length_indicators(perp_lines, width, dl_corner, corner_radius=0.05, **kwargs):
    rects = VGroup()
    for line in perp_lines:
        rect = RoundedRectangle(
            corner_radius, width=width, height=line.get_length(), color=line.get_color()
        )
        rects += rect
    rects.arrange(DOWN, 0).next_to(dl_corner, buff=0, aligned_edge=DOWN)
    rects.set_style(**kwargs)
    rects.dl_corner = dl_corner
    return rects


def length_indicators_updater(rects, perp_lines):
    for rect, line in zip(rects, perp_lines):
        rect.stretch_to_fit_height(line.get_length())
    return rects.arrange(DOWN, 0).next_to(rects.dl_corner, buff=0, aligned_edge=DOWN)

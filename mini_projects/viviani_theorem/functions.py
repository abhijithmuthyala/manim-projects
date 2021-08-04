import numpy as np
from manim.constants import DOWN, PI
from manim.mobject.geometry import Elbow, Polygon, RoundedRectangle
from manim.mobject.svg.tex_mobject import MathTex
from manim.mobject.types.vectorized_mobject import VGroup
from manim.utils.space_ops import angle_of_vector, rotate_vector


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


def get_triangle_to_edge(edge_index, eq_triangle, point, **kwargs):
    vertices = eq_triangle.get_vertices()
    vertices = np.append(vertices, [vertices[0]], 0)
    return Polygon(point, *vertices[edge_index : edge_index + 2], **kwargs)


def get_altitude_text(
    perp_line, text, buff=0.15, scale_factor=1, match_line_style=False, **kwargs
):
    text = MathTex(text)
    if match_line_style:
        text.match_style(perp_line)
    else:
        text.set_style(**kwargs)
    line_vector = perp_line.get_vector()
    text.scale(scale_factor)
    text.rotate(angle_of_vector(line_vector) - 1.5 * PI)
    text.next_to(perp_line.get_center(), rotate_vector(line_vector, PI / 2), buff)
    return text


def get_area_text(height_text, height_text_color, **kwargs):
    tex = MathTex("\\frac{1}{2}b", height_text, **kwargs)
    tex.set_color_by_tex_to_color_map({height_text: height_text_color})
    return tex

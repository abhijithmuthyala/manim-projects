"""
Commit above which this project is made:
https://github.com/ManimCommunity/manim/tree/3156b9f20aa33f559e6f288d38cfd4a4db456389
"""


from manim import *
from manim.opengl import *
from manim_fonts import *

import collections

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


config.background_color = "#111111"


class VivianiTheorem(Scene):
    def construct(self):
        with RegisterFont("Merienda") as fonts:
            title = Text("Viviani Theorem", font=fonts[0], color=GOLD_E).scale(2)
            title.add(Underline(title, 0.25))

            theorem = Paragraph(
                "For an equilateral triangle, the sum of the distances from any",
                "interior point to the sides, is equal to its altitude.",
                line_spacing=0.8,
                font=fonts[0],
            ).set_opacity(0.35)

        self.wait(0.25)
        self.play(FadeInFromLarge(title, 1.15, run_time=4, lag_ratio=0.1))
        self.wait(0.5)
        self.play(title.animate.scale(0.5).to_corner(UL, buff=0.25))
        self.wait(0.25)

        theorem.set(width=config.frame_width - 1)
        theorem.next_to(title, DOWN, buff=0.5, aligned_edge=LEFT)
        triangle = EquilateralTriangle(4.5, color=GOLD_E, fill_opacity=0.1)
        triangle.next_to(theorem, DOWN, buff=0.5)

        self.play(FadeIn(theorem, lag_ratio=0.25, run_time=4, rate_func=linear))
        self.wait()
        self.play(
            theorem[0][:25].animate(lag_ratio=1).set_opacity(1),
            GrowFromCenter(triangle),
            run_time=3,
        )
        self.wait(0.5)

        dot = Dot(point=triangle.circumcenter)
        perp_line_colors = [RED_C, PINK, BLUE_E]  # ccw starting from right edge
        perp_lines = []
        right_angles = []
        for i, color in zip([2, 0, 1], perp_line_colors):
            line = triangle.get_perpendicular_line_to_edge(
                i, dot.get_center(), color=color
            )
            line.z_index = -1
            right_angle = get_right_angle_to_edge(line, 0.125).match_style(line)
            perp_lines.append(line)
            right_angles.append(right_angle)

        self.play(
            FadeInFromLarge(dot, 3),
            AnimationGroup(
                theorem[0][25:].animate(lag_ratio=1).set_opacity(1),
                theorem[1][:13].animate(lag_ratio=1).set_opacity(1),
                lag_ratio=1,
            ),
            run_time=3,
        )
        self.play(*map(Create, perp_lines), run_time=0.75)
        self.play(*map(Create, right_angles), run_time=0.75)

        length_indicators = get_length_indicators(
            perp_lines,
            0.5,
            triangle.get_vertices()[1] + 2 * LEFT,
            fill_opacity=0.25,
            stroke_width=2,
        ).save_state()
        length_indicators.stretch(0.0001, 1, about_edge=DOWN)

        self.play(Restore(length_indicators, run_time=2))
        self.wait(0.5)

        altitude_ref_lines = []
        for i, corner in zip([0, 1], [UR, DR]):
            start = triangle.get_vertices()[i]
            end = length_indicators.get_corner(corner)
            altitude_ref_lines.append(DashedLine(start, end))

        self.play(
            *map(Create, altitude_ref_lines),
            theorem[1][13:].animate(lag_ratio=1).set_opacity(1),
            run_time=3,
        )  # there's something weird about indexing Paragraph or I don't understand it well
        self.wait()

        updater_anims = [
            *map(
                lambda l: UpdateFromFunc(
                    l, lambda l: perp_line_updater(l, triangle, dot)
                ),
                perp_lines,
            ),
            UpdateFromFunc(
                length_indicators, lambda li: length_indicators_updater(li, perp_lines)
            ),
            UpdateFromFunc(
                right_angles[0],
                lambda r: right_angle_updater(right_angles[0], perp_lines[0]),
            ),
            UpdateFromFunc(
                right_angles[1],
                lambda r: right_angle_updater(right_angles[1], perp_lines[1]),
            ),
            UpdateFromFunc(
                right_angles[2],
                lambda r: right_angle_updater(right_angles[2], perp_lines[2]),
            ),
        ]

        def move_dot_along_random_path(blob_center):
            for _ in range(2):
                blob = Blob(triangle.inradius - 0.125, max_scale=0.95, n_samples=15)
                blob.shift(blob_center)
                self.play(
                    dot.animate.move_to(blob.points[0]),
                    *updater_anims,
                    rate_func=linear,
                    run_time=2,
                )
                self.play(
                    MoveAlongPath(dot, blob),
                    *updater_anims,
                    rate_func=linear,
                    run_time=8,
                )

        move_dot_along_random_path(triangle.circumcenter)
        self.play(
            dot.animate.move_to(triangle.get_center()),
            *updater_anims,
            rate_func=linear,
            run_time=2,
        )
        self.wait()

        triangle_copy = triangle.copy()
        edge_triangles = VGroup()
        for i, color in zip([2, 0, 1], perp_line_colors):
            edge_tri = get_triangle_to_edge(
                i, triangle, dot.get_center(), color=color, fill_opacity=0.25
            )
            edge_triangles += edge_tri

        self.add(triangle_copy)
        self.play(
            FadeOutAndShift(Group(*length_indicators, *altitude_ref_lines), LEFT),
            run_time=0.5,
        )
        self.play(
            triangle_copy.animate.shift(3 * LEFT),
            Group(triangle, dot, *perp_lines, *right_angles).animate.shift(3 * RIGHT),
        )

        edge_triangles.shift(3 * RIGHT)
        edge_triangles_group = VGroup(*edge_triangles, *perp_lines, *right_angles, dot)

        self.wait(0.5)
        self.play(
            LaggedStart(
                GrowFromPoint(
                    edge_triangles, dot.get_center(), lag_ratio=1, run_time=2
                ),
                triangle.animate.set_opacity(0),
                lag_ratio=0.5,
            )
        )
        self.wait(0.5)

        theorem_group = VGroup(title, theorem)
        theorem_group.save_state()
        triangles_group = VGroup(triangle_copy, edge_triangles_group)
        triangles_group.save_state()

        self.play(
            LaggedStart(
                FadeOutAndShift(theorem_group, UP),
                triangles_group.animate.to_edge(UP),
                lag_ratio=1,
            )
        )
        triangle.to_edge(UP)
        self.wait(0.5)

        base_braces = [
            BraceText(mob, "b", Text, label_scale=0.6)
            for mob in [triangle_copy, edge_triangles_group]
        ]
        h_line = triangle_copy.get_perpendicular_line_to_edge(
            1, triangle_copy.get_vertices()[0], color=triangle_copy.get_color()
        )
        h_ra = get_right_angle_to_edge(h_line, 0.125).match_style(h_line)
        h_text = get_altitude_text(
            h_line, "h", 0.03, 0.65, fill_color=triangle_copy.get_color()
        )
        h0_text, h1_text, h2_text = [
            get_altitude_text(pl, f"h_{pl.edge_index}", 0.03, 0.65, fill_color=col)
            for pl, col in zip(perp_lines, perp_line_colors)
        ]
        h_texts = VGroup(h_text, h0_text, h1_text, h2_text)

        self.play(LaggedStartMap(Create, Group(h_line, h_ra), lag_ratio=1))
        self.wait(0.5)
        self.play(LaggedStartMap(FadeInFromLarge, h_texts, lag_ratio=1))
        self.play(
            LaggedStartMap(
                GrowFromCenter, Group(*base_braces), lag_ratio=0, run_time=0.75
            )
        )
        self.wait(0.5)

        shuffled_edge_triangles = collections.deque([*edge_triangles])
        shuffled_edge_triangles.rotate(2)
        shuffled_edge_triangles = list(shuffled_edge_triangles)

        area_left = get_area_text("h", triangle_copy.get_color())
        area_left.next_to(base_braces[0], DOWN)
        area_right = VGroup()

        for index, tri in zip([0, 1, 2], shuffled_edge_triangles):
            area_right += get_area_text(f"h_{index}", tri.get_color())
            area_right += MathTex("+")
        area_right = area_right[:-1]
        area_right.arrange(buff=0.1).next_to(base_braces[1], DOWN)

        equals = MathTex("=")
        area_eqn = VGroup(area_left, equals, area_right).arrange(buff=2)
        area_eqn.next_to(base_braces[0].label, DOWN, 0.5, LEFT)

        self.play(*map(FadeInFromLarge, area_eqn[:2]))
        self.wait(0.5)

        edge_triangles_group += h_texts[1:]
        edge_triangles_group.save_state()
        self.play(
            Rotating(
                edge_triangles_group,
                radians=2 * PI / 3,
                about_point=triangle.circumcenter,
                run_time=0.75,
            )
        )
        self.wait(0.5)

        for i in range(3):
            self.play(FadeInFromLarge(area_right[2 * i]))
            self.wait(0.5)
            if i != 2:
                self.play(
                    Rotating(
                        edge_triangles_group,
                        radians=-2 * PI / 3,
                        about_point=triangle.circumcenter,
                    ),
                    FadeInFromLarge(area_right[2 * i + 1]),
                    run_time=0.75,
                )
            self.wait(0.5)
        self.play(Restore(edge_triangles_group, run_time=0.75))
        self.wait(0.5)
        self.play(area_eqn.animate.arrange(buff=0.25, center=False).move_to(2.5 * DOWN))
        self.wait(0.5)

        half_b = [area_left, *area_right[::2]]
        surr_rects = [
            SurroundingRectangle(hb[0], buff=0.01, stroke_width=1, fill_opacity=0.1)
            for hb in half_b
        ]

        self.play(FadeInFrom(Group(*surr_rects), UP, lag_ratio=0.15))
        self.wait(0.5)

        for rect, hb in zip(surr_rects, half_b):
            rect.add(hb[0])
            hb.remove(hb[0])

        self.play(
            AnimationGroup(
                FadeOutAndShift(Group(*surr_rects), DOWN, lag_ratio=0.1),
                FadeOutAndShift(Group(*base_braces), 0.2 * DOWN),
                lag_ratio=0.1,
                run_time=2,
            )
        )
        self.wait(0.25)

        area_eqn_copy = area_eqn.copy()
        area_eqn_copy[2].arrange(buff=0.2, center=False)
        area_eqn_copy.arrange(buff=0.25, center=False)
        area_eqn_copy.move_to(2.5 * DOWN)

        self.play(TransformMatchingShapes(area_eqn, area_eqn_copy, run_time=0.75))
        area_eqn.__dict__ = (
            area_eqn_copy.__dict__
        )  # had to do bcz of a bug in Transform
        self.wait()

        surr_rect_area_eqn = SurroundingRectangle(
            area_eqn, triangle.get_color(), stroke_width=1, fill_opacity=0.1
        )
        self.play(GrowFromEdge(surr_rect_area_eqn, LEFT))
        self.wait(0.5)

        self.play(
            Group(area_eqn, surr_rect_area_eqn).animate.scale(0.8).shift(3 * UP),
            AnimationGroup(
                Group(*triangles_group, h_line, h_ra, h_text, *h_texts).animate.to_edge(
                    DOWN
                ),
                FadeInFrom(theorem_group, 0.25 * UP),
                lag_ratio=0.8,
            ),
        )
        self.wait(2)

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


def get_triangle_to_edge(edge_index, eq_triangle, point, **kwargs):
    vertices = eq_triangle.get_vertices()
    vertices = np.append(vertices, [vertices[0]], 0)
    return Polygon(point, *vertices[edge_index : edge_index + 2], **kwargs)


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
            run_time=3
        )
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

        for _ in range(2):
            blob = Blob(triangle.inradius - 0.125, max_scale=0.95, n_samples=15)
            blob.shift(triangle.circumcenter)
            self.play(
                dot.animate.move_to(blob.points[0]),
                *updater_anims,
                rate_func=linear,
                run_time=2
            )
            self.play(
                MoveAlongPath(dot, blob), *updater_anims, rate_func=linear, run_time=8
            )

        self.play(
            dot.animate.move_to(triangle.get_center()),
            *updater_anims,
            rate_func=linear,
            run_time=2
        )

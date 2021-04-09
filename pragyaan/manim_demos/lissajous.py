from manim import *
import numpy as np

COLORS = (GOLD, MAROON, PURPLE, GREEN)
MIN_SPEED = 1
MAX_SPEED = 3


def color_map(speed, min_value, max_value, *colors):
    alpha = (speed - min_value) / (max_value - min_value)
    if len(colors) == 0:
        raise ValueError("Atleast 1 color needed, passed 0")
    if len(colors) == 1:
        colors = list(colors) * 2
    rgba_s = np.array(list(map(color_to_rgba, colors)))
    interpolated_color = rgba_to_color(bezier(rgba_s)(alpha))
    return interpolated_color


def speed_to_color_map(speed):
    return color_map(speed, MIN_SPEED, MAX_SPEED, *COLORS)


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


class LissajousCircle(Circle):
    def __init__(
        self,
        radius=1,
        speed=0.5,
        point_type=SmallDot,
        point_kwargs={},
        include_radius_line=True,
        radius_line_kwargs={},
        start_angle=0,
        **circle_kwargs
    ):
        circle_kwargs["radius"] = radius
        super().__init__(**circle_kwargs)

        self.speed = speed
        self.theta = start_angle
        self.include_radius_line = include_radius_line
        point = self.point_from_proportion(self.theta / TAU)
        self.dot = point_type(point=point, **point_kwargs)
        if include_radius_line:
            radius_line = Line(self.get_center(), point, **radius_line_kwargs)
            self.radius_line = radius_line
            self.add(radius_line)
        self.add(self.dot)

    def update_point(self, dt, speed=None):
        speed = speed or self.speed
        self.theta += speed * dt
        if self.theta > TAU:
            self.theta -= TAU
            self.cycle_incremented = (
                True  # not a good name for what this is meant for, change.
            )
        else:
            self.cycle_incremented = False
        self.dot.move_to(self.point_from_proportion(self.theta / TAU))
        if self.include_radius_line:
            self.radius_line.set_angle(self.theta)


class LissajousTableScene(Scene):
    def __init__(
        self,
        radius=0.75,
        circle_kwargs={},
        row_buff=0.25,
        column_buff=0.25,
        left_edge_buff=0.5,
        top_edge_buff=0.5,
        include_radius_line=True,
        row_circle_speeds_range=(1, 3),
        column_circle_speeds_range=(1, 3),
        **kwargs
    ):
        self.radius = radius
        self.circle_kwargs = circle_kwargs
        self.row_buff = row_buff
        self.column_buff = column_buff
        self.left_edge_buff = left_edge_buff
        self.top_edge_buff = top_edge_buff
        self.include_radius_line = include_radius_line
        self.n_rows, self.n_cols = self.get_grid_size()
        self.row_circle_speeds = np.linspace(*row_circle_speeds_range, self.n_rows - 1)
        self.column_circle_speeds = np.linspace(
            *column_circle_speeds_range, self.n_cols - 1
        )
        self.row_speed_range = row_circle_speeds_range
        self.column_speed_range = column_circle_speeds_range
        super().__init__(**kwargs)

    def setup(self):
        self.row_circles = get_circles(
            self.radius, self.n_rows - 1, self.row_circle_speeds, self.row_buff
        )
        self.column_circles = get_circles(
            self.radius,
            self.n_cols - 1,
            self.column_circle_speeds,
            self.column_buff,
            DOWN,
        )
        self.arrange_row_circles_to_match_buff()
        self.arrange_column_circles_to_match_buff()

    def get_grid_size(self):
        row_length = config["frame_width"] - 2 * self.left_edge_buff
        column_length = config["frame_height"] - 2 * self.top_edge_buff
        n_rows = self.get_max_circles(row_length, self.row_buff)
        n_cols = self.get_max_circles(column_length, self.column_buff)
        return (n_rows, n_cols)

    def get_max_circles(self, length, buff, radius=None):
        radius = radius or self.radius
        return int((length + buff) / (2 * radius + buff))

    def add_circle_updaters(self, circles=None):
        if circles is None:
            circles = [*self.row_circles, *self.column_circles]
        for c in circles:
            c.add_updater(lambda c, dt: c.update_point(dt))

    def arrange_row_circles_to_match_buff(self, row_circles=None):
        circles = row_circles or self.row_circles
        y = config["frame_height"] / 2 - (self.top_edge_buff + self.radius)
        x = (
            2 * self.radius
            + self.row_buff
            + self.left_edge_buff
            - config["frame_width"] / 2
        )
        return circles.next_to(x * RIGHT + y * UP, buff=0)

    def arrange_column_circles_to_match_buff(self, column_circles=None):
        circles = column_circles or self.column_circles
        x = self.left_edge_buff + self.radius - config["frame_width"] / 2
        y = config["frame_height"] / 2 - (
            self.top_edge_buff + 2 * self.radius + self.column_buff
        )
        aligned_edge = self.column_circles.get_critical_point(UP)
        return circles.next_to(x * RIGHT + y * UP, DOWN, 0, aligned_edge)

    def get_horizontal_lines(self, column_circles=None, line_style=Line, **style):
        circles = column_circles or self.column_circles
        lines = VGroup()
        for circ in circles:
            start = circ.dot.get_center()
            end = np.array(
                [config["frame_width"] / 2 - self.left_edge_buff, circ.dot.get_y(), 0]
            )
            lines.add(line_style(start, end))
        return lines.set_style(**style)

    def get_vertical_lines(self, row_circles=None, line_style=Line, **style):
        circles = row_circles or self.row_circles
        lines = VGroup()
        for circ in circles:
            start = circ.dot.get_center()
            end = np.array(
                [circ.dot.get_x(), self.top_edge_buff - config["frame_height"] / 2, 0]
            )
            lines.add(line_style(start, end))
        return lines.set_style(**style)

    def add_lines_updaters(self, h_lines, v_lines):
        h_lines.add_updater(
            lambda h: h.become(self.get_horizontal_lines(**h_lines.get_style()))
        )
        v_lines.add_updater(
            lambda v: v.become(self.get_vertical_lines(**v_lines.get_style()))
        )

    def initiate_paths(self, **style):
        paths = VGroup()
        for col_circ in self.column_circles:
            for row_circ in self.row_circles:
                point = get_intersection_point(row_circ, col_circ)
                path = VMobject(**style).set_points_as_corners(
                    [point, point * 1.0000000001]
                )
                path.set_color(
                    interpolate_color(row_circ.get_color(), col_circ.get_color(), 0.5)
                )
                dot = SmallDot(point=point)
                path.add(dot)
                path.dot = dot
                path.row_circle = row_circ
                path.column_circle = col_circ
                paths.add(path)
        self.paths = paths

    def add_path_updaters(self):
        def path_update_func(path, dt):
            rc, cc = path.row_circle, path.column_circle
            if not (rc.cycle_incremented and cc.cycle_incremented):
                # path.set_points_as_corners(path.points[:2])
                # else:
                point = get_intersection_point(rc, cc)
                path.add_points_as_corners([point])
                path.dot.move_to(point)

        for path in self.paths:
            path.add_updater(path_update_func)

    def is_path_traced_once(self):
        # for a given combination of a row circ and a column circ,
        # if both the circles enter a new cycle in the same frame,
        # atleast 1 cycle of the corresponding lissajous curve
        # must have completed.
        for cc in self.column_circles:
            for rc in self.row_circles:
                if not (rc.cycle_incremented and cc.cycle_incremented):
                    return False
        return True

    def set_circle_colors_by_speed(self):
        for c in [*self.row_circles, *self.column_circles]:
            c.set_color(speed_to_color_map(c.speed))

    def suspend_circles_updating(self):
        [c.suspend_updating() for c in [*self.row_circles, *self.column_circles]]

    def resume_circles_updating(self):
        [c.resume_updating() for c in [*self.row_circles, *self.column_circles]]


class DrawLissajousFigures(LissajousTableScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        self.camera.background_color = "#0C2D48"

        lines_style = {"stroke_width": 0.75}
        vert_lines = self.get_vertical_lines(**lines_style)
        hor_lines = self.get_horizontal_lines(**lines_style)

        self.set_circle_colors_by_speed()
        [c.dot.set_color(WHITE) for c in [*self.row_circles, *self.column_circles]]
        self.initiate_paths(stroke_width=2)

        # self.add(self.row_circles, self.column_circles, hor_lines, vert_lines, self.paths)
        self.wait(2)
        self.play(
            AnimationGroup(
                LaggedStart(
                    *[FadeInFrom(c, 0.25 * LEFT) for c in self.row_circles],
                    lag_ratio=0.25
                ),
                LaggedStart(
                    *[FadeInFrom(c, 0.25 * UP) for c in self.column_circles],
                    lag_ratio=0.25
                ),
                lag_ratio=1,
                run_time=4,
            )
        )
        self.wait(2)
        self.play(
            AnimationGroup(
                ShowCreation(VGroup(hor_lines, vert_lines), lag_ratio=1),
                ShowCreation(self.paths, lag_ratio=0.25),
                lag_ratio=1,
                run_time=4,
            )
        )
        self.wait(2)

        # order here matters.
        self.add_circle_updaters()
        self.add_lines_updaters(hor_lines, vert_lines)
        self.add_path_updaters()

        self.wait_until(lambda: self.is_path_traced_once())
        self.wait(1 / self.camera.frame_rate)
        self.suspend_circles_updating()
        self.wait(2)

        # for _ in range(2):
        #     self.wait_until(lambda: self.is_path_traced_once(), max_time=25)
        #     [c.suspend_updating() for c in [*self.row_circles, *self.column_circles]]
        #     self.wait()
        #     [c.resume_updating() for c in [*self.row_circles, *self.column_circles]]


class RadiusOne(DrawLissajousFigures):
    def __init__(self):
        super().__init__(
            radius=1,
            row_buff=0.5,
            column_buff=0.4,
            top_edge_buff=0.5,
            left_edge_buff=0.5,
        )


class RadiusHalf(DrawLissajousFigures):
    def __init__(self):
        super().__init__(
            radius=0.5,
            row_buff=0.25,
            column_buff=0.3,
            top_edge_buff=0.5,
            left_edge_buff=0.5,
        )


class RadiusThreeFourths(DrawLissajousFigures):
    def __init__(self):
        super().__init__(
            radius=0.75,
            row_buff=0.25,
            column_buff=0.25,
            top_edge_buff=0.5,
            left_edge_buff=0.5,
        )

from functions import *
from manimlib import *
# lost these, will upload if found
from mobjects import Particle
from numpy import arange, array, cos, sin

x_col, y_col = MAROON_D, GREEN_D
curve_col, t_col = YELLOW_D, BLUE_D
center_buff = 0.1

t_axis_config = dict(
    stroke_color=t_col,
    unit_size=1,
    include_numbers=True,
    label_direction=UP,
    include_tip=True,
    include_label=True,
    label="time(s)",
    exclude_zero_from_default_numbers=False,
    number_scale_val=0.6,
    label_buff=0.02,
)

default_plane_config = dict(
    # background_line_style={"stroke_opacity": 0.5},
    axis_config={
        "axis_label_direction": RIGHT,
        "include_tip": True,
        "include_label": True,
        "stroke_width": 5,
        "include_ticks": True,
        "number_scale_val": 0.6,
    },
    x_axis_config={
        "stroke_color": x_col,
        "unit_size": 1,
        "x_min": 0,
        "x_max": 5,
        "label_direction": DOWN,
        "label": "x(t)",
        "label_buff": 0.05,
    },
    y_axis_config={
        "stroke_color": y_col,
        "unit_size": 1,
        "x_min": 0,
        "x_max": 4,
        "label_direction": UP,
        "label": "y(t)",
        "label_buff": 0.05,
    },
)

background_rect_style = dict(color="#111111", opacity=0.75, buff=0.1)


def cycloid(t, rad=1):
    return rad * array([t - sin(t), 1 - cos(t)])


class ArcLengthScene(Scene):
    CONFIG = {
        "t_axis_config": t_axis_config,
        "plane_config": default_plane_config,
        "particle_a_config": {"text": "$A$", "color": PURPLE_E},
        "particle_b_config": {"text": "$B$", "color": TEAL_E},
        "t_func": cycloid,
        "t_min": 0,
        "t_max": 4,
        "include_background_rectangle": False,
        "background_rect_style": background_rect_style,
        "x_color": x_col,
        "y_color": y_col,
        "t_color": t_col,
        "curve_color": curve_col,
        "dt_max": 1,
        "dt_min": 0.05,
        "secant_gradient": [BLUE_D, GREEN_D],
    }

    def setup(self):
        self.t_tracker = ValueTracker(self.t_min)
        self.t_min_tracker = ValueTracker(self.t_min)
        self.t_max_tracker = ValueTracker(self.t_max)
        self.dt_tracker = ValueTracker(self.dt_max)

        axis_config = dict(
            self.t_axis_config, **{"x_min": self.t_min, "x_max": self.t_max + 1}
        )
        self.plane = NumberPlane(**self.plane_config)
        self.t_axis = NumberLine(**axis_config)
        self.t_min_pivot = self.t_axis.get_pivot(self.t_min).add_updater(
            lambda p: p.next_to(
                self.t_axis.n2p(self.t_min_tracker.get_value()), DOWN, buff=0
            )
        )
        self.t_max_pivot = self.t_axis.get_pivot(self.t_max).add_updater(
            lambda p: p.next_to(
                self.t_axis.n2p(self.t_max_tracker.get_value()), DOWN, buff=0
            )
        )
        self.t_dot = Dot(self.t_axis.n2p(self.t_min)).add_updater(
            lambda d: d.move_to(self.t_axis.n2p(self.t_tracker.get_value()))
        )
        self.t_axis.add(self.t_min_pivot, self.t_max_pivot).match_width(self.plane)
        VGroup(self.t_axis, self.plane).arrange(DOWN).to_edge()

        mobs_to_rotate = [self.plane.y_axis.label]
        if hasattr(self.plane.y_axis, "numbers"):
            mobs_to_rotate[1:] = self.plane.y_axis.numbers
        [mob.rotate(PI / 2, IN) for mob in mobs_to_rotate]

        if self.include_background_rectangle:
            for mob in (self.t_axis, self.plane):
                mob.add_background_rectangle(**self.background_rect_style)

        self.a = Particle(**self.particle_a_config)
        self.b = Particle(**self.particle_b_config)

        self.curve = self.get_curve()
        self.curve.add_updater(lambda c: c.become(self.get_curve()))
        self.add(self.curve)

        velocity_axes_config = merge_dicts_recursively(
            self.plane_config,
            dict(
                axis_config={"include_numbers": True},
                x_axis_config={"x_max": 6, "stroke_color": GREY, "label": "t"},
                y_axis_config={
                    "x_max": 3,
                    "stroke_color": GREY,
                    "unit_size": 1.25,
                    "label": "v(t)",
                },
            ),
        )
        self.velocity_axes = Axes(**velocity_axes_config)
        [
            mob.rotate(-PI / 2)
            for mob in [
                *self.velocity_axes.y_axis.numbers,
                self.velocity_axes.y_axis.label,
            ]
        ]
        self.velocity_axes.x_axis.label.set_color(self.t_color)
        self.velocity_axes.y_axis.label.set_color(self.secant_gradient)
        self.velocity_axes.to_corner(DR)

        self.velocity_step_graph = self.get_step_graph(
            self.dt_max, self.t_min, self.t_max
        )
        self.riemann_rects = self.get_riemann_rects(self.dt_max, self.t_min, self.t_max)
        self.run_time = self.t_max - self.t_min
        # self.frame = self.camera_frame

    def get_step_graph(
        self, dt, t_min, t_max, axes=None, t_func=None, gradient=None, **style
    ):
        axes = axes or self.velocity_axes
        t_func = t_func or self.t_func
        gradient = gradient or self.secant_gradient
        lines = VGroup()

        for t in arange(t_min, t_max, dt):
            height = get_velocity(t_func, t, dt)
            lines.add(Line(*[axes.c2p(x, height) for x in [t, t + dt]]))
        lines.set_style(**style).set_color_by_gradient(*gradient)
        return lines

    def get_riemann_rects(
        self, dt, t_min, t_max, axes=None, t_func=None, gradient=None, **style
    ):
        axes = axes or self.velocity_axes
        t_func = t_func or self.t_func
        gradient = gradient or self.secant_gradient
        width = axes.x_axis.unit_size * dt
        style = dict(
            {"fill_opacity": 0.6, "stroke_color": BLACK, "stroke_width": 0.5}, **style
        )
        rects = VGroup()

        for t in arange(t_min, t_max, dt):
            height = get_velocity(t_func, t, dt) * axes.y_axis.unit_size
            rect = Rectangle(width=width, height=height)
            rect.next_to(axes.c2p(t, 0), UP, aligned_edge=LEFT, buff=0)
            rects.add(rect)
        rects.set_color_by_gradient(*gradient).set_style(**style)
        return rects

    def get_curve(self, t_func=None):
        t_func = self.t_func if t_func is None else t_func
        return self.plane.get_parametric_curve(
            t_func,
            t_min=self.t_min_tracker.get_value(),
            t_max=self.t_max_tracker.get_value(),
            color=self.curve_color,
        )

    def get_coordinates(self, coords, colors=None, scale_fact=1):
        if colors is None:
            colors = (self.x_color, self.y_color)
        coords = Matrix(coords).scale(scale_fact)
        [num.set_color(col) for num, col in zip(coords.elements, colors)]
        return coords

    def get_secant_lines_and_dots(self, curve, t_min, t_max, dt, gradient=None):
        gradient = gradient or self.secant_gradient
        points = list(map(curve.function, arange(t_min, t_max + dt, dt)))
        rad = 0.07 + 0.04 * (dt - self.dt_max) / (self.dt_max - self.dt_min)

        dots = VGroup(*[Dot(pos, radius=rad) for pos in points])
        dots.set_color_by_gradient(*gradient)

        lines = VGroup()
        for i in range(len(points) - 1):
            ends = points[i : i + 2]
            lines.add(Line(*ends))
        lines.set_color_by_gradient(*gradient)

        return VGroup(lines, dots)

    def collapse_secant_lines(
        self,
        sct_lines,
        dots=None,
        align_to=None,
        target_style=None,
        animate=True,
        added_anims=[],
        **kwargs,
    ):
        target_style = {} if target_style is None else target_style
        target_points = self.get_points_after_collapse(sct_lines, align_to)
        target_lines = VGroup()
        sct_lines_copy = sct_lines.copy()

        for i in range(len(target_points) - 1):
            line = sct_lines_copy[i]
            line.put_start_and_end_on(*target_points[i : i + 2])
            target_lines.add(line)
        target_lines.set_style(**target_style)

        anims = [ApplyMethod(sct_lines.become, target_lines), *added_anims]
        if dots is not None:
            anims[2:] = [
                ApplyMethod(dot.move_to, pos) for dot, pos in zip(dots, target_points)
            ]

        if animate:
            self.play(AnimationGroup(*anims), **kwargs)
        else:
            [dot.move_to(pos) for dot, pos in zip(dots, target_points)]
            return VGroup(target_lines, dots)

    def get_points_after_collapse(self, sct_lines, align_to=None):
        target_lines = VGroup()
        align_to = sct_lines[0].get_start() if align_to is None else align_to

        for line in sct_lines.copy():
            line.rotate(-line.get_angle(), about_point=line.get_start())
            target_lines.add(line)

        target_lines.arrange(buff=0).next_to(align_to, buff=0)
        target_points = [line.get_start() for line in target_lines]
        target_points.append(target_lines[-1].get_end())

        return target_points

    def transform_curve_to_line(
        self,
        curve,
        scale_fact=1,
        align_to=None,
        use_copy=True,
        added_anims=[],
        **kwargs,
    ):
        arc_length = get_arc_length(curve.t_func, *curve.t_range[:-1])
        line = Line().set_length(arc_length).scale(scale_fact)
        line.match_style(curve)
        align_to = curve.points[0] if align_to is None else align_to
        line.next_to(align_to, buff=0)
        anims = added_anims
        anims.append(
            TransformFromCopy(curve, line)
            if use_copy
            else TransformFromCopy(curve, line)
        )
        self.play(*anims, **kwargs)

    def trace_curve(self, curve, tracing_mob, added_anims=[], **kwargs):
        kwargs = dict({"run_time": self.run_time, "rate_func": linear}, **kwargs)

        def update_mob(mob):
            mob.move_to(curve.get_end())

        self.play(
            ShowCreation(curve),
            UpdateFromFunc(tracing_mob, update_mob),
            *added_anims,
            **kwargs,
        )

    def show_map_from_ip_to_op(
        self,
        x_range,
        axis=None,
        plane=None,
        t_func=None,
        junction=None,
        gradient=None,
        **kwargs,
    ):
        axis = axis or self.t_axis
        plane = plane or self.plane
        t_func = t_func or self.t_func

        dots = self.get_dots_on_axis(
            axis,
            *x_range,
            gradient,
            stroke_color=WHITE,
            stroke_width=1,
            stroke_opacity=1,
        )
        final_targets = [plane.c2p(*t_func(x)) for x in arange(*x_range)]
        kwargs = dict({"lag_ratio": 0, "run_time": 4}, **kwargs)

        self.play(
            LaggedStartMap(GrowFromCenter, VGroup(*dots), lag_ratio=1), run_time=2
        )
        self.wait()
        if junction is None:
            self.move_to_target(dots, final_targets, **kwargs)
        else:
            kwargs["run_time"] *= 0.5
            self.move_to_target(dots, [list(junction)] * len(dots), **kwargs)
            self.move_to_target(dots, final_targets, **kwargs)
        self.wait(2)
        self.play(LaggedStartMap(FadeOut, dots, lag_ratio=0.5))

    def move_to_target(self, mobs, targets, **kwargs):
        self.play(
            LaggedStart(
                *[ApplyMethod(m.move_to, t) for m, t in zip(mobs, targets)], **kwargs
            )
        )

    def move_along_secant_lines(self, mob, secant_lines, dt):
        for i, line in enumerate(secant_lines):
            self.play(
                MoveAlongPath(mob, line),
                self.t_tracker.set_value,
                (i + 1) * dt,
                run_time=dt,
                rate_func=linear,
            )

    def get_dots_on_axis(self, axis, t_min, t_max, dt, gradient=None, **style):
        rad = 0.08 + 0.03 * (dt - self.dt_max) / (self.dt_max - self.dt_min)
        x_vals = arange(t_min, t_max + dt, dt)
        dots = VGroup(*[Dot(pos, radius=rad) for pos in map(axis.n2p, x_vals)])
        gradient = gradient or self.secant_gradient
        return dots.set_color_by_gradient(*gradient).set_style(**style)

    def trace_distance_func(self, mob, plane, func, time=4, color=None):
        origin = plane.c2p(0, 0)
        x, y = origin[:-1]
        curve_col = color or self.curve_color
        x_col, y_col = [axis.get_color() for axis in plane.axes]
        mob.move_to(origin)
        curve = plane.get_parametric_curve(
            lambda t: [t, func(t)], t_min=0, t_max=time, color=curve_col
        )

        h_line = DashedLine(start=origin, end=origin * 1.001, color=x_col)
        v_line = DashedLine(start=origin, end=origin * 1.001, color=y_col)
        self.add(h_line, v_line)

        def update_h_line(h_line):
            end = curve.pfp(1)
            start = array([x, end[1], 0])
            if all(end - start) == 0:
                end *= 1.00001
            line = DashedLine(start, end, color=x_col)
            h_line.become(line)

        def update_v_line(v_line):
            end = curve.pfp(1)
            start = array([end[0], y, 0])
            if all(end - start) == 0:
                end *= 1.00001
            v_line.become(DashedLine(start, end, color=y_col))

        def update_mob(mob):
            mob.move_to(h_line.get_start())

        mob.add_updater(update_mob)
        self.add(mob)

        self.play(
            ShowCreation(curve),
            UpdateFromFunc(h_line, update_h_line),
            UpdateFromFunc(v_line, update_v_line),
            run_time=time,
            rate_func=linear,
        )
        mob.remove_updater(update_mob)
        self.wait()

    def get_delta_text(self, variable, color, aligned_edge=None):
        aligned_edge = aligned_edge if aligned_edge is not None else DOWN
        text = Text("$\\triangle$", variable, color=color)
        text[0].scale(0.7)
        text.arrange(aligned_edge=aligned_edge, buff=0.02)
        return text

    def get_delta_lines(
        self,
        t,
        dt,
        curve=None,
        plane=None,
    ):
        curve = curve or self.curve
        plane = plane or self.plane

        x1, y1 = curve.function(t)[:2]
        x2, y2 = curve.function(t + dt)[:2]

        dx_line = Line([x1, y1, 0], [x2, y1, 0], color=self.x_color)
        dy_line = Line([x2, y2, 0], [x2, y1, 0], color=self.y_color)
        ds_line = Line([x1, y1, 0], [x2, y2, 0], color=self.curve_color)
        return VGroup(dx_line, dy_line, ds_line)


class AskQuestion(ArcLengthScene):
    CONFIG = {
        "include_background_rectangle": False,
        "camera_config": {"background_color": "#111111"},
    }

    def construct(self):
        self.remove(self.curve)
        t_axis, plane, curve = self.t_axis, self.plane, self.curve
        axes = VGroup(t_axis, plane).save_state()
        axes.scale(1.2, about_point=axes.get_left())
        particle_a = self.a.move_to(axes)

        r_t_group = self.setup_t_func_text().next_to(axes)
        r_t, equals, r_t_matrix = r_t_group

        self.add(*axes, self.t_dot)
        self.wait()
        self.play(FadeIn(particle_a, 10))
        self.wait()
        self.play(particle_a.move_to, plane.c2p(0, 0))
        self.wait(3)

        self.trace_curve(
            curve,
            particle_a,
            added_anims=[ApplyMethod(self.t_tracker.set_value, self.t_max)],
        )
        self.wait(3)

        self.play(Write(r_t))
        self.wait()
        self.play(
            Indicate(r_t[2]),
            Indicate(t_axis.label),
        )
        self.wait()
        self.play(
            GrowFromPoint(VGroup(equals, r_t_matrix.brackets), equals.get_center())
        )
        self.wait()
        self.play(Write(r_t_matrix.elements[0]), run_time=2)
        self.wait()
        self.play(Write(r_t_matrix.elements[1]), run_time=2)
        self.wait()
        self.play(r_t_group.shift, 2 * UP)
        self.play(FocusOn(t_axis.n2p(2)))

        self.show_map_from_ip_to_op((0, 4, 0.2), junction=r_t[2].get_center())
        self.wait()

        particle_a.add_updater(
            lambda p: p.move_to(curve.function(self.t_tracker.get_value()))
        )
        self.add(particle_a)

        self.t_max_pivot.suspend_updating()
        self.play(
            self.t_max_tracker.set_value,
            0.015,
            self.t_tracker.set_value,
            0,
        )
        self.wait()

        distance_text = Text("Distance", color=self.curve_color)
        arc_len_text = Text("Arc length", color=self.curve_color)
        question = VGroup(
            distance_text, Text("="), arc_len_text, Text("="), Text("? ?")
        )
        question.scale(1.25).arrange(DOWN)
        question.next_to(r_t_group, 4 * DOWN, aligned_edge=LEFT)

        self.play(
            self.t_max_tracker.set_value,
            self.t_max,
            self.t_tracker.set_value,
            self.t_max,
            Write(question[0]),
            run_time=self.run_time,
            rate_func=linear,
        )
        self.wait(3)
        self.play(Write(question[1:]), run_time=2)
        self.wait()
        self.play(ApplyWave(curve, amplitude=0.5), run_time=2)
        self.wait(8)

    def setup_t_func_text(self):
        r_t = Text("r", "(", "t", ")").scale(1.25)
        r_t[0].set_color(self.curve_color)
        r_t[2].set_color(self.t_color)
        r_t_matrix = self.get_coordinates(["t-sin(t)", "1-cos(t)"])
        [r_t_matrix.elements[i][0][6].set_color(self.t_color) for i in (0, 1)]
        return VGroup(r_t, Text("="), r_t_matrix).arrange()


class LoyalParticleAndTheInstruction(ArcLengthScene):
    CONFIG = {
        "include_background_rectangle": False,
        "camera_config": {"background_color": "#111111"},
        "dist_func": lambda t: 0.05 * t ** 3,
        "image_path": "sahil.png",
    }

    def setup(self):
        super().setup()

        sahil = ImageMobject(self.image_path).scale(3).stretch(1.2, 0)
        question = ImageMobject("AskQuestion.png").scale([3, 3, 1])
        sahil.to_corner(DL).shift(LEFT)
        question.to_edge(RIGHT)

        self.sahil, self.question = sahil, question
        self.a.add_updater(
            lambda a: a.move_to(self.curve.function(self.t_tracker.get_value()))
        )
        self.add(self.a)

        self.t_max_tracker.set_value(self.t_min + 0.015)

    def construct(self):
        particle_b = self.b.save_state().scale(3)
        axes = VGroup(self.t_axis, self.plane).save_state()
        # axes.scale(1.2, about_point=axes.get_left())
        t_axis, plane = axes
        particle_a = self.a
        curve = self.curve

        self.remove(*self.mobjects)
        self.add(self.sahil, self.question)
        self.wait(3)
        self.play(FadeOut(self.question), run_time=0.5)
        self.wait()
        self.play(FadeIn(particle_b, 2), run_time=2)
        self.wait(3)
        self.play(particle_b.to_edge, RIGHT)
        self.wait()

        self.show_example_instruction()
        self.play(
            *list(map(FadeIn, [axes, curve, self.t_dot, particle_a])), run_time=0.5
        )
        self.wait(5)

        self.show_specific_instruction()

    def show_example_instruction(self):
        b, sahil = self.b, self.sahil
        sahil_bubble = SpeechBubble(width=4, height=2.5)
        sahil_bubble.next_to(sahil).shift(2.5 * UL)
        b_bubble = SpeechBubble(width=2.5, height=1.5).flip().next_to(b, UL)
        sahil_text = sahil_bubble.write("Follow s(t) = 0.05 $t^{3}$")
        b_text = b_bubble.write("Sure thing !")

        self.wait(8)
        self.play(GrowFromPoint(sahil_bubble, sahil_bubble.get_corner(DL)))
        self.play(Write(sahil_text.content), run_time=2)
        self.wait()
        self.play(GrowFromPoint(b_bubble, b_bubble.get_corner(DR)))
        self.play(Write(b_text.content))
        self.wait()

        plane_config = merge_dicts_recursively(
            default_plane_config,
            {
                "x_axis_config": {"label": "t", "unit_size": 1.25},
                "y_axis_config": {"label": "s(t)", "unit_size": 1.4},
            },
        )
        plane = NumberPlane(**plane_config).center().to_edge(RIGHT)
        for mob in [*plane.y_axis.numbers, plane.y_axis.label]:
            mob.rotate(-PI / 2)

        self.play(FadeOut(b_text.content), FadeOut(b_bubble), FadeIn(plane))
        self.play(b.restore, b.move_to, plane.c2p(0, 0))
        self.trace_distance_func(b, plane, self.dist_func)
        mobs_to_fade = [mob for mob in self.mobjects if mob is not b]
        self.play(
            *list(map(FadeOutToPoint, mobs_to_fade, DOWN)), b.center, run_time=0.5
        )

    def show_specific_instruction(self):
        self.setup_specific_instruction()
        instruction = self.instruction
        self.play(FadeIn(instruction.background_rectangle), run_time=0.2)
        self.wait()

        b = self.b
        start = b.get_center() + 0.001 * LEFT
        b_dist_line = Line(start, b.get_center(), color=self.curve_color)

        t = self.t_tracker

        def update_line(line):
            dist = get_arc_length(self.t_func, 0, t.get_value(), 0.01)
            line.set_length((dist + 0.001) * self.plane.x_axis.unit_size)
            line.next_to(start, buff=0)

        t_decimal = DecimalNumber(0, num_decimal_places=2, color=self.t_color).scale(
            0.75
        )
        t_decimal.add_updater(lambda d: d.set_value(t.get_value()))
        t_group = (
            VGroup(Text("t", color=self.t_color), TexText("="), t_decimal)
            .arrange(buff=0.1)
            .add_updater(lambda t: t.next_to(b, UP))
        )

        b.add_updater(lambda b: b.move_to(b_dist_line.get_end()))
        self.a.add_updater(lambda a: a.move_to(self.curve.get_end()))
        self.add(b, t_group, self.a, self.t_max_tracker)
        self.t_max_pivot.suspend_updating()
        self.t_dot.suspend_updating()

        self.play(
            AnimationGroup(
                ApplyMethod(t.set_value, 2, run_time=2),
                UpdateFromFunc(b_dist_line, update_line, run_time=2),
                Write(instruction[:3], run_time=4),
            )
        )
        self.wait()
        self.t_dot.resume_updating()
        self.play(
            AnimationGroup(
                ApplyMethod(self.t_max_tracker.set_value, 2, run_time=2),
                Write(instruction[3:], run_time=4),
            )
        )
        self.wait(2)

        def show_comparision():
            ref_lines = VGroup(
                *[
                    DashedLine(p, p + 0.5 * DOWN)
                    for p in b_dist_line.get_start_and_end()
                ]
            )
            curve_line = self.curve.copy()
            b_line_copy = b_dist_line.copy()
            self.add(curve_line, b_line_copy)
            self.play(ShowCreation(ref_lines), b_line_copy.shift, 0.5 * DOWN)
            self.play(Transform(curve_line, b_line_copy), run_time=2)
            self.wait()
            self.play(
                Indicate(t_group, scale_factor=1.5),
                Indicate(self.t_dot, scale_factor=1.5),
            )
            self.wait()
            self.play(FadeOut(curve_line), FadeOut(ref_lines), FadeOut(b_line_copy))
            self.wait(2)

        show_comparision()

        self.play(
            t.set_value,
            4,
            UpdateFromFunc(b_dist_line, update_line),
            self.t_max_tracker.set_value,
            4,
            run_time=2,
        )
        self.wait(2)
        show_comparision()

        self.wait(6)

        t_decimal.suspend_updating()
        self.play(
            t.set_value,
            1,
            self.t_max_tracker.set_value,
            1,
            run_time=6,
            rate_func=there_and_back,
        )
        self.wait(6)

    def setup_specific_instruction(self):
        # use Paragraph ra, arey entra idi
        instruction = VGroup(
            Text("The distance particle B travels along a"),
            Text("straight line in a certain time t,"),
            Text("should be the same as that of the distance"),
            Text("travelled by particle A, in the same time t."),
        ).arrange(DOWN, aligned_edge=LEFT)

        instruction[0][0][3:11].set_color(self.curve_color)
        instruction[0][0][11:20].set_color(self.b.get_color())
        instruction[1][0][-2].set_color(self.t_color)
        instruction[2][0][-1:-9:-1].set_color(self.curve_color)
        instruction[3][0][11:20].set_color(self.a.get_color())
        instruction[3][0][-2].set_color(self.t_color)

        instruction.add_background_rectangle(
            stroke_opacity=1, stroke_width=1, stroke_color=WHITE, buff=0.5
        )
        instruction.scale(0.7).to_corner(UR, buff=0.1)
        self.instruction = instruction


class SecantPathAssumption(ArcLengthScene):
    CONFIG = {
        "include_background_rectangle": False,
        "camera_config": {"background_color": "#111111"},
        "dt_max": 1,
        "dt_min": 0.1,
        "b_start": 2 * UP,
    }

    def setup(self):
        ArcLengthScene.setup(self)
        self.setup_assumption_text()
        VGroup(self.t_axis, self.plane).to_corner(DL)
        self.t_dots = always_redraw(
            lambda: self.get_dots_on_axis(
                self.t_axis,
                self.t_min,
                self.t_max,
                self.dt_tracker.get_value(),
                stroke_color=WHITE,
                stroke_width=1,
                stroke_opacity=1,
            )
        )
        self.secant_group = always_redraw(
            lambda: VGroup(
                *self.get_secant_lines_and_dots(
                    self.curve, self.t_min, self.t_max, self.dt_tracker.get_value()
                )
            )
        )
        self.add(
            self.t_axis,
            self.plane,
            self.t_dot,
            self.curve,
            self.a.move_to(self.plane.c2p(0, 0)),
        )

        t_decimal = DecimalNumber(
            self.dt_max, num_decimal_places=2, color=self.t_color
        ).scale(0.85)
        t_decimal.add_updater(lambda d: d.set_value(self.dt_tracker.get_value()))
        delta_t_text = Text("$\\triangle$", "t", color=self.t_color)
        delta_t_text[0].scale(0.75)
        delta_t_text[1].scale(1.25)
        delta_t_text.arrange(aligned_edge=DOWN, buff=0)
        self.dt_group = (
            VGroup(delta_t_text, Text("="), t_decimal)
            .arrange(buff=0.1)
            .next_to(self.t_axis, UP)
        )
        # self.setup_assumption_text()

    def construct(self):
        self.wait(5)
        self.play(
            ShowCreation(self.secant_group, lag_ratio=1),
            Write(self.assumption),
            run_time=3,
        )
        self.play(LaggedStartMap(Indicate, self.secant_group[1]))
        self.play(FocusOn(self.t_axis.n2p(2)))
        self.play(LaggedStartMap(GrowFromCenter, self.t_dots, lag_ratio=0.5))
        self.play(Write(self.dt_group), run_time=2)

        self.play(
            self.t_dots.become,
            self.secant_group[1].copy(),
            run_time=3,
            rate_func=there_and_back_with_pause,
        )
        self.wait(2)

        self.move_along_secant_lines(self.a, self.secant_group[0], self.dt_max)
        self.wait(2)

        self.secant_group.save_state()
        self.collapse_secant_lines(
            *self.secant_group, self.plane.c2p(0, 3) + 0.5 * RIGHT, run_time=2
        )
        self.wait(2)
        self.play(Restore(self.secant_group), run_time=2)
        self.wait()
        self.write_delta_s_components()

        # particle b takes over
        self.wait(6)
        self.b.move_to(self.b_start)
        self.play(FadeIn(self.b, 5), run_time=2)
        self.wait()

        b_path = always_redraw(
            lambda: self.collapse_secant_lines(
                *self.secant_group.copy(), self.b_start, animate=False
            )
        )

        self.play(ShowCreation(b_path), run_time=2)
        self.wait()
        self.bring_to_front(self.a, self.b)
        self.a.set_fill(opacity=0.5)
        self.b.set_fill(opacity=0.5)

        for i in range(len(self.secant_group[0])):
            self.play(
                MoveAlongPath(self.a, self.secant_group[0][i]),
                MoveAlongPath(self.b, b_path[0][i]),
                self.t_tracker.set_value,
                (i + 1) * self.dt_tracker.get_value(),
                run_time=self.dt_tracker.get_value(),
                rate_func=linear,
            )
        self.wait()

        ref_lines = VGroup(
            *[
                DashedLine(dot.get_center(), dot.get_center() + DOWN)
                for dot in b_path[1]
            ]
        )
        b_path.suspend_updating()
        self.secant_group.save_state()
        self.collapse_secant_lines(
            *self.secant_group,
            self.b_start + DOWN,
            added_anims=[ShowCreation(ref_lines)],
            run_time=2,
        )  # why doesn't rate_func = there_and_back work?
        self.wait(2)
        self.play(Restore(self.secant_group), FadeOut(ref_lines))
        self.wait(2)
        b_path.resume_updating()

        self.write_velocity_expression()
        self.wait()

        # plot velocity
        self.play(
            self.velocity_eq.next_to,
            b_path,
            UP,
            {"aligned_edge": LEFT},
            self.a.move_to,
            self.plane.c2p(0, 0),
            self.t_tracker.set_value,
            self.t_min,
            self.b.move_to,
            self.b_start,
        )
        self.wait(5)
        self.plot_velocity_graph(b_path)
        self.wait(5)  # If you've done some calc

        self.b_path = b_path
        self.let_the_deltas_approach_zero()

    def let_the_deltas_approach_zero(self):
        # hide rhs and only show plane and t_axis ?? --> failed
        self.riemann_rects.add_updater(
            lambda r: r.become(
                self.get_riemann_rects(
                    self.dt_tracker.get_value(), self.t_min, self.t_max
                )
            )
        )
        self.velocity_step_graph.add_updater(
            lambda c: c.become(
                self.get_step_graph(
                    self.dt_tracker.get_value(),
                    self.t_min_tracker.get_value(),
                    self.t_max_tracker.get_value(),
                )
            )
        )
        self.add(self.riemann_rects, self.velocity_step_graph)

        self.play(FocusOn(self.dt_group), FocusOn(self.secant_group))
        self.wait()
        self.play(self.dt_tracker.set_value, 0.5, run_time=6, rate_func=linear)
        self.wait(2)
        self.play(self.dt_tracker.set_value, self.dt_min, run_time=6, rate_func=linear)
        self.wait(4)

        self.play(Indicate(self.velocity_eq[1][1][3:8]))
        self.wait()
        self.play(Indicate(self.velocity_eq[1][1][12:17]))
        self.wait()

        v_t = TexText("\\sqrt{x'(t)^{2}+y'(t)^{2}}").scale(0.8)
        v_t[0][2].set_color(self.x_color)
        v_t[0][9].set_color(self.y_color)
        [v_t[0][i].set_color(self.t_color) for i in (5, 12)]
        v_t.next_to(self.velocity_eq[1][0])
        self.play(Transform(self.velocity_eq[1][1], v_t), run_time=2)
        self.wait(4)

        [rect.save_state() for rect in self.riemann_rects]
        self.play(
            LaggedStart(
                *[
                    ApplyMethod(rect.stretch, 0.001, 1, {"about_point": rect.get_top()})
                    for rect in self.riemann_rects
                ],
            ),
            run_time=2,
        )
        self.wait()

        v_func = VGroup(TexText("="), v_t.copy()).arrange(buff=0.2)
        v_func.next_to(self.velocity_axes.y_axis.label, buff=0.1)
        self.play(Write(v_func[0]), TransformFromCopy(v_t, v_func[1]), run_time=2)
        self.wait(4)
        self.play(LaggedStartMap(Restore, self.riemann_rects), run_time=2)
        self.wait(6)

        integral = TexText("\\int_{0}^{4}\\sqrt{x'(t)^{2}+y'(t)^{2}}\\ dt")
        [integral[0][i].set_color(self.t_color) for i in (8, 15, 18, 19)]
        integral[0][5].set_color(self.x_color)
        integral[0][12].set_color(self.y_color)
        integral.next_to(self.riemann_rects, UP, buff=0.1)
        integral.scale(0.7)
        self.play(Write(integral), run_time=4)
        self.wait(3)
        self.play(ApplyWave(self.curve, amplitude=0.6), run_time=2)
        self.wait(2)
        self.play(Indicate(integral))
        self.wait(8)

    def plot_velocity_graph(self, b_path):
        self.play(FadeIn(self.velocity_axes))
        self.wait()
        for i in range(len(self.secant_group[0])):
            self.play(
                MoveAlongPath(self.a, self.secant_group[0][i]),
                MoveAlongPath(self.b, b_path[0][i]),
                ShowCreation(self.velocity_step_graph[i]),
                self.t_tracker.set_value,
                (i + 1) * self.dt_tracker.get_value(),
                run_time=self.dt_tracker.get_value(),
                rate_func=linear,
            )
        self.wait(8)

        def get_brace(
            index,
            t,
        ):
            brace = Brace(b_path[0][index])
            comment = TexText("\\triangle s", "=", f"v({t}).\\triangle t")
            comment[0].set_color(b_path[0][index].get_color())
            comment[-1][0].set_color(self.secant_gradient)
            [comment[-1][i].set_color(self.t_color) for i in (2, 5, 6)]
            comment.scale(0.75).next_to(brace, DOWN, buff=0.1)
            comment.add_background_rectangle(
                stroke_color=WHITE, stroke_opacity=1, buff=0.1
            )
            return VGroup(brace, comment)

        b_ds_brace = get_brace(0, 0)
        self.play(GrowFromCenter(b_ds_brace))
        self.wait()
        for i in range(len(b_path[0]) - 1):
            self.play(b_ds_brace.become, get_brace(i + 1, i + 1))
            self.wait()
        self.wait(2)
        self.play(ApplyWave(b_path), run_time=2)
        self.wait(2)

        [
            mob.save_state().stretch(0.001, 1, about_point=mob.get_top())
            for mob in self.riemann_rects
        ]
        # [rect.stretch(0.001, 1, about_point=rect.get_top()) for rect in self.riemann_rects]
        self.play(
            LaggedStartMap(Restore, self.riemann_rects, lag_ratio=0.2), run_time=4
        )
        self.wait()
        self.play(b_ds_brace.become, get_brace(0, 0))

        def get_rect_braces(index, t):
            dt_brace = Brace(self.riemann_rects[index], UP)
            dt_text = dt_brace.get_tex("\\triangle t").set_color(self.t_color)
            v_brace = Brace(self.riemann_rects[index], LEFT)
            v_text = v_brace.get_tex(f"v({t})")
            v_text[0][0].set_color(self.secant_gradient)
            v_text[0][2:4].set_color(self.t_color)
            v_text.add_background_rectangle(buff=0.1)
            dt = VGroup(dt_brace, dt_text)
            v = VGroup(v_brace, v_text)
            return VGroup(v, dt)

        v_brace = get_rect_braces(0, 0)
        self.play(LaggedStartMap(GrowFromCenter, v_brace))
        self.wait(2)

        for i in (1, 2, 3):
            self.play(
                v_brace.become,
                get_rect_braces(i, i),
                b_ds_brace.become,
                get_brace(i, i),
            )
            self.wait(0.5)
        self.wait()
        self.play(*list(map(FadeOut, [v_brace, b_ds_brace])))
        self.wait()

    def write_velocity_expression(self):
        velocity = Text("Velocity").set_color_by_gradient(*self.secant_gradient)
        delta_st_text = TexText("\\frac{\\triangle s}{\\triangle t}")
        delta_st_text[0][:2].set_color(self.secant_group[0][2].get_color())
        delta_st_text[0][3:].set_color(self.t_color)
        delta_st = (
            VGroup(velocity, TexText("="), delta_st_text)
            .scale(0.75)
            .arrange()
            .next_to(self.plane)
        )
        expanded_delta_st = (
            TexText(
                "=",
                "\\sqrt{(\\frac{\\triangle x}{\\triangle t})^{2}+(\\frac{\\triangle y}{\\triangle t})^{2}}",
            )
            .scale(0.75)
            .next_to(delta_st)
        )
        expanded_delta_st[1][3:5].set_color(self.x_color)
        expanded_delta_st[1][12:14].set_color(self.y_color)
        [expanded_delta_st[1][i].set_color(self.t_color) for i in (6, 7, 15, 16)]

        self.play(Write(velocity))
        self.wait(2)
        self.play(Write(delta_st[1:]), run_time=2)
        self.wait(2)
        self.play(Indicate(self.delta_s_formula), Indicate(delta_st_text[0][:2]))
        self.wait(2)
        self.play(FadeIn(expanded_delta_st))
        self.wait(6)
        self.play(
            FadeOut(delta_st[1:]), expanded_delta_st.next_to, delta_st[0], {"buff": 0.1}
        )
        self.wait(2)

        velocity_eq = VGroup(velocity, expanded_delta_st)
        self.velocity_eq = velocity_eq

    def write_delta_s_components(self):
        ds = self.get_delta_text("s", self.curve_color)
        dx = self.get_delta_text("x", self.x_color)
        dy = self.get_delta_text("y", self.y_color, UP)

        delta_lines = self.get_delta_lines(2, self.dt_tracker.get_value())
        ds_col = self.secant_group[0][2].get_color()
        [mob.set_color(ds_col) for mob in [ds, delta_lines[-1]]]
        delta_lines_copy = delta_lines.copy()

        self.play(ShowCreation(delta_lines))
        self.add(delta_lines_copy)
        self.play(delta_lines_copy.move_to, 2 * RIGHT, delta_lines_copy.scale, 2)
        self.wait()

        [
            mob.next_to(line, direction=dir)
            for mob, line, dir in zip([dx, dy], delta_lines_copy[:-1], [DOWN, RIGHT])
        ]
        ds.move_to(delta_lines_copy[-1]).shift(0.3 * UL)

        self.play(Write(ds))
        self.wait(2)
        self.play(Write(dx), Write(dy), run_time=2)
        self.wait(2)

        delta_s_formula = (
            TexText(
                "\\triangle s", "=", "\\sqrt{(\\triangle x)^{2}+(\\triangle y)^{2}}"
            )
            .scale(0.75)
            .next_to(1.5 * UP)
        )
        delta_s_formula[0].set_color(ds_col)
        delta_s_formula[2][3:5].set_color(self.x_color)
        delta_s_formula[2][9:11].set_color(self.y_color)
        self.delta_s_formula = delta_s_formula
        self.play(FadeInFromPoint(delta_s_formula, DOWN), run_time=2)
        self.wait(2)
        self.play(
            delta_s_formula.next_to,
            self.t_axis,
            DOWN,
            *list(
                map(
                    FadeOut,
                    [delta_lines_copy, delta_lines, ds, dx, dy, self.assumption],
                )
            ),
            self.a.move_to,
            self.plane.c2p(0, 0),
            self.t_tracker.set_value,
            self.t_min,
        )

    def setup_assumption_text(self):
        assumption = (
            VGroup(
                Text("Assumption :"),
                Text("Particle A travels"),
                Text("along the secant lines."),
            )
            .scale(0.75)
            .arrange()
        )
        assumption[0].set_color_by_gradient(*self.secant_gradient)
        assumption[2].next_to(assumption[0], DOWN, aligned_edge=LEFT)
        assumption[1][0][:9].set_color(self.a.get_color())
        assumption[-1][0][8:-1].set_color_by_gradient(*self.secant_gradient)
        assumption.add_background_rectangle(
            buff=0.2, stroke_color=WHITE, stroke_width=2, stroke_opacity=1
        )
        assumption.to_corner(UR, buff=0.2)
        self.assumption = assumption


class SecantPathUptoRiemann(SecantPathAssumption):
    CONFIG = {}


class SecantPathUptoRiemannBlack(SecantPathAssumption):
    CONFIG = {"camera_config": {"background_color": BLACK}}


class DeltaTApproachesZero(SecantPathAssumption):  # n85
    CONFIG = {}


class DeltaTApproachesZeroBlack(SecantPathAssumption):  # n85
    CONFIG = {"camera_config": {"background_color": BLACK}}


class AskQuestionBlack(AskQuestion):
    CONFIG = {"camera_config": {"background_color": BLACK}}


class Essence(SecantPathAssumption):
    def construct(self):
        [mob.set_opacity(0.5) for mob in (self.a, self.b)]
        self.b.move_to(self.b_start)
        self.wait(2)
        self.play(ShowCreation(self.secant_group, lag_ratio=1), run_time=3)
        self.play(LaggedStartMap(Indicate, self.secant_group[1]))
        self.play(FocusOn(self.t_axis.n2p(2)))
        self.play(LaggedStartMap(GrowFromCenter, self.t_dots, lag_ratio=0.5))
        self.play(Write(self.dt_group), run_time=2)
        self.play(
            self.t_dots.become,
            self.secant_group[1].copy(),
            run_time=3,
            rate_func=there_and_back_with_pause,
        )
        self.wait(2)

        b_path = always_redraw(
            lambda: self.collapse_secant_lines(
                *self.secant_group.copy(), self.b_start, animate=False
            )
        )
        self.play(
            GrowFromCenter(self.b),
            ShowCreation(b_path, lag_ratio=1),
            FadeIn(self.velocity_axes),
            run_time=2,
        )
        self.wait(2)

        for i in range(len(self.secant_group[0])):
            self.play(
                MoveAlongPath(self.a, self.secant_group[0][i]),
                MoveAlongPath(self.b, b_path[0][i]),
                ShowCreation(self.velocity_step_graph[i]),
                self.t_tracker.set_value,
                (i + 1) * self.dt_tracker.get_value(),
                run_time=self.dt_tracker.get_value(),
                rate_func=linear,
            )

        self.wait(2)
        self.play(
            LaggedStart(
                *[
                    TransformFromCopy(line, rect)
                    for line, rect in zip(b_path[0], self.riemann_rects)
                ],
                lag_ratio=0.3,
                run_time=4,
            )
        )
        self.wait(2)

        self.riemann_rects.add_updater(
            lambda r: r.become(
                self.get_riemann_rects(
                    self.dt_tracker.get_value(), self.t_min, self.t_max
                )
            )
        )
        self.velocity_step_graph.add_updater(
            lambda c: c.become(
                self.get_step_graph(
                    self.dt_tracker.get_value(),
                    self.t_min_tracker.get_value(),
                    self.t_max_tracker.get_value(),
                )
            )
        )
        self.secant_group.resume_updating()
        self.add(self.secant_group, self.riemann_rects, self.velocity_step_graph)

        self.play(self.dt_tracker.set_value, self.dt_min, run_time=8, rate_func=linear)
        self.wait(4)


class EssenceBlack(Essence):
    CONFIG = {"camera_config": {"background_color": BLACK}}

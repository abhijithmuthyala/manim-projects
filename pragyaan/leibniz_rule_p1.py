from manimlib import *
from manimlib.once_useful_constructs.graph_scene import GraphScene


class IntroAndIntegrals(GraphScene):

    CONFIG = {
        "x_min": -1,
        "x_max": 3,
        "x_axis_width": 8,
        "y_min": -1,
        "y_max": 3,
        "y_axis_height": 5,
        "x_tick_frequency": 0.5,
        "y_tick_frequency": 0.5,
        "axes_color": "#cf0e4e",
        "graph_origin": LEFT + DOWN,
        "default_graph_colors": [TEAL_E, GREEN, YELLOW],
        "default_derivative_color": GREEN,
        "default_input_color": YELLOW,
        "stroke_width": 5,
        "num_rects": 200,
        "number_line_kwargs": {
            "include_numbers": True,
            "include_tip": True,
        },
        "func": lambda x: 2 * x ** 2 - x ** 3 + 1,
        "rieman_rects_kwargs": {
            "x_min": 0,
            "x_max": 2,
            "stroke_width": 0.1,
            "stroke_color": "#aa9f4b",
            "fill_opacity": 0.8,
            "start_color": "#d40b37",  # "#d40b37", "#d4b90b"
            "end_color": "#d4b90b",
        },
    }

    def construct(self):
        self.introduce_context()
        self.recollect_integral()

    def introduce_context(self):

        context = (
            Text("Leibnitz integral rule over constant limits")
            .set_width(FRAME_WIDTH - 1)
            .to_edge(UP, 1)
        )
        context.set_color("#d9aa26")
        underline = (
            Line(context.get_left(), context.get_right())
            .next_to(context, DOWN)
            .set_style(stroke_width=2, stroke_color="#a7f542")
        )

        formula = (
            TexText(
                "\\frac{\mathrm{d}}{\mathrm{d} t}\int_{a}^{b}f(x,t)dx = \int_{a}^{b}\\frac{\partial }{\partial t}f(x,t)dx"
            )
            .next_to(underline, 3.5 * DOWN)
            .set_width(FRAME_WIDTH - 2)
            .set_color(MAROON)
        )  # "#aa9f4b"

        self.add(context)
        self.wait(4.5)
        self.play(ShowCreation(underline), run_time=2)
        self.wait()
        self.play(DrawBorderThenFill(formula), run_time=2, rate_func=linear)
        self.wait(4)
        self.play(
            *[FadeOut(mob) for mob in self.mobjects if mob is not self.board],
            lag_ratio=0.15
        )

    def recollect_integral(self, **graph_kwargs):

        self.setup_axes()

        curve = self.get_graph(self.func)
        graph = VGroup(self.axes, curve).to_edge(LEFT)
        fx = (
            TexText("f(x) = 2x^{2} - x^{3} + 1")
            .set_color(YELLOW_D)
            .to_edge(UP, buff=1)
            .shift(1.5 * LEFT)
        )

        self.wait(1.5)
        self.play(Write(fx), lag_ratio=0.3, run_time=4)
        self.wait()
        self.play(ShowCreation(curve), run_time=1)
        self.wait()

        self.sweep_through_area(curve)
        self.wait()

        # divide into segments, raise the first set of rectangles from base
        eq_spaced_lines = VGroup()
        dx = ValueTracker(0.5)
        dx_val = DecimalNumber(
            dx.get_value(), include_sign=False, num_decimal_places=2
        ).next_to(self.underlying_area, 3 * DOWN)
        rieman_rects = self.get_riemann_rectangles(
            curve, dx=dx.get_value(), **self.rieman_rects_kwargs
        )
        delta_x = TexText("\\triangle x=").next_to(dx_val, LEFT)
        delta_x_brace = Brace(rieman_rects[0], DOWN, buff=SMALL_BUFF)

        for i in np.arange(0, 2.5, dx.get_value()):
            line = Line(
                self.x_axis.number_to_point(i), self.input_to_graph_point(i, curve)
            )
            eq_spaced_lines.add(line)
        self.play(Write(eq_spaced_lines), run_time=3)
        self.wait()
        self.play(Write(delta_x_brace), Write(delta_x), Write(dx_val))
        self.wait()
        self.play(
            *[
                GrowFromEdge(rect, line.get_start())
                for rect, line in zip(rieman_rects, eq_spaced_lines)
            ],
            *[FadeOut(line) for line in eq_spaced_lines],
            lag_ratio=0.15,
            run_time=2
        )
        self.wait()

        height = Brace(rieman_rects[0], LEFT)
        height.add(TexText("f(x)").next_to(height, LEFT))
        self.play(Write(height))
        self.wait(4)

        # sum of areas of rects approximates the area under curve
        approx_equals = TexText("\\approx ").move_to(
            self.area_equals[0][4].get_center()
        )
        equals_copy = self.area_equals[0][4].copy()
        sigma = TexText("\sum f(x)", "\\triangle x").move_to(
            self.area_equals[0][-1].get_center() + RIGHT
        )
        self.play(FocusOn(self.area_equals[0][-1]))
        self.play(
            ReplacementTransform(self.area_equals[0][-1], sigma),
            ReplacementTransform(self.area_equals[0][4], approx_equals),
            run_time=2,
        )
        self.wait(4)

        # delta x can be factored out from sigma
        self.play(
            sigma[1].shift,
            1.6 * LEFT,
            sigma[0].shift,
            RIGHT,
            run_time=4,
            rate_func=there_and_back_with_pause,
        )
        self.wait(3)

        # update rieman rects as delta x approaches 0
        rieman_rects.add_updater(
            lambda r: r.become(
                self.get_riemann_rectangles(
                    curve, dx=dx.get_value(), **self.rieman_rects_kwargs
                )
            )
        )
        dx_val.add_updater(lambda x: x.set_value(dx.get_value()))
        delta_x_brace.add_updater(
            lambda b: b.become(Brace(rieman_rects[0], DOWN, buff=SMALL_BUFF))
        )
        self.add(rieman_rects, dx_val, delta_x_brace)
        self.play(dx.set_value, 0.01, run_time=10, rate_func=linear)
        self.wait(6)

        # change in notation as dx-->0
        rect_approx = SurroundingRectangle(approx_equals, buff=SMALL_BUFF)
        rect_sigma = SurroundingRectangle(sigma[0][0], buff=SMALL_BUFF)
        rect_deltax = SurroundingRectangle(sigma[1], buff=MED_SMALL_BUFF)
        integrand = TexText("\\int_{0}^{2}").move_to(sigma.get_center())
        surr_rects = [rect_deltax, rect_sigma, rect_approx]
        transform_from = [sigma[1][-2], sigma[0][0], approx_equals]
        transform_to = [
            TexText("d").next_to(sigma[1][-1], LEFT, buff=0.05),
            integrand.shift(0.8 * LEFT),
            equals_copy,
        ]

        for i in range(3):
            self.play(ShowCreation(surr_rects[i]))
            self.remove(surr_rects[i])
            self.play(Transform(transform_from[i], transform_to[i]))
            self.wait()
        self.wait(6)

    def sweep_through_area(self, graph):
        sweeper = Triangle().scale(0.15).move_to(self.x_axis.number_to_point(0))
        sweeper.shift((sweeper.get_top()[1] - sweeper.get_center()[1]) * DOWN)
        l_pivot = sweeper.copy()
        r_pivot = sweeper.copy().shift(2 * self.space_unit_to_x * RIGHT)

        t = ValueTracker(0)
        area = self.get_area(graph, t_min=0, t_max=t.get_value())
        self.play(ShowCreation(l_pivot), ShowCreation(r_pivot), ShowCreation(area))
        self.wait(2)

        area.add_updater(
            lambda area: area.become(self.get_area(graph, t_min=0, t_max=t.get_value()))
        )
        self.add(area)

        self.area_equals = (
            Text("Area = ?").scale(1.5).next_to(graph, RIGHT).shift(5 * UP + 2 * LEFT)
        )
        self.area_equals[0][:4].set_color_by_gradient(BLUE, GREEN)

        self.play(
            sweeper.move_to,
            r_pivot,
            t.set_value,
            2,
            Write(self.area_equals),
            run_time=3,
            rate_func=smooth,
        )
        self.wait()

        self.underlying_area = area


class TheDerivative(GraphScene):

    CONFIG = {
        "x_min": -1,
        "x_max": 3,
        "x_axis_width": 8,
        "y_min": -1,
        "y_max": 3,
        "y_axis_height": 5,
        "x_tick_frequency": 0.5,
        "y_tick_frequency": 0.5,
        "axes_color": "#cf0e4e",
        "graph_origin": LEFT + DOWN,
        "default_graph_colors": [TEAL_E, GREEN, YELLOW],
        "default_derivative_color": GREEN,
        "default_input_color": YELLOW,
        "stroke_width": 5,
        "num_rects": 200,
        "number_line_kwargs": {
            "include_numbers": True,
            "include_tip": True,
        },
        "func": lambda x: 2 * x ** 2 - x ** 3 + 1,
        "rieman_rects_kwargs": {
            "x_min": 0,
            "x_max": 2,
            "stroke_width": 0.1,
            "stroke_color": "#aa9f4b",
            "fill_opacity": 0.8,
            "start_color": "#d40b37",  # "#d40b37", "#d4b90b"
            "end_color": "#d4b90b",
        },
    }

    def construct(self):
        curve = self.get_graph(self.func)
        graph = VGroup(self.axes, curve).to_edge(LEFT).shift(2 * LEFT)
        fx = (
            TexText("f(x) = 2x^{2} - x^{3} + 1")
            .set_color(YELLOW_D)
            .next_to(self.y_axis.number_to_point(3), buff=0.5)
        )

        text1 = Text("How sensitive the function is,")
        text1[0][3:12].set_color(YELLOW_D)
        text2 = Text("to tiny changes in input ?")
        context = (
            VGroup(text1, text2)
            .arrange_submobjects(DOWN, aligned_edge=LEFT)
            .scale(0.8)
            .to_corner(UR)
        )
        context.add_background_rectangle(
            stroke_color=YELLOW_D,
            stroke_width=1.5,
            stroke_opacity=1,
            opacity=0,
            buff=0.2,
        )

        self.add(graph, fx)
        self.wait(4)
        self.play(Write(context), run_time=3)
        self.wait()

        x = 0.5
        dx_tracker = ValueTracker(1)
        dx = DecimalNumber(
            dx_tracker.get_value(), include_sign=False, num_decimal_places=2
        )
        point1 = Dot(self.input_to_graph_point(x, curve)).scale(0.75)
        point2 = Dot(self.input_to_graph_point(x + dx.get_value(), curve)).scale(0.75)
        ref_line_kwargs = {"stroke_color": "#8b7c74", "stroke_width": 1.5}
        dx_line = Line(
            point1.get_center(),
            point1.get_center() + RIGHT * dx.get_value() * self.space_unit_to_x,
            **ref_line_kwargs
        )
        dy_line = Line(dx_line.get_end(), point2.get_center(), **ref_line_kwargs)
        secant_line = Line(
            point1.get_center(), point2.get_center(), color=GREEN, stroke_width=2
        ).scale(1.75)
        sct_line_width = secant_line.get_length()

        p = TexText("P").next_to(point1, UP + LEFT, buff=0.1).scale(0.8)
        p_coords = (
            TexText("P : ( a, f(a) )")
            .scale(0.8)
            .next_to(self.input_to_graph_point(2, curve))
        )

        v_l1 = Line(
            point1.get_center(), self.x_axis.number_to_point(x), **ref_line_kwargs
        )
        v_l2 = Line(
            point2.get_center(),
            self.x_axis.number_to_point(x + dx.get_value()),
            **ref_line_kwargs
        )

        dx_brace = Brace(Line(v_l1.get_end(), v_l2.get_end()))
        dx_text = TexText("\\triangle x = ")
        delta_x = VGroup(dx_text, dx).arrange_submobjects().next_to(dx_brace, DOWN)
        delta_x.add(dx_brace)

        dy_brace = Brace(dy_line, RIGHT)
        dy_text = TexText("\\triangle y")
        delta_y = (
            VGroup(dy_brace, dy_text).arrange_submobjects().next_to(dy_line, RIGHT)
        )

        self.play(GrowFromCenter(point1), Write(p), Write(p_coords), run_time=4)
        # self.wait(2)
        self.play(ShowCreation(dx_line))
        # self.wait()
        self.play(ShowCreation(v_l1), ShowCreation(v_l2), lag_ratio=0)
        self.play(Write(delta_x))
        self.wait()
        self.play(Write(delta_y), GrowFromCenter(point2))
        self.wait(4)

        slope = TexText(
            "\\frac{\\triangle y}{\\triangle x} ",
            "= \\frac{f(a+\\triangle x) - f(x)}{\\triangle x}",
        )
        slope.scale(0.8).to_edge(RIGHT).shift(1.5 * UP + 2.5 * LEFT)
        eval_slope = (
            TexText("= 4x-3x^{2}+\\triangle x .(2-3x) - (\\triangle x )^{2}")
            .scale(0.8)
            .next_to(slope[1][0], 2 * DOWN, aligned_edge=LEFT)
        )
        self.play(Write(slope[0]), ShowCreation(secant_line))
        self.wait()
        self.play(Write(slope[1]))
        self.wait()
        self.play(Write(eval_slope))
        self.wait()
        self.play(FadeOut(slope[1]), eval_slope.next_to, slope[0])
        self.wait()
        delta_y.fade(darkness=1)

        # updaters
        dx.add_updater(lambda x: x.set_value(dx_tracker.get_value()))
        point2.add_updater(
            lambda p: p.move_to(
                self.input_to_graph_point(x + dx_tracker.get_value(), curve)
            )
        )
        dx_line.add_updater(
            lambda l: l.put_start_and_end_on(
                point1.get_center(),
                point1.get_center()
                + RIGHT * dx_tracker.get_value() * self.space_unit_to_x,
            )
        )
        dy_line.add_updater(
            lambda l: l.put_start_and_end_on(dx_line.get_end(), point2.get_center())
        )
        secant_line.add_updater(
            lambda l: l.become(
                Line(
                    point1.get_center(),
                    point2.get_center(),
                    color=GREEN,
                    stroke_width=2,
                ).set_width(sct_line_width)
            )
        )
        v_l2.add_updater(
            lambda l: l.put_start_and_end_on(
                point2.get_center(), self.x_axis.number_to_point(x + dx.get_value())
            )
        )
        dx_brace.add_updater(
            lambda b: b.become(Brace(Line(v_l1.get_end(), v_l2.get_end())))
        )

        self.add(point2, dx_line, dy_line, secant_line, dx_brace, v_l2, dx)
        self.play(dx_tracker.set_value, 0.01, run_time=6)
        self.wait()

        zeros_brace = Brace(eval_slope[0][8:], DOWN)
        zeros_brace_text = Text("Approach zero").next_to(zeros_brace, DOWN).scale(0.8)
        approach_zero = VGroup(zeros_brace, zeros_brace_text)

        self.play(ShowCreationThenFadeOut(SurroundingRectangle(eval_slope)))
        self.wait()
        self.play(
            CircleIndicate(eval_slope[0][8:10]),
            CircleIndicate(eval_slope[0][18:]),
            Write(approach_zero),
            run_time=2,
        )

        self.play(
            ApplyMethod(eval_slope[0][7:].fade, darkness=1),
            ApplyMethod(approach_zero.fade, darkness=1),
        )
        self.wait(8)

        self.play(
            FadeOut(approach_zero),
            FadeOut(eval_slope[0][7:]),
            Transform(
                slope[0],
                TexText("\\frac{dy}{dx}").move_to(slope[0].get_center()).scale(0.8),
            ),
            run_time=2,
        )
        self.wait(2)

        deriv = TexText(" = {f}'(x)").scale(0.8).next_to(eval_slope[0][5])
        deriv[0][1:].set_color(YELLOW_D)
        self.play(Write(deriv), run_time=2)
        self.wait(2)

        approx_y = TexText("dy =", "{f}'(x)", ".dx").scale(0.8).shift(2 * RIGHT)
        approx_y[1].set_color(YELLOW_D)
        self.play(Write(approx_y[1]))
        self.wait(2)
        self.play(Write(approx_y[2]))
        self.wait(2)
        self.play(Write(approx_y[0]))
        self.wait(10)


class WhatAreWeLookingFor(GraphScene):
    CONFIG = {
        "x_min": -0.5,
        "x_max": 4,
        "x_axis_width": 7,
        "y_min": -1,
        "y_max": 4,
        "y_axis_height": 6,
        "x_tick_frequency": 0.5,
        "y_tick_frequency": 0.5,
        "y_axis_label": "$f(x,t)$",
        "axes_color": LIGHT_GREY,  # b9464f  #a95660 #b6497b  "#d8d776"
        "graph_origin": LEFT + DOWN,
        "default_graph_colors": [YELLOW_D],
        "default_derivative_color": GREEN,
        "default_input_color": YELLOW,
        "stroke_width": 5,
        "num_rects": 100,
        "number_line_kwargs": {
            "include_numbers": True,
            "include_tip": True,
        },
        "rieman_rects_kwargs": {
            "x_min": 0,
            "x_max": 2,
            "stroke_width": 0.5,
            "stroke_color": "#aa9f4b",
            "fill_opacity": 0.8,
            "start_color": "#d40b37",  # "#d40b37", "#d4b90b"
            "end_color": "#d4b90b",
        },
        "diff_area_kwargs": {
            "stroke_width": 0.1,
            "stroke_color": "#aa9f4b",
            "fill_opacity": 0.8,
        },
        "diff_area_cols": ["#d40b37", "#d4b90b"],
    }

    def construct(self):
        self.setup_axes()
        t_tracker = ValueTracker(1)
        func = lambda x: 2 * x ** 2 - x ** 3 + 0.5 * t_tracker.get_value() * (x + 1)
        curve = self.get_graph(func, x_min=-0.5, x_max=2.5)
        graph = VGroup(self.axes, curve).to_edge(RIGHT, buff=0.1).shift(DOWN)
        curve_copy = curve.copy()

        formula = (
            TexText(
                "\\frac{\mathrm{d}}{\mathrm{d} t}\int_{a}^{b}f(x,t)dx = \int_{a}^{b}\\frac{\partial }{\partial t}f(x,t)dx"
            )
            .set_color("#d8d776")
            .scale(0.85)
            .to_edge(LEFT)
            .shift(1.5 * UP)
        )
        function = (
            TexText("f(x,t) = 2x^{2} - x^{3} + \\frac{(x+1)}{2} \\ t")
            .next_to(formula[0][0], 1.5 * UP, aligned_edge=LEFT)
            .scale(0.85)
        )
        function.set_color(YELLOW_D)
        self.add(formula)

        surr_rect_kwargs = {
            "stroke_width": 1,
            "stroke_color": YELLOW_D,
            "buff": SMALL_BUFF,
        }
        fxt_surr_rect = SurroundingRectangle(formula[0][7:13], **surr_rect_kwargs)
        integral_brace = Brace(formula[0][4:15], color="#d8d776")
        integral_brace.add(
            Text("area", color="#d8d776").scale(0.8).next_to(integral_brace, DOWN)
        )
        deriv_brace = Brace(formula[0][0:15], color="#d8d776").shift(DOWN)
        deriv_brace.add(
            Text("rate of change of area", color="#d8d776")
            .scale(0.8)
            .next_to(deriv_brace, DOWN, aligned_edge=formula.get_edge_center(LEFT))
        )

        self.wait(4)
        self.play(FadeOut(formula[0][15:]))
        self.wait(2)
        self.play(ShowCreation(fxt_surr_rect))
        self.wait(2)
        self.play(Write(function), run_time=0.5)
        self.wait(2)
        self.play(Write(graph))
        self.wait()
        self.add(curve_copy)

        t_num_line_kwargs = {
            "color": LIGHT_GREY,
            "x_min": 0,
            "x_max": 4,
            "unit_size": 1,
            "tick_frequency": 0.5,
        }
        t_num_line = NumberLine(**t_num_line_kwargs).to_corner(UR)
        t_num_line.add(TexText("t").set_color(YELLOW_D).next_to(t_num_line, buff=0.1))
        sweeper = (
            Triangle(color=YELLOW_D).scale(0.15).move_to(t_num_line.number_to_point(1))
        )
        sweeper.rotate(PI, about_point=sweeper.get_center())
        sweeper.shift((sweeper.get_top()[1] - sweeper.get_center()[1]) * UP)
        self.add(t_num_line, sweeper)

        curve.add_updater(
            lambda c: c.become(
                self.get_graph(
                    lambda x: 2 * x ** 2
                    - x ** 3
                    + 0.5 * t_tracker.get_value() * (1 + x),
                    x_min=-0.5,
                    x_max=2.5,
                )
            )
        )
        self.add(curve)

        self.play(
            t_tracker.set_value,
            3,
            sweeper.shift,
            2 * RIGHT * t_num_line.unit_size,
            run_time=4,
            rate_func=there_and_back,
        )
        self.remove(fxt_surr_rect, curve_copy)
        self.wait()

        # the integral
        area = self.get_area(curve, 0.5, 2)
        lower_bound = (
            TexText("a")
            .scale(0.75)
            .next_to(self.x_axis.number_to_point(0.5), LEFT + UP, buff=0.1)
        )
        upper_bound = (
            TexText("b")
            .scale(0.75)
            .next_to(self.x_axis.number_to_point(2), RIGHT + UP, buff=0.1)
        )
        bounds = VGroup(lower_bound, upper_bound)

        self.play(Write(integral_brace[0]))
        self.wait()
        self.play(Write(integral_brace[1]), ShowCreation(area), Write(bounds))
        self.wait(3)
        self.play(ShowCreation(deriv_brace[0]))
        self.wait(3)
        self.play(Write(deriv_brace[1]))

        curve.add_updater(
            lambda c: c.become(
                self.get_graph(
                    lambda x: 2 * x ** 2
                    - x ** 3
                    + 0.5 * t_tracker.get_value() * (1 + x),
                    x_min=-0.5,
                    x_max=2.5,
                )
            )
        )
        area.add_updater(lambda a: a.become(self.get_area(curve, 0.5, 2)))
        self.add(curve, area)

        for i in range(2):
            self.play(
                sweeper.shift,
                2 * RIGHT * t_num_line.unit_size,
                t_tracker.set_value,
                3,
                run_time=4,
                rate_func=there_and_back,
            )
            self.wait()

        self.play(
            *[FadeOut(mob) for mob in [integral_brace, deriv_brace, function]],
            formula[0][:15].shift,
            1.5 * UP
        )
        self.wait()

        fxt = (
            TexText("f(x,t)")
            .scale(0.8)
            .next_to(self.input_to_graph_point(2.4, curve_copy))
            .set_color("#ff6500")
        )
        self.play(Write(fxt))

        area.clear_updaters()

        diff_area = self.get_change_in_area(area, 1)
        self.add(diff_area)

        dt_tracker = ValueTracker(1)
        delta_t = TexText("\\triangle t =").scale(0.8).next_to(t_num_line, DOWN)
        dt = (
            DecimalNumber(
                dt_tracker.get_value(), include_sign=False, num_decimal_places=2
            )
            .scale(0.8)
            .next_to(delta_t)
        )
        self.add(sweeper.copy(), curve_copy)

        curve.add_updater(
            lambda c: c.become(
                self.get_graph(
                    lambda x: 2 * x ** 2
                    - x ** 3
                    + 0.5 * t_tracker.get_value() * (1 + x),
                    x_min=-0.5,
                    x_max=2.5,
                )
            )
        )
        diff_area.add_updater(
            lambda a: a.become(self.get_change_in_area(area, t_tracker.get_value()))
        )
        self.add(curve, diff_area)

        self.play(
            t_tracker.set_value,
            t_tracker.get_value() + dt_tracker.get_value(),
            sweeper.shift,
            dt_tracker.get_value() * RIGHT * t_num_line.unit_size,
            run_time=1,
        )

        fx_delta_t = (
            TexText("f(x,t+\\triangle t)")
            .scale(0.8)
            .next_to(self.input_to_graph_point(2.4, curve))
            .set_color("#ff6500")
        )
        self.play(Write(delta_t), Write(dt))
        self.play(Write(fx_delta_t))
        self.wait()

        delta_a = (
            TexText("\\triangle A")
            .set_color_by_gradient(*self.diff_area_cols)
            .scale(0.8)
        )
        delta_a.to_edge(LEFT).shift(1.5 * UP)
        self.add(delta_a)
        self.play(TransformFromCopy(diff_area, delta_a))
        self.wait()

        # approximating areas with riemann rects
        dx_tracker = ValueTracker(0.25)
        dx = DecimalNumber(
            dx_tracker.get_value(), include_sign=False, num_decimal_places=2
        ).scale(0.8)
        curve2 = self.get_graph(
            lambda x: 2 * x ** 2 - x ** 3 + 0.5 * (x + 1), x_min=-0.5, x_max=2.5
        ).move_to(curve_copy)
        approx_area = self.get_riemann_rectangles(
            curve2, x_min=0.5, x_max=2, dx=0.25, stroke_width=0.7, fill_opacity=0.8
        )
        dx_brace = Brace(approx_area[0])
        dx_brace.add(TexText("\\triangle x =").scale(0.8).next_to(dx_brace, DOWN))
        dx.next_to(dx_brace[1])
        delta_x = VGroup(dx_brace, dx)

        approx_diff_area = self.get_change_in_area(approx_area, t_tracker.get_value())
        # had to create curve2 same as curve_copy ; self.get_riemann_rectangles(curve_copy) was giving unexpected results

        self.play(FadeOut(area), FadeOut(diff_area), lag_ratio=0)
        self.wait()
        self.play(
            *[GrowFromEdge(mob, mob.get_bottom()) for mob in approx_area],
            Write(delta_x),
            run_time=4
        )
        self.wait(3)

        self.play(
            *[GrowFromEdge(mob, mob.get_vertices()[1]) for mob in approx_diff_area],
            run_time=3
        )
        self.wait(4)

        # change in area of a sample rect
        sample_rect = approx_diff_area[2]
        sample_rect_pos = sample_rect.get_center()
        self.play(sample_rect.next_to, delta_a, 6 * DOWN)
        self.wait()
        delta_h = Brace(sample_rect, RIGHT)
        delta_h.add(TexText("\\triangle h").next_to(delta_h, buff=0.2).scale(0.8))
        delta_x = Brace(sample_rect)
        delta_x.add(TexText("\\triangle x").scale(0.8).next_to(delta_x, DOWN, buff=0.2))
        sample_rect_dims = VGroup(delta_h, delta_x)
        self.play(Write(sample_rect_dims))
        self.wait()
        approx_delta_h = (
            TexText("\\approx \\frac{\partial f(x,t)}{\partial t} \ \\triangle t")
            .scale(0.8)
            .next_to(delta_h)
        )
        self.play(Write(approx_delta_h), run_time=5)
        self.wait(2)

        area_of_sample_rect = (
            TexText("area")
            .next_to(sample_rect, 3 * RIGHT + 2 * DOWN)
            .set_color(sample_rect.get_color())
            .scale(0.8)
        )
        area_of_sample_rect.add(approx_delta_h.copy().next_to(area_of_sample_rect))
        area_of_sample_rect.add(delta_x[-1].copy().next_to(area_of_sample_rect))
        self.play(Write(area_of_sample_rect), run_time=2)
        self.wait(2)

        self.play(
            ApplyWave(approx_diff_area, amplitude=0.5), lag_ratio=0.15, run_time=2
        )
        self.wait()

        sigma = (
            TexText(
                "\\approx \sum \\frac{\partial f(x,t)}{\partial t}\\triangle t \ \\triangle x"
            )
            .scale(0.8)
            .next_to(delta_a)
        )

        FadeOut(area_of_sample_rect[0])
        self.play(Write(sigma), run_time=2)
        self.wait(5)

        # ratio delta a over delta t
        underline_da = Line(
            delta_a.get_left() + 0.4 * DOWN,
            delta_a.get_right() + 0.4 * DOWN,
            stroke_width=1.5,
        )
        self.play(sigma[0][12:14].shift, 2.1 * LEFT, sigma[0][1:12].shift, 0.5 * RIGHT)
        self.wait(2)
        self.play(
            ShowCreation(underline_da),
            ApplyMethod(
                sigma[0][12:14].next_to, underline_da, DOWN + 0.3 * RIGHT, buff=0.1
            ),  # delta t
            ApplyMethod(sigma[0][1:12].shift, 0.3 * LEFT + 0.3 * DOWN),  # sigma f
            ApplyMethod(sigma[0][0].shift, 0.1 * RIGHT + 0.3 * DOWN),  # approx
            ApplyMethod(sigma[0][14:].shift, 0.3 * LEFT + 0.3 * DOWN),  # deltax
        )
        self.wait(4)

        self.play(
            FadeOut(delta_h[0]),
            FadeOut(delta_x),
            FadeOut(area_of_sample_rect),
            sample_rect.move_to,
            sample_rect_pos,
            lag_ratio=0,
        )
        self.wait(3)

        # let the deltas approach zero
        # dx approaches 0
        approx_area.add_updater(
            lambda a: a.become(
                self.get_riemann_rectangles(
                    curve2,
                    x_min=0.5,
                    x_max=2,
                    dx=dx_tracker.get_value(),
                    stroke_width=0.1,
                    fill_opacity=0.8,
                )
            )
        )
        approx_diff_area.add_updater(
            lambda a: a.become(
                self.get_change_in_area(approx_area, t_tracker.get_value())
            )
        )
        dx.add_updater(lambda x: x.set_value(dx_tracker.get_value()))
        dx_brace[0].add_updater(lambda b: b.become(Brace(approx_area[0])))
        self.add(approx_diff_area, approx_area, dx, dx_brace)
        self.play(dx_tracker.set_value, 0.01, run_time=6)
        self.wait(3)
        # dt approaches 0

        curve.clear_updaters()
        approx_diff_area.add_updater(
            lambda a: a.become(
                self.get_change_in_area(approx_area, 1 + dt_tracker.get_value())
            )
        )
        dt.add_updater(lambda t: t.set_value(dt_tracker.get_value()))
        curve.add_updater(
            lambda c: c.become(
                self.get_graph(
                    lambda x: 2 * x ** 2
                    - x ** 3
                    + 0.5 * (x + 1) * (1 + dt_tracker.get_value())
                )
            )
        )
        self.add(approx_diff_area, dt, curve)
        self.play(
            ApplyMethod(sweeper.shift, LEFT * t_num_line.unit_size * 0.9),
            dt_tracker.set_value,
            0.1,
            run_time=2,
        )
        self.wait()

        dh_surr_rect = SurroundingRectangle(VGroup(delta_h[1], approx_delta_h))
        self.add(dh_surr_rect)
        self.play(
            Transform(
                approx_delta_h[0][0],
                TexText("=").scale(0.8).move_to(approx_delta_h[0][0]),
            ),
            run_time=2,
        )
        self.wait(2)
        # self.remove()
        # self.wait()
        self.remove(dh_surr_rect, approx_delta_h, delta_h[1])
        self.wait()

        deriv_surr_rect = SurroundingRectangle(
            VGroup(delta_a, sigma), stroke_color=YELLOW_D, stroke_width=1.5
        )
        self.add(deriv_surr_rect)
        self.wait()

        arrow = (
            Vector(color=YELLOW_D)
            .rotate(3 * PI / 2, about_point=ORIGIN)
            .next_to(sigma, DOWN)
        )
        approach_zero = (
            VGroup(
                TexText("\\triangle x\\rightarrow 0"),
                TexText("\\triangle t\\rightarrow 0"),
            )
            .scale(0.8)
            .arrange_submobjects(DOWN)
            .next_to(arrow, buff=0.2)
        )
        arrow.add(approach_zero)
        self.play(Write(arrow))
        self.wait(2)

        final_eq = (
            TexText(
                "\\frac{\mathrm{d} A}{\mathrm{d} t}",
                " =\int_{a}^{b}\\frac{\partial f(x,t)}{\partial t} \ dx",
            )
            .scale(0.85)
            .next_to(arrow, DOWN)
        )
        final_eq.set_color("#d8d776")
        self.play(Write(final_eq), run_time=2, lag_ratio=0.15)
        self.wait(3)

        self.play(final_eq[1].copy().next_to, formula[0][14])
        self.wait(5)

    def get_change_in_area(self, area, t_val):

        func = lambda x, t: 2 * x ** 2 - x ** 3 + 0.5 * t * (x + 1)
        width = area[0].get_width()
        diff_area = VGroup()

        for index, x in enumerate(np.arange(0.5, 2, width / self.x_axis.unit_size)):
            height = (func(x, t_val) - func(x, 1)) * self.y_axis.unit_size
            rect = Rectangle(width=width, height=height, **self.diff_area_kwargs)
            rect.next_to(area[index], UP, buff=0)
            diff_area.add(rect)

        diff_area.set_submobject_colors_by_gradient(*self.diff_area_cols)
        return diff_area

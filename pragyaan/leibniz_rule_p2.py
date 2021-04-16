from manimlib import *
from manimlib.once_useful_constructs.graph_scene import GraphScene


class ExtendToGeneralCase2(GraphScene):

    CONFIG = {
        "x_min": -0.5,
        "x_max": 3,
        "x_axis_width": 6,
        "x_tick_frequency": 0.5,
        "y_min": -1,
        "y_max": 4,
        "y_axis_height": 6,
        "y_tick_frequency": 0.5,
        "y_axis_label": "$f(x,t)$",
        "axes_color": LIGHT_GREY,
        "default_graph_colors": [ORANGE],
        "default_derivative_color": GREEN,
        "default_input_color": YELLOW_D,
        "area_opacity": 0.8,
        "num_rects": 150,
        "init_limits": [0.5, 2],
        "vert_area_cols": ["#d40b37", "#d4b90b"],
        "left_rect_kwargs": {
            "stroke_width": 1,
            "stroke_color": BLUE,
            "fill_color": YELLOW_D,
            "fill_opacity": 1,
        },
        "right_rect_kwargs": {
            "stroke_width": 1,
            "stroke_color": BLUE,
            "fill_color": MAROON,
            "fill_opacity": 1,
        },
    }

    def construct(self):
        context = (
            Text("Leibnitz integral rule for varying limits")
            .set_width(FRAME_WIDTH - 1)
            .set_color(YELLOW_D)
            .to_edge(UP)
        )
        underline = Line(
            context.get_left(), context.get_right(), stroke_width=2
        ).next_to(context, DOWN)
        formula = (
            TexText(
                "\\frac{\mathrm{d}}{\mathrm{d} t}\int_{a(t)}^{b(t)}f(x,t)dx",
                "=",
                "\int_{a(t)}^{b(t)} \\frac{\partial f(x,t) }{\partial t}dt \ + \ \\frac{\mathrm{d}b(t) }{\mathrm{d} t}\ f(b(t),t) \ - \ \\frac{\mathrm{d} a(t)}{\mathrm{d} t}\ f(a(t),t",
            )
            .next_to(underline, 3.5 * DOWN)
            .set_width(FRAME_WIDTH - 1)
            .set_style(stroke_color=LIGHT_GREY)
        )
        self.add(context)
        self.wait()
        self.play(ShowCreation(underline), run_time=2)
        self.wait()
        self.play(FadeIn(formula), lag_ratio=0.15, run_time=3)
        self.wait(4)
        self.play(
            *[FadeOut(mob) for mob in [context, underline, formula[1:]]],
            formula[0].scale,
            0.8,
            formula[0].to_corner,
            UL,
            0.2,
        )
        self.wait()

        t_tracker = ValueTracker(1)
        dt = DecimalNumber(
            t_tracker.get_value(), include_sign=False, num_decimal_places=2
        ).scale(0.6)
        t_num_line_kwargs = {
            "color": LIGHT_GREY,
            "x_min": 0,
            "x_max": 4,
            "unit_size": 1,
            "tick_frequency": 0.5,
        }
        t_num_line = (
            NumberLine(**t_num_line_kwargs).to_corner(UR, buff=0.5).shift(0.5 * DOWN)
        )
        [mob.scale_in_place(0.8) for mob in t_num_line.numbers]
        t_indicator = self.get_pivot_on_axis(t_num_line, 1, True)
        t_num_line.add(t_indicator)
        t_num_line.add(TexText("t").set_color(YELLOW_D).next_to(t_num_line))

        self.curve_func = (
            lambda x: 2 * x ** 2 - x ** 3 + (x + 1) * 0.5 * t_tracker.get_value()
        )
        self.l_limit_func = lambda t: (3 - t) / 4
        self.u_limit_func = lambda t: (7 + t) / 4

        self.setup_axes()
        curve = self.get_graph(
            self.curve_func,
            stroke_width=4,
        )
        graph = VGroup(self.axes, curve).to_edge(RIGHT, buff=0.1)
        curve_copy = curve.copy()
        [mob.scale_in_place(0.8) for mob in self.axes_label_mobs]
        fxt = (
            TexText("f(x,t)")
            .scale(0.8)
            .next_to(self.x_axis.number_to_point(3), 2.5 * DOWN)
            .set_style(fill_color=ORANGE)
        )

        self.play(ShowCreation(graph, lag_ratio=0.15), run_time=2)
        self.play(ShowCreation(t_num_line))
        self.wait(2)

        # show the function changing wrt t
        curve.add_updater(
            lambda c: c.become(self.get_graph(self.curve_func, stroke_width=4))
        )
        self.add(curve)
        self.play(
            t_tracker.set_value,
            3,
            t_indicator.shift,
            2 * RIGHT * t_num_line.unit_size,
            run_time=4,
            rate_func=there_and_back,
        )
        self.wait()

        # pivot points for limits of integration
        l_pivot = self.get_pivot_on_axis(self.x_axis, self.init_limits[0])
        r_pivot = self.get_pivot_on_axis(self.x_axis, self.init_limits[1])
        b_t = formula[0][5:9].copy().add_background_rectangle()
        a_t = formula[0][9:13].copy().add_background_rectangle()
        self.play(
            ApplyMethod(
                a_t.next_to, self.x_axis.number_to_point(self.init_limits[0]), 2 * DOWN
            ),
            ApplyMethod(
                b_t.next_to, self.x_axis.number_to_point(self.init_limits[1]), 2 * DOWN
            ),
            ShowCreation(VGroup(l_pivot, r_pivot)),
            lag_ratio=0,
            run_time=2,
        )
        self.wait(2)
        l_pivot.add(a_t)
        r_pivot.add(b_t)

        area = self.get_area_under_curve(curve, t_tracker.get_value())
        initial_area = area.copy()
        self.play(LaggedStartMap(ShowCreation, area, lag_ratio=0.3), run_time=2)
        self.wait(2)

        text1 = Text("Area under the curve")
        text2 = Text("changes with t")
        text2[0][-1].set_color(YELLOW_D)
        text = (
            VGroup(text1, text2)
            .arrange_submobjects(DOWN, aligned_edge=LEFT)
            .scale(0.8)
            .next_to(t_num_line, 2 * DOWN)
        )
        self.play(Write(text), run_time=2)
        self.wait(2)

        # show area changing with t
        area.add_updater(
            lambda a: a.become(self.get_area_under_curve(curve, t_tracker.get_value()))
        )
        self.add(area)
        self.play(
            t_tracker.set_value,
            3,
            ApplyMethod(t_indicator.shift, 2 * RIGHT * t_num_line.unit_size),
            ApplyMethod(
                l_pivot.shift,
                (self.init_limits[0] - self.l_limit_func(3))
                * LEFT
                * self.x_axis.unit_size,
            ),
            ApplyMethod(
                r_pivot.shift,
                (self.init_limits[1] - self.u_limit_func(3))
                * LEFT
                * self.x_axis.unit_size,
            ),
            run_time=4,
            rate_func=there_and_back,
        )
        self.play(FadeOut(text))
        self.wait(2)

        # brute-forcing and hardcoding ahead ;
        vert_change_in_area = self.get_vertical_change_in_area(
            initial_area, t_tracker.get_value()
        )
        left_rect = self.rectangles_due_to_varying_limits(
            initial_area, "lower", t_tracker.get_value()
        )
        right_rect = self.rectangles_due_to_varying_limits(
            initial_area, "upper", t_tracker.get_value()
        )

        del_t_equals = (
            TexText("\\triangle t=")
            .scale(0.6)
            .next_to(t_num_line.number_to_point(1), 2.5 * DOWN)
        )
        dt.next_to(del_t_equals)
        delta_t = VGroup(del_t_equals, dt)

        self.add(
            vert_change_in_area, left_rect, right_rect, curve_copy, t_indicator.copy()
        )
        area.clear_updaters()
        l_pivot.remove(a_t)
        r_pivot.remove(b_t)

        vert_change_in_area.add_updater(
            lambda a: a.become(
                self.get_vertical_change_in_area(initial_area, t_tracker.get_value())
            )
        )
        left_rect.add_updater(
            lambda a: a.become(
                self.rectangles_due_to_varying_limits(
                    initial_area, "lower", t_tracker.get_value()
                )
            )
        )
        right_rect.add_updater(
            lambda a: a.become(
                self.rectangles_due_to_varying_limits(
                    initial_area, "upper", t_tracker.get_value()
                )
            )
        )
        self.add(
            vert_change_in_area, left_rect, right_rect, l_pivot.copy(), r_pivot.copy()
        )
        self.play(
            t_tracker.set_value,
            2,
            ApplyMethod(t_indicator.shift, RIGHT * t_num_line.unit_size),
            ApplyMethod(
                l_pivot.shift,
                (self.init_limits[0] - self.l_limit_func(2))
                * LEFT
                * self.x_axis.unit_size,
            ),
            ApplyMethod(
                r_pivot.shift,
                (self.init_limits[1] - self.u_limit_func(2))
                * LEFT
                * self.x_axis.unit_size,
            ),
            run_time=2,
        )
        self.play(Write(delta_t))
        self.wait()

        l1, l2 = self.get_edge_lines(t_tracker.get_value(), curve)

        area_indicators = VGroup()
        for index, ar in enumerate([vert_change_in_area, left_rect, right_rect]):
            circ = Circle(radius=0.15, color=WHITE, stroke_width=2).move_to(
                ar.get_center_of_mass()
            )
            circ.add(
                Text(f"{index+1}", color=WHITE)
                .set_stroke(color=WHITE, width=1, opacity=1)
                .set_width(0.1)
                .move_to(circ.get_center())
            )
            area_indicators.add(circ)
        c4 = Circle(radius=0.15, color=WHITE, stroke_width=2).next_to(
            left_rect, 0.5 * UP
        )
        c4.add(
            Text(4)
            .set_stroke(color=WHITE, width=1, opacity=1)
            .set_width(0.1)
            .move_to(c4.get_center())
        )
        c5 = Circle(radius=0.15, color=WHITE, stroke_width=2).next_to(
            right_rect, 0.5 * UP
        )
        c5.add(
            Text(5)
            .set_stroke(color=WHITE, width=1, opacity=1)
            .set_width(0.1)
            .move_to(c5.get_center())
        )

        self.play(Write(area_indicators, lag_ratio=1), run_time=3)
        self.play(
            *[Write(mob) for mob in [c4, c5]],
            ShowCreation(l1),
            ShowCreation(l2),
            lag_ratio=1,
            run_time=2,
        )
        self.wait(2)

        area_indicators.add(c4, c5)

        change_in_area = (
            TexText("change \ in \ area \ =", "\\triangle A")
            .scale(0.75)
            .to_edge()
            .shift(2 * UP)
        )
        self.play(Write(change_in_area), run_time=2)
        self.wait(2)
        self.play(FadeOut(change_in_area))
        delta_a_equals = TexText("\\triangle A =").scale(0.75).to_edge().shift(2 * UP)
        dummy_area_inds = (
            VGroup(*[mob.copy() for mob in area_indicators])
            .arrange_submobjects(2 * RIGHT)
            .next_to(delta_a_equals)
        )
        plus_group = (
            VGroup(*[TexText("+").scale(0.8) for i in range(4)])
            .arrange_submobjects(2 * RIGHT)
            .next_to(dummy_area_inds[0], 0.7 * RIGHT)
        )
        self.play(Write(delta_a_equals))
        self.play(
            *[
                ApplyMethod(mob.copy().move_to, dummy_mob.get_center())
                for mob, dummy_mob in zip(area_indicators, dummy_area_inds)
            ],
            ShowCreation(plus_group, lag_ratio=1),
            run_time=2,
        )
        self.wait(3)

        curve_copy2 = self.get_graph(
            lambda x: 2 * x ** 2 - x ** 3 + (x + 1) * 0.5,
            stroke_width=4,
        )
        approx_area = self.get_riemann_rectangles(
            curve_copy2, 0.5, 2, dx=0.25, stroke_width=0.5
        )
        approx_diff_area = self.get_vertical_change_in_area(approx_area, 2)
        self.play(FadeOut(area), ShowCreation(approx_area), lag_ratio=1, run_time=2)
        self.play(
            FadeOut(vert_change_in_area),
            ShowCreation(approx_diff_area),
            lag_ratio=1,
            run_time=2,
        )
        self.wait(2)

        dx_tracker = ValueTracker(0.25)
        delta_x_brace = Brace(
            Line(self.x_axis.number_to_point(1.25), self.x_axis.number_to_point(1.5)),
            DOWN,
        )
        delta_x_text = (
            TexText("\\triangle x", "=")
            .scale(0.6)
            .next_to(delta_x_brace, DOWN + 0.2 * LEFT)
        )
        dx = (
            DecimalNumber(
                dx_tracker.get_value(), include_sign=False, num_decimal_places=2
            )
            .next_to(delta_x_text, buff=0.05)
            .scale(0.6)
        )
        delta_x = VGroup(delta_x_brace, delta_x_text, dx)
        delta_x_copy = delta_x_text[0].copy()

        delta_h_brace = Brace(approx_diff_area[1], LEFT, buff=0.1)
        delta_h_text = (
            TexText("\\frac{\partial f(x,t)}{\partial t} \ \\triangle t")
            .scale(0.6)
            .next_to(delta_h_brace, LEFT)
        )
        delta_h_text.add_background_rectangle(buff=0.1)
        delta_h = VGroup(delta_h_text, delta_h_brace)
        self.play(Write(delta_h), Write(delta_x))
        self.wait(2)

        area_indicators_copy = area_indicators.copy()
        for mob in area_indicators_copy:
            mob.add(TexText("\\approx").scale(0.75).next_to(mob))
        area_indicators_copy.arrange_submobjects(3 * DOWN).to_edge().shift(DOWN)
        dummy_form1 = (
            TexText(
                "\\sum ",
                "\\frac{\partial f(x,t)}{\partial t} \ \\triangle t \ ",
                "\\triangle x",
            )
            .scale(0.6)
            .next_to(area_indicators_copy[0])
        )
        self.play(
            Write(area_indicators_copy[0]),
            FadeOut(delta_h_text[0]),
            FadeOut(delta_h_brace),
            ApplyMethod(delta_h_text[1].move_to, dummy_form1[1]),
            ApplyMethod(delta_x_copy.move_to, dummy_form1[2]),
            Write(dummy_form1[0]),
            run_time=2,
        )
        self.wait(2)
        left_rect.clear_updaters()
        right_rect.clear_updaters()

        self.play(left_rect.shift, 3 * LEFT)
        l_rect_braces = VGroup(Brace(left_rect, LEFT), Brace(left_rect, DOWN))
        l_rect_width = (
            TexText("\\frac{\mathrm{d} \ a(t) }{\mathrm{d} t}\ \\triangle t")
            .scale(0.6)
            .next_to(l_rect_braces[1], DOWN)
        )
        l_rect_height = TexText("f(a(t),t)").scale(0.6).next_to(l_rect_braces[0], LEFT)
        l_rect_braces[0].add(l_rect_width, l_rect_height)
        self.play(Write(l_rect_braces), lag_ratio=0.15, run_time=2)
        self.wait(2)
        dummy_form2 = (
            VGroup(l_rect_width.copy(), l_rect_height.copy())
            .arrange_submobjects()
            .next_to(area_indicators_copy[1])
        )
        self.play(Write(area_indicators_copy[1]))
        self.play(
            l_rect_width.move_to,
            dummy_form2[0],
            l_rect_height.move_to,
            dummy_form2[1],
            left_rect.shift,
            3 * RIGHT,
            FadeOut(l_rect_braces[0][0]),
            FadeOut(l_rect_braces[1][0]),
        )
        self.wait(2)

        self.play(right_rect.shift, 6 * LEFT)
        r_rect_braces = VGroup(Brace(right_rect, LEFT), Brace(right_rect, DOWN))
        r_rect_width = (
            TexText("\\frac{\mathrm{d} \ b(t) }{\mathrm{d} t}\ \\triangle t")
            .scale(0.6)
            .next_to(r_rect_braces[1], DOWN)
        )
        r_rect_height = TexText("f(b(t),t)").scale(0.6).next_to(r_rect_braces[0], LEFT)
        r_rect_braces[0].add(r_rect_width, r_rect_height)
        self.play(Write(r_rect_braces), lag_ratio=0.15, run_time=2)
        self.wait(2)
        dummy_form3 = (
            VGroup(r_rect_width.copy(), r_rect_height.copy())
            .arrange_submobjects()
            .next_to(area_indicators_copy[2])
        )
        self.play(Write(area_indicators_copy[2]))
        self.play(
            r_rect_width.move_to,
            dummy_form3[0],
            r_rect_height.move_to,
            dummy_form3[1],
            right_rect.shift,
            6 * RIGHT,
            FadeOut(r_rect_braces[0][0]),
            FadeOut(r_rect_braces[1][0]),
        )
        self.wait(2)

        approach_zero = (
            VGroup(
                VGroup(
                    Text("Areas"),
                    area_indicators[-2].copy(),
                    Text("and"),
                    area_indicators[-1].copy(),
                    Text("approach zero"),
                ).arrange_submobjects(),
                VGroup(
                    Text("as"),
                    TexText("\\triangle t").scale(0.8),
                    Text("approaches zero."),
                ).arrange_submobjects(),
            )
            .arrange_submobjects(DOWN, aligned_edge=LEFT)
            .scale(0.8)
            .to_corner(DL)
            .shift(0.8 * UP)
            .add_background_rectangle(
                stroke_color=YELLOW_D,
                stroke_width=1.5,
                stroke_opacity=1,
                opacity=0,
                buff=0.2,
            )
        )
        self.play(Write(approach_zero), run_time=3)
        self.wait(2)

        self.play(
            FocusOn(area_indicators[-2]), FocusOn(area_indicators[-1]), lag_ratio=0
        )
        self.wait()

        approx_diff_area.add_updater(
            lambda a: a.become(
                self.get_vertical_change_in_area(approx_area, t_tracker.get_value())
            )
        )
        left_rect.add_updater(
            lambda a: a.become(
                self.rectangles_due_to_varying_limits(
                    initial_area, "lower", t_tracker.get_value()
                )
            )
        )
        right_rect.add_updater(
            lambda a: a.become(
                self.rectangles_due_to_varying_limits(
                    initial_area, "upper", t_tracker.get_value()
                )
            )
        )
        l_pivot.add_updater(
            lambda p: p.become(
                self.get_pivot_on_axis(
                    self.x_axis, self.l_limit_func(t_tracker.get_value())
                )
            )
        )
        r_pivot.add_updater(
            lambda p: p.become(
                self.get_pivot_on_axis(
                    self.x_axis, self.u_limit_func(t_tracker.get_value())
                )
            )
        )
        dt.add_updater(lambda t: t.set_value(t_tracker.get_value() - 1))
        l1.add_updater(
            lambda l: l.become(self.get_edge_lines(t_tracker.get_value(), curve)[0])
        )
        l2.add_updater(
            lambda l: l.become(self.get_edge_lines(t_tracker.get_value(), curve)[1])
        )
        self.add(approx_diff_area, left_rect, right_rect, l_pivot, r_pivot, dt)
        self.play(
            t_tracker.set_value,
            1.25,
            ApplyMethod(t_indicator.shift, 0.75 * LEFT * t_num_line.unit_size),
            FadeOut(area_indicators),
            run_time=4,
            rate_func=there_and_back,
        )
        self.add(area_indicators)
        self.wait(2)

        self.play(FadeOut(approach_zero))

        approx_form = (
            TexText(
                "\\triangle A",
                "\\approx",
                "\\sum \\frac{\partial f(x,t) }{\partial t}\\triangle t\\triangle x",
                "+",
                "\\frac{\mathrm{d} b(t)}{\mathrm{d}t}\\triangle t \ f(b(t),t)",
                "-",
                "\\frac{\mathrm{d}a(t)}{\mathrm{d}t}\\triangle t \ f(a(t),t)",
            )
            .scale(0.8)
            .next_to(area_indicators_copy[3], 0.8 * DOWN, aligned_edge=LEFT)
            .shift(0.2 * LEFT)
            .add_background_rectangle(buff=0.2)
        )
        self.play(Write(approx_form), run_time=2)
        self.wait(3)

        self.play(
            FadeOut(
                VGroup(
                    area_indicators_copy,
                    delta_h_text[1],
                    delta_x_copy,
                    l_rect_width,
                    l_rect_height,
                    r_rect_width,
                    r_rect_height,
                    dummy_form1[0],
                    approx_form[0],
                )
            ),
            approx_form.scale,
            0.7,
            {"about_edge": LEFT},
            approx_form.shift,
            3.5 * UP,
            lag_ratio=0,
        )
        # self.play(FadeIn(approx_form_rect))
        approx_form_rect = SurroundingRectangle(
            approx_form, color=YELLOW_D, stroke_width=1, buff=0.2
        )
        self.wait(2)

        vect1 = Vector(color=YELLOW_D).rotate(-PI / 2).scale(0.8)
        vect1_text = (
            VGroup(Text("divide by"), TexText("\\triangle t"))
            .scale(0.7)
            .arrange_submobjects()
        )
        ar1 = (
            VGroup(vect1, vect1_text)
            .arrange_submobjects()
            .next_to(approx_form_rect, DOWN)
        )
        self.play(Write(ar1), run_time=2)
        self.wait()

        approx_deriv = TexText(
            "\\frac{\\triangle A}{\\triangle t}\\approx \sum \\frac{\partial f(x,t) }{\partial t}\\triangle x \ + \\frac{\mathrm{d} b(t)}{\mathrm{d}t}\ f(b(t),t) \ - \\frac{\mathrm{d}a(t)}{\mathrm{d}t}\ f(a(t),t)"
        )
        approx_deriv.scale(0.6).next_to(
            approx_form_rect, 5 * DOWN, aligned_edge=LEFT
        ).shift(0.2 * RIGHT)
        self.play(Write(approx_deriv), run_time=3)
        self.wait(3)
        self.play(
            FadeOut(approx_form),
            FadeOut(ar1),
            FadeOut(approx_form_rect),
            ApplyMethod(
                approx_deriv.next_to, approx_form, 1 * DOWN, {"aligned_edge": LEFT}
            ),
        )
        self.wait(2)

        approach_0 = (
            VGroup(
                TexText(
                    "As\ ",
                    "\\triangle x \ and \  \\triangle t \ ",
                    "approach \ ",
                    "0,\ ",
                    "the\ ",
                    "ratio\ ",
                ),
                TexText(
                    "\\frac{\\triangle A}{\\triangle t}\ ",
                    "becomes\ ",
                    "more\ ",
                    "and\ ",
                    "more\ ",
                    "accurate\ ",
                ),
                # TexText("more\ ", "and\ ", "more\ ", "accurate\ ")
            )
            .scale(0.7)
            .arrange_submobjects(DOWN, aligned_edge=LEFT)
            .to_corner(DL, buff=1)
        )
        rect = SurroundingRectangle(
            approach_0, buff=0.2, color=YELLOW_D, stroke_width=1
        )
        self.play(Write(approach_0, run_time=4), ShowCreation(rect, run_time=1))
        self.wait(2)

        self.play(
            FadeOut(area_indicators), FadeOut(delta_x_brace), FocusOn(approx_area)
        )
        self.wait()

        curve.clear_updaters()
        approx_area.add_updater(
            lambda a: a.become(
                self.get_riemann_rectangles(
                    curve_copy2, 0.5, 2, dx=dx_tracker.get_value(), stroke_width=0.5
                )
            )
        )
        approx_diff_area.add_updater(
            lambda a: a.become(self.get_vertical_change_in_area(approx_area, 2))
        )
        dx.add_updater(lambda x: x.set_value(dx_tracker.get_value()))
        self.add(approx_area, approx_diff_area, dx)
        self.play(dx_tracker.set_value, 0.01, run_time=6, rate_func=linear)
        self.wait(2)

        curve.add_updater(
            lambda c: c.become(self.get_graph(self.curve_func, stroke_width=4))
        )
        approx_diff_area.add_updater(
            lambda a: a.become(
                self.get_vertical_change_in_area(approx_area, t_tracker.get_value())
            )
        )
        l1.add_updater(
            lambda l: l.become(self.get_edge_lines(t_tracker.get_value(), curve)[0])
        )
        l2.add_updater(
            lambda l: l.become(self.get_edge_lines(t_tracker.get_value(), curve)[1])
        )
        self.add(curve, approx_diff_area, l1, l2)
        self.play(
            t_tracker.set_value,
            1.2,
            t_indicator.shift,
            -0.8 * RIGHT * t_num_line.unit_size,
            run_time=4,
        )
        self.wait(2)

        self.play(FadeOut(approach_0), FadeOut(rect))
        self.wait()

        approx_deriv_rect = SurroundingRectangle(
            approx_deriv, buff=0.1, color=YELLOW_D, stroke_width=1
        )
        self.play(ShowCreation(approx_deriv_rect))
        self.wait()
        ar2 = Vector(color=YELLOW_D).rotate(-PI / 2)
        ar2_text = (
            VGroup(
                TexText("\\triangle x\\rightarrow 0"),
                TexText("\\triangle t\\rightarrow 0"),
            )
            .scale(0.6)
            .arrange_submobjects(DOWN)
            .next_to(ar2, buff=0.2)
        )
        arrow = (
            VGroup(ar2, ar2_text).arrange_submobjects().next_to(approx_deriv_rect, DOWN)
        )

        self.play(Write(arrow), run_time=2)
        self.wait()

        final_form = (
            TexText(
                "\\frac{\mathrm{d} A}{\mathrm{d} t}",
                " = \ \int_{a(t)}^{b(t)} \\frac{\partial f(x,t) }{\partial t}dt \ + \ \\frac{\mathrm{d}b(t) }{\mathrm{d} t}\ f(b(t),t) \ - \ \\frac{\mathrm{d} a(t)}{\mathrm{d} t}\ f(a(t),t)",
            )
            .scale(0.6)
            .to_corner(DL)
        )
        self.play(FadeIn(final_form), run_time=3, lag_ratio=0.15)
        self.wait(2)

        self.play(final_form[1].copy().next_to, formula[0], run_time=2)
        self.wait(2)

        leibnitz_form = VGroup(formula[0], final_form[1].copy().next_to(formula[0]))

        self.add(leibnitz_form)
        self.play(
            *[FadeOut(mob) for mob in [*self.mobjects] if mob is not leibnitz_form],
            leibnitz_form.move_to,
            ORIGIN,
            leibnitz_form.scale,
            1.25,
        )
        self.wait(3)

    def get_pivot_on_axis(self, axis, number, invert=False, scale_fact=0.12, **kwargs):
        pivot = (
            Triangle(**kwargs).scale(scale_fact).move_to(axis.number_to_point(number))
        )

        if invert:
            pivot.rotate_in_place(PI)
            pivot.shift((pivot.get_top()[1] - pivot.get_center()[1]) * UP)
        else:
            pivot.shift((pivot.get_top()[1] - pivot.get_center()[1]) * DOWN)

        return pivot

    def get_area_under_curve(self, curve, t):
        area = self.get_area(
            curve, t_min=self.l_limit_func(t), t_max=self.u_limit_func(t)
        )
        return area

    def get_vertical_change_in_area(self, area, t_val):
        width = area[0].get_width()
        change_in_area = VGroup()
        func = lambda x, t: 2 * x ** 2 - x ** 3 + (x + 1) * 0.5 * t

        for index, x in enumerate(
            np.arange(*self.init_limits, width / self.x_axis.unit_size)
        ):
            height = (func(x, t_val) - func(x, 1)) * self.y_axis.unit_size
            rectangle = Rectangle(
                width=width,
                height=height,
                fill_opacity=0.8,
                stroke_width=0.5,
                stroke_color=BLACK,
            )
            rectangle.next_to(area[index], UP, buff=0)
            change_in_area.add(rectangle)

        change_in_area.set_submobject_colors_by_gradient(*self.vert_area_cols)
        return change_in_area

    def rectangles_due_to_varying_limits(self, initial_area, limit, t_val):
        curve_func = lambda x, t: 2 * x ** 2 - x ** 3 + (x + 1) * 0.5 * t
        if limit == "lower":
            width = (
                self.l_limit_func(t_val) - self.l_limit_func(1)
            ) * self.x_axis.unit_size
            height = curve_func(self.init_limits[0], 1) * self.y_axis.unit_size
            rect = Rectangle(
                width=width, height=height, **self.left_rect_kwargs
            ).next_to(initial_area[0], LEFT, buff=0)

        else:
            width = (
                self.u_limit_func(t_val) - self.u_limit_func(1)
            ) * self.x_axis.unit_size
            height = curve_func(self.init_limits[1], 1) * self.y_axis.unit_size
            rect = Rectangle(
                width=width, height=height, **self.right_rect_kwargs
            ).next_to(initial_area[-1], buff=0)

        return rect

    def get_edge_lines(self, t_val, curve):
        l1 = Line(
            self.x_axis.number_to_point(self.l_limit_func(t_val)),
            self.input_to_graph_point(self.l_limit_func(t_val), curve),
            stroke_width=1,
        )
        l2 = Line(
            self.x_axis.number_to_point(self.u_limit_func(t_val)),
            self.input_to_graph_point(self.u_limit_func(t_val), curve),
            stroke_width=1,
        )
        return [l1, l2]


class PrevVid(Scene):
    def construct(self):

        prev_vid = VGroup(
            Text("Please watch my previous video on the"),
            Text("leibnitz integral rule for constant limits,"),
            Text("to better understand what is happening here."),
        ).arrange_submobjects(DOWN, aligned_edge=LEFT)
        prev_vid[1].set_color(YELLOW_D)

        self.wait()
        self.play(FadeIn(prev_vid), lag_ratio=0.3, run_time=4, rate_func=linear)
        self.wait(2)
        self.play(
            *[FadeOut(mob) for mob in [*self.mobjects] if mob is not self.board],
            lag_ratio=0.15,
        )

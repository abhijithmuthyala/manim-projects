from manimlib import *
from manimlib.once_useful_constructs.graph_scene import GraphScene


def number_to_proportion(num, graph):
    return (num - graph.x_min) / (graph.x_max - graph.x_min)
    # This throws an attribute error to you.
    # set the attributes,
    #       graph.x_min = x_min
    #       graph.x_max = x_max
    # in the get_graph() method of GraphScene.


def get_area(axes, graph, x_min, x_max, **area_style):
    l_prop = number_to_proportion(x_min, graph)
    r_prop = number_to_proportion(x_max, graph)
    area = Polygon(
        axes.x_axis.number_to_point(x_min),
        *[graph.point_from_proportion(p) for p in np.linspace(l_prop, r_prop, 20)],
        axes.x_axis.number_to_point(x_max),
    ).set_style(**dict(stroke_width=0, fill_opacity=0.2, **area_style))
    return area


class IntroScene(GraphScene):  # Do this in a video editor??
    CONFIG = dict(
        x_axis_width=5.5, x_min=0, x_max=8.5, y_max=7, y_min=0, y_axis_height=4.5
    )

    def setup(
        self,
    ):  # In manim, setup method will be executed before the construct method
        # self.camera.background_image = "FadedBoard2.png"
        # self.camera.init_background()
        self.fx = lambda x: 0.05 * x ** 3 - 0.5 * x ** 2 + x + 5
        super().setup()

    def construct(self):

        self.axes.to_edge(buff=0.2)
        exam_texts = ["JEE", "BITSAT", "..."]
        exams = (
            VGroup(*[Text(exam, font="Comic Sans MS") for exam in exam_texts])
            .arrange(DOWN, aligned_edge=LEFT, buff=1)
            .set_style(fill_opacity=0, stroke_width=5, stroke_color=TEAL_E)
            .scale(1.25)
        )

        self.wait(3)
        self.play(
            LaggedStart(
                *[FadeInFromPoint(mob, UP) for mob in exams],
                lag_ratio=0.9,
                run_time=4,
            )
        )
        self.wait(3)
        self.play(FadeOut(exams))
        self.wait()

        properties = (
            VGroup(
                Text("Properties Of Definite Integrals :", font="Comic Sans MS").scale(
                    0.65
                ),
                TexText("\\int_{a}^{b}f(x)dx = -\\int_{b}^{a}f(x)dx"),
                TexText("\\int_{a}^{b}k\ f(x)dx = k\\int_{a}^{b}f(x)dx"),
                TexText("\\int_{a}^{b}f(x)dx", "=", "\\int_{a}^{b}f(a+b-x)dx"),
                TexText(
                    "\\int_{a}^{b}[f(x)+g(x)]dx = \\int_{a}^{b}f(x)dx + \\int_{a}^{b}g(x)dx"
                ),
                Text("..."),
            )
            .scale(0.75)
            .arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        )
        properties[0].set_style(fill_opacity=0, stroke_width=2, stroke_color=YELLOW_D)
        king_rule = properties[3].copy()
        king_rule_text = (
            Text("King Rule :", font="Comic Sans MS", color=BLUE_E)
            .scale(0.6)
            .next_to(king_rule, LEFT)
        )

        self.play(
            LaggedStart(
                *[FadeInFromPoint(prop, UP) for prop in properties],
                lag_ratio=0.3,
                run_time=3,
            )
        )
        self.add(king_rule)
        self.wait(3)
        self.play(Write(king_rule_text))
        self.wait()
        self.play(FadeOut(properties), lag_ratio=0.3)
        self.play(VGroup(king_rule, king_rule_text).to_corner, UL)
        self.wait()
        self.play(Indicate(king_rule[0]), run_time=2)
        self.wait(2)
        self.play(Indicate(king_rule[-1]), run_time=2)
        self.wait(8)

        proof = (
            VGroup(
                TexText("u=a+b-x"),
                TexText(
                    "\\int_{a}^{b}f(x)dx = \\int_{b}^{a}f(a+b-u)(-du) = \\int_{a}^{b}f(a+b-x)dx"
                ),
            )
            .arrange(DOWN, buff=0.75, aligned_edge=LEFT)
            .next_to(king_rule_text, 4 * DOWN, aligned_edge=LEFT)
        )

        self.play(Write(proof[0]), run_time=2)
        self.play(FadeIn(proof[1]), run_time=4, lag_ratio=0.15)
        self.wait(2)
        self.play(FadeOut(VGroup(*self.mobjects)), run_time=2, lag_ratio=0.3)
        self.show_axes(animate=False)
        self.wait()

        fx_graph = self.get_graph(self.fx, MAROON_D, -0.5, 7.5)
        fx_graph_text = (
            TexText("f(x)", color=MAROON_D).next_to(fx_graph, UP).scale(0.75)
        )
        fx_area = get_area(self.axes, fx_graph, 1, 7, fill_color=MAROON_D)
        fx_integral = (
            TexText("\\int_{1}^{7}", "f(x)", "dx").move_to(fx_area).scale(0.75)
        )
        fx_integral.set_color_by_tex("f(x)", MAROON_D)

        graph1 = VGroup(self.axes, fx_graph, fx_area)
        graph2 = VGroup(*[mob.deepcopy() for mob in graph1]).to_edge(RIGHT)

        self.play(Write(fx_graph), FadeIn(fx_area))
        self.play(Write(fx_graph_text), Write(fx_integral))
        self.wait()
        self.play(TransformFromCopy(graph1, graph2, path_arc=PI / 3), run_time=2)
        self.wait()

        gx_graph = (
            graph2[1]
            .copy()
            .flip(
                about_point=graph2[1].point_from_proportion(
                    number_to_proportion(4, graph2[1])
                )
            )
            .set_color(YELLOW_D)
        )
        gx_graph_text = (
            TexText("f(1+7-x)", color=YELLOW_D).next_to(graph2[1], UP).scale(0.75)
        )
        gx_area = graph2[-1].copy().flip().set_fill(color=YELLOW_D)
        gx_integral = (
            TexText("\\int_{1}^{7}", "f(1+7-x)", "dx").move_to(gx_area).scale(0.75)
        )
        gx_integral.set_color_by_tex("f(1+7-x)", YELLOW_D)

        flip_axis = DashedLine(
            graph2[0].x_axis.number_to_point(4),
            graph2[1].point_from_proportion(number_to_proportion(4, graph2[1])),
        ).scale(1.75)
        flip_axis.add(Text("Flip axis").scale(0.75).next_to(flip_axis.get_start()))

        self.play(Write(flip_axis))
        self.play(Transform(graph2[1:], VGroup(gx_graph, gx_area)), run_time=2)
        self.play(Write(gx_graph_text), Write(gx_integral))
        self.wait()
        self.play(
            VGroup(fx_integral, gx_integral).become,
            VGroup(fx_integral.copy(), TexText("="), gx_integral.copy())
            .arrange()
            .to_edge(UP),
            run_time=2,
        )
        self.wait(5)


class KingRule(GraphScene):
    CONFIG = dict(x_max=9, x_axis_width=8)

    def setup(self):
        # self.camera.background_image = "FadedBoard2.png"
        # self.camera.init_background()
        self.fx = lambda x: 0.05 * x ** 3 - 0.5 * x ** 2 + x + 7
        super().setup()
        self.axes.to_edge(DOWN + LEFT, buff=1)
        self.add(self.axes)
        self.wait()

    def construct(self):

        a, b = ValueTracker(1), ValueTracker(7)
        a_text = always_redraw(
            lambda: Text("a").next_to(
                self.x_axis.number_to_point(a.get_value()), UP + LEFT, 0.1
            )
        )
        b_text = always_redraw(
            lambda: Text("b").next_to(
                self.x_axis.number_to_point(b.get_value()), UP + RIGHT, 0.1
            )
        )

        fx_graph = self.get_graph(self.fx, MAROON_D, -1, 8)
        fx_text = TexText("f(x)", color=MAROON_D).next_to(
            fx_graph.get_start(), LEFT, 0.1
        )
        fx_area = always_redraw(
            lambda: get_area(
                self.axes, fx_graph, a.get_value(), b.get_value(), fill_color=MAROON_D
            )
        )

        fx_integral = (
            TexText("\\int_{a}^{b}", "f(x)", "dx").move_to(fx_area).scale(0.75)
        )
        fx_integral.set_color_by_tex("f(x)", MAROON_D)

        flip_axis = always_redraw(
            lambda: DashedLine(
                self.x_axis.number_to_point(0.5 * (a.get_value() + b.get_value())),
                self.input_to_graph_point(
                    0.5 * (a.get_value() + b.get_value()), fx_graph
                ),
            ).scale(1.5)
        )
        avg = always_redraw(
            lambda: TexText("\\frac{a+b}{2}").scale(0.5).next_to(flip_axis, DOWN, 0.1)
        )

        self.play(Write(fx_text), ShowCreation(fx_graph))
        self.wait(2)
        self.play(
            FadeIn(fx_area), Write(VGroup(a_text, b_text)), lag_ratio=1, run_time=2
        )
        self.wait(2)
        self.play(Write(fx_integral))
        self.wait(2)
        self.play(fx_integral.center, fx_integral.to_edge, UP)
        self.wait()
        self.play(Write(flip_axis), Write(avg))
        self.wait(7)

        gx_graph = always_redraw(
            lambda: fx_graph.copy()
            .flip(
                about_point=self.input_to_graph_point(
                    0.5 * (a.get_value() + b.get_value()), fx_graph
                )
            )
            .set_color(YELLOW_D)
        )
        gx_area = always_redraw(
            lambda: fx_area.deepcopy()
            .flip(
                about_point=self.input_to_graph_point(
                    0.5 * (a.get_value() + b.get_value()), fx_graph
                )
            )
            .set_style(
                **dict(
                    fx_area.get_style(),
                    **{"fill_color": YELLOW_D},
                )
            )
        )
        gx_text = TexText("g(x)", color=YELLOW_D).next_to(
            gx_graph.get_start(), DOWN, 0.1
        )
        gx_integral = (
            TexText("\\int_{a}^{b}", "g(x)", "dx").move_to(gx_area).scale(0.75)
        )
        gx_integral.set_color_by_tex("g(x)", YELLOW_D)

        self.play(
            TransformFromCopy(fx_graph, gx_graph),
            TransformFromCopy(fx_area, gx_area),
            run_time=2,
            lag_ratio=0,
        )
        self.wait(7)
        self.play(ApplyWave(gx_area, amplitude=0.5), run_time=2)
        self.wait()
        self.play(ApplyWave(fx_area, amplitude=0.5), run_time=2)
        self.wait(13)
        self.play(Write(gx_text))
        self.wait(4)
        self.play(Write(gx_integral), run_time=2)
        self.wait()
        equals = TexText("=").scale(0.6).next_to(fx_integral, LEFT)
        self.play(gx_integral.next_to, equals, LEFT, Write(equals), run_time=2)
        self.wait(6)

        x = ValueTracker(2)
        vert_line_to_g = always_redraw(
            lambda: DashedLine(
                self.x_axis.number_to_point(x.get_value()),
                gx_graph.point_from_proportion(
                    number_to_proportion(8 - x.get_value(), gx_graph)
                ),
                color=YELLOW_D,
            )
        )
        vert_line_to_f = always_redraw(
            lambda: DashedLine(
                self.x_axis.number_to_point(8 - x.get_value()),
                self.input_to_graph_point(8 - x.get_value(), fx_graph),
                color=MAROON_D,
            )
        )
        fg_line = always_redraw(
            lambda: DashedLine(
                vert_line_to_g.get_end(), vert_line_to_f.get_end()
            ).set_color_by_gradient(YELLOW_D, MAROON_D)
        )
        x_text = always_redraw(
            lambda: VGroup(
                Dot(self.x_axis.number_to_point(x.get_value())).scale(0.7),
                TexText("x")
                .scale(0.7)
                .next_to(self.x_axis.number_to_point(x.get_value()), DOWN + LEFT, 0.1),
            ).set_color(YELLOW_D)
        )
        x_prime_text = always_redraw(
            lambda: VGroup(
                Dot(self.x_axis.number_to_point(8 - x.get_value())).scale(0.7),
                TexText("{x}'")
                .scale(0.7)
                .next_to(
                    self.x_axis.number_to_point(8 - x.get_value()), DOWN + RIGHT, 0.1
                ),
            ).set_color(MAROON_D)
        )

        self.wait(6)
        self.play(FocusOn(x_text), FocusOn(x_prime_text))
        self.play(
            Write(x_text),
            Write(x_prime_text),
        )
        self.wait()
        self.play(ShowCreation(VGroup(vert_line_to_g, vert_line_to_f)))
        self.play(ShowCreation(fg_line))
        self.wait(4)

        dist_arrow = (
            Vector(LEFT * 2 * self.x_axis.unit_size)
            .shift(self.x_axis.number_to_point(4))
            .shift(2 * UP)
        )
        self.play(GrowFromPoint(dist_arrow, dist_arrow.get_start()))
        self.play(
            Rotating(
                dist_arrow, radians=PI, axis=IN, about_point=dist_arrow.get_start()
            ),
            run_time=2,
        )
        self.wait()
        self.play(FadeOut(dist_arrow))
        self.wait(3)

        input_avg = TexText("\\frac{x + {x}'}{2}").scale(0.5)
        input_avg[0][0].set_color(YELLOW_D)
        input_avg[0][2:4].set_color(MAROON_D)
        avg_copy = avg.copy()
        average = (
            VGroup(input_avg, TexText("=").scale(0.5), avg_copy)
            .scale(2)
            .arrange()
            .to_edge(RIGHT)
        )
        relation = (
            VGroup(
                average[0][0][2:4].copy(),
                average[1].copy(),
                average[-1][0][:-2].copy(),
                TexText("-"),
                average[0][0][0].copy(),
            )
            .arrange()
            .next_to(average, DOWN, 1, aligned_edge=LEFT)
        )

        self.play(Write(average), run_time=3)
        self.wait(2)
        self.play(FadeInFromPoint(relation, UP))
        self.wait()
        self.play(relation.shift, 2 * UP, FadeOut(average))
        self.wait()
        self.play(x.set_value, 8, rate_func=there_and_back, run_time=8)
        self.wait(3)

        g_as_f = TexText("g(x)", "=", "f", "(a+b-", "x", ")").next_to(
            relation, DOWN, 1, aligned_edge=RIGHT
        )
        g_as_f[0].set_color(YELLOW_D)
        g_as_f.set_color_by_tex("f", MAROON_D)
        g_as_f.set_color_by_tex("x", YELLOW_D)

        self.play(Write(g_as_f), run_time=3)
        self.wait()

        abx_integral = (
            VGroup(
                TexText("="),
                TexText("\\int_{a} ^ {b}"),
                VGroup(g_as_f[2:].copy(), TexText("dx")).arrange(buff=0.1),
            )
            .scale(0.75)
            .arrange()
            .next_to(fx_integral)
        )

        self.play(FocusOn(abx_integral))
        self.play(Write(abx_integral), run_time=3)
        self.wait(3)


# shouldn't really be done with manim, prefer powerpoint and desmos instead
class ExampleScene(Scene):
    def construct(self):
        #         self.camera.background_image = "FadedBoard2.png"
        #         self.camera.init_background()

        question = (
            VGroup(
                Text("Q. Evaluate "),
                TexText(
                    "\\int_{-\\frac{\pi}{2}}^{\ \\frac{\pi}{2}}",
                    "\\frac{sin^{2}x}{1+2^{x}}",
                    "dx",
                ),
                Text("  (JEE Mains - 2018)"),
            )
            .scale(0.65)
            .arrange()
            .to_corner(UL)
            .set_color(YELLOW_D)
        )

        i1 = (
            VGroup(
                Text("I ="),
                question[1].copy().set_color(WHITE),
            )
            .arrange()
            .next_to(question, DOWN, 0.6, aligned_edge=LEFT)
        )
        eq1 = TexText("\\rightarrow 1").next_to(i1, buff=1)

        fx_exp = (
            VGroup(TexText("f(x) ="), i1[1].copy())
            .arrange()
            .next_to(i1, DOWN, aligned_edge=LEFT)
        )

        king_rule = (
            VGroup(
                Text("King rule :", color=MAROON_D),
                TexText("\\int_{a}^{b}f(x)dx", "=", "\\int_{a}^{b}f(a+b-x)dx").scale(
                    0.65
                ),
            )
            .arrange()
            .next_to(eq1, buff=1)
        )

        i_int1 = (
            VGroup(
                i1[0].copy(),
                TexText(
                    "\\int_{-\\frac{\pi}{2}}^{\ \\frac{\pi}{2}}",
                    "\\frac{(sin(-\\frac{\pi}{2}+\\frac{\pi}{2}-x))^{2}}{1+2^{-\\frac{\pi}{2}+\\frac{\pi}{2}-x}}dx",
                ).scale(0.65),
            )
            .arrange()
            .next_to(i1, 2 * DOWN, aligned_edge=LEFT)
        )
        i_int2 = (
            VGroup(
                TexText("="),
                TexText(
                    "\\int_{-\\frac{\pi}{2}} ^ {\ \\frac{\pi}{2}}",
                    "\\frac{2^{x}sin ^ {2}x}{1+2 ^ {x}}dx",
                ).scale(0.65),
            )
            .arrange()
            .next_to(i_int1[0][0][1], 3 * DOWN, aligned_edge=LEFT)
        )

        self.add(question)
        self.wait(6)
        self.play(Indicate(question[1][1], color=GREEN_D, scale_factor=1.5))
        self.wait()
        self.play(Indicate(question[1][0], color=GREEN_D, scale_factor=1.5))
        self.wait(2)
        self.play(Write(i1[0]))
        self.wait()
        self.play(TransformFromCopy(question[1], i1[1]), run_time=2)
        self.wait(3)
        self.play(FadeIn(king_rule), lag_ratio=0.3)
        self.wait(3)
        self.play(Write(i_int1), run_time=3)
        self.wait()
        self.play(Write(i_int2), run_time=2)
        self.wait()
        self.play(
            FadeOut(i_int1[1]),
            FadeOut(i_int2[0]),
            i_int2[1].next_to,
            i_int1[0],
        )
        self.wait(7)
        self.play(Indicate(i_int2[1][1][:2], scale_factor=1.5))
        self.wait(2)

        # i2 = VGroup(i_int1[0],i_int2[1])
        eq2 = TexText("\\rightarrow 2").next_to(i_int2[1])
        eq2.shift((eq1.get_left()[0] - eq2.get_left()[0]) * RIGHT)

        self.play(ShowCreation(VGroup(eq1, eq2)))
        self.wait()

        two_i = (
            VGroup(
                Text("2.I", " ="),
                i1[1].copy(),
                TexText("+"),
                i_int2[1].copy(),
            )
            .arrange()
            .next_to(i_int1, 2 * DOWN, aligned_edge=LEFT)
        )

        clubbed_2i = (
            VGroup(
                TexText("="),
                TexText(
                    "\\int_{-\\frac{\pi}{2}} ^ {\ \\frac{\pi}{2}}",
                    "[\ ",
                    "\\frac{sin ^ {2}x}{1+2 ^ {x}}",
                    "+",
                    "\\frac{2^{x}sin ^ {2}x}{1+2 ^ {x}}\ ]",
                    "dx",
                ).scale(0.65),
            )
            .arrange()
            .next_to(two_i)
        )
        simplified_2i = (
            VGroup(
                TexText("="),
                TexText(
                    "\\int_{-\\frac{\pi}{2}} ^ {\ \\frac{\pi}{2}}", "\\sin^{2}x}", "dx"
                ).scale(0.65),
            )
            .arrange()
            .next_to(clubbed_2i, 1.5 * DOWN, aligned_edge=LEFT)
        )

        self.play(Write(two_i), run_time=3)
        self.wait(2)
        self.play(Indicate(two_i[1][0][:8]), Indicate(two_i[-1][0][:8]), lag_ratio=0)
        self.wait(2)
        self.play(Write(clubbed_2i), run_time=2)
        self.wait()

        self.play(Write(simplified_2i), run_time=2)
        self.wait(2)

        # EndScene
        self.wait()
        self.play(Indicate(two_i[1:]))
        self.wait()
        self.play(Indicate(clubbed_2i[1]))
        self.wait()
        self.play(Indicate(simplified_2i[1]))
        self.wait()

        self.play(FadeOut(clubbed_2i), simplified_2i.next_to, two_i)
        self.wait()
        self.play(
            FadeOut(two_i[1:]),
            FadeOut(two_i[0][1]),
            simplified_2i.next_to,
            two_i[0][0],
            run_time=2,
        )
        self.wait()

        two_i_val = TexText("=", "\\frac{\pi}{2}").scale(0.65).next_to(simplified_2i)
        i_val = (
            VGroup(TexText("I ="), TexText("\\frac{\pi}{4}").scale(0.65))
            .arrange()
            .next_to(two_i, 1.5 * DOWN, aligned_edge=LEFT)
        )
        i_val.add_background_rectangle(
            stroke_color=YELLOW_D, stroke_width=2, stroke_opacity=1, buff=0.25
        )

        self.play(Write(two_i_val))
        self.wait(3)
        self.play(Write(i_val))
        self.wait()

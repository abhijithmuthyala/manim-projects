from math import radians as rad

from manimlib import *
from manimlib.once_useful_constructs.graph_scene import GraphScene

from pragyaan.manim_demos.surface_demo import plane_config, z_axis_config

from .functions import *

X_COLOR = MAROON_D
Y_COLOR = GREEN_D
T_COLOR = TEAL_E
CURVE_COLOR = GOLD_E
SCALAR_FIELD_COLOR = PINK


class ScalarLineIntegralScene(ThreeDScene):
    CONFIG = {
        "plane_config": plane_config,
        "z_axis_config": z_axis_config,
        "curve_t_func": None,
        "curve_kwargs": {"color": GOLD_E},
        "scalar_field": None,
        "t_min": -3,
        "t_max": 3,
        "t_axis_kwargs": {},
        "riemann_gradient": (BLUE_E, GREEN_E),
        "area_style": {"stroke_width": 0, "fill_opacity": 0.75},
        "n_rects_for_area": 2000,  # yup you saw it right! Trust the shaders.
        "origin": ORIGIN,
    }

    def setup(self):
        self.setup_axes()
        self.curve = get_parametric_curve(
            self.axes,
            self.curve_t_func,
            (self.t_min, self.t_max, 0.01),
            **self.curve_kwargs
        )
        self.area = self.get_area(self.n_rects_for_area, **self.area_style)
        self.t_axis = NumberLine([self.t_min, self.t_max], **self.t_axis_kwargs)

    def setup_axes(
        self,
    ):  # bcz the ThreeDAxes's z_axis tip looks weird look for whatever reason
        plane = NumberPlane(**self.plane_config).shift(self.origin)
        z_axis = NumberLine(**self.z_axis_config).shift(plane.c2p(0, 0))
        z_axis.rotate(PI / 2, axis=z_axis.get_unit_vector(), about_point=z_axis.n2p(0))
        z_axis.rotate(
            PI / 2, axis=-plane.y_axis.get_unit_vector(), about_point=z_axis.n2p(0)
        )
        if hasattr(z_axis, "numbers"):
            [num.rotate(PI / 2, UP) for num in z_axis.numbers]
        self.plane = plane
        self.z_axis = z_axis
        self.axes = self.axes.axes = VGroup(*self.plane.axes, self.z_axis)

    def get_area(self, n_rects=None, **style):
        n_rects = n_rects or self.n_rects_for_area
        style = dict(self.area_style, **style)
        return self.get_riemann_sum(n_rects, **style)

    def get_riemann_sum(self, n_rects, gradient=None, **style):
        gradient = gradient or self.riemann_gradient
        style = dict(self.area_style, **style)
        rects = VGroup()
        t_range, dt = np.linspace(self.t_min, self.t_max, n_rects, False, True)

        for t in t_range:
            dl = self.c2p(self.curve_t_func(t))
            dr = self.c2p(self.curve_t_func(t + dt))
            ul = self.c2p([*dl[:2], self.scalar_field(*dl[:2])])
            ur = ul + (dr - dl)
            rects.add(Polygon(ur, ul, dl, dr))

        rects.set_color_by_gradient(*gradient)
        return rects.set_style(**style)

    def get_rescaled_riemann_sum(self, riemann_sum):
        # scalar_field = scalar_field or self.scalar_field
        rescaled_rects = VGroup()
        t_unit = self.t_axis.get_unit_size()
        z_unit = self.z_axis.get_unit_size()
        t_range, dt = np.linspace(self.t_min, self.t_max, len(riemann_sum), False, True)

        for rect, t in zip(riemann_sum, t_range):
            height = self.scalar_field(*self.curve_t_func(t)[:2])
            width = get_norm(self.curve_t_func(t + dt) - self.curve_t_func(t))
            rescaled_rects.add(
                Rectangle(dt * t_unit, (height * width / dt) * z_unit).set_style(
                    **rect.get_style()
                )
            )

        rescaled_rects.arrange(buff=0, aligned_edge=DOWN)
        rescaled_rects.next_to(
            self.t_axis.n2p(self.t_min),
            UP,
            0,
            aligned_edge=LEFT,
        )
        return rescaled_rects

    def c2p(self, coords):
        return c2p(self.axes, coords)

    def update_riemann_rectangles(
        self,
        rects,
        step,
        n_iters,
        wait_time=0.5,
        style={},
        dt_brace=None,
        t_samples=None,
        **transform_kwargs
    ):
        # style is absolutely unnecessary here, but manim decides not to work without it
        # Transform(rects, self.get_riemann_sum(n_rects, **rect.get_style())) should have
        # worked just as fine. Also, brace and t_sample updaters shouldn't live here;
        # just couldn't figure out a better way
        for _ in range(n_iters):
            n_rects = len(rects) + step
            anims = [
                Transform(
                    rects, self.get_riemann_sum(n_rects, **style), **transform_kwargs
                )
            ]
            if dt_brace is not None:
                anims.append(
                    ApplyMethod(
                        dt_brace.stretch_to_fit_width,
                        (self.t_max - self.t_min) * self.t_axis.unit_size / n_rects,
                        {"about_point": self.t_axis.pfp(0)},
                        run_time=transform_kwargs.get("run_time") or 1,
                    )
                )
            if t_samples is not None:
                self.t_samples_kwargs["radius"] *= 0.9
                upd_samples = self.get_samples_on_t_axis(
                    n_rects + 1, **self.t_samples_kwargs
                )
                anims.append(
                    Transform(
                        t_samples,
                        upd_samples,
                        run_time=transform_kwargs.get("run_time") or 1,
                    )
                )
            self.play(*anims)
            self.wait(wait_time)

    def raise_riemann_rectangles(
        self, rectangles, added_anims=None, **rect_anim_kwargs
    ):
        for rect in rectangles:
            rect.save_state()
            rect.stretch(0.01, 2, about_point=self.plane.c2p(0, 0))

        anims = LaggedStart(*map(Restore, rectangles), **rect_anim_kwargs)
        if added_anims is None:
            added_anims = []
        self.play(anims, *added_anims)

    def get_sample_input_spheres(self, x_range, y_range, **sphere_kwargs):
        return get_sample_input_spheres(x_range, y_range, self.axes, **sphere_kwargs)

    def raise_sample_spheres_to_output(
        self, input_spheres, scalar_field=None, added_anims=None, **kwargs
    ):
        scalar_field = scalar_field or self.scalar_field
        for sphere in input_spheres:
            # using these x,y attrs is not a good idea; use p2n instead; realized later
            x, y = sphere.x, sphere.y
            sphere.target = self.c2p((x, y, scalar_field(x, y)))
        anims = LaggedStart(
            *[ApplyMethod(s.move_to, s.target) for s in input_spheres],
            lag_ratio=kwargs.get("lag_ratio") or 0
        )
        if added_anims is None:
            added_anims = []
        self.play(anims, *added_anims, run_time=kwargs.get("run_time"))

    def get_parametric_surface(self, scalar_field=None, **kwargs):
        scalar_field = scalar_field or self.scalar_field

        def uv_func(u, v):
            return self.c2p((u, v, scalar_field(u, v)))

        return ParametricSurface(uv_func, **kwargs)

    def get_flattened_area(self, aligned_edge):
        return get_flattened_area(aligned_edge, self.area, self.axes[0])

    def get_flattened_curve(self, aligned_edge):
        return get_flattened_curve(aligned_edge, self.curve)

    def get_samples_on_t_axis(
        self, n_samples, t_min=None, t_max=None, t_axis=None, **kwargs
    ):
        """
        n_samples is 1 more than n_rects for riemann_sum
        """
        t_axis = t_axis or self.t_axis
        t_min = t_min or self.t_min
        t_max = t_max or self.t_max
        return SGroup(
            *[
                Sphere(**kwargs).move_to(t_axis.n2p(t))
                for t in np.linspace(t_min, t_max, n_samples)
            ]
        )

    def show_parametric_function_map(
        self, t_samples, t_axis=None, curve=None, **kwargs
    ):
        curve = curve or self.curve
        t_axis = t_axis or self.t_axis
        t_min = t_axis.p2n(t_samples[0].get_center())
        t_max = t_axis.p2n(t_samples[-1].get_center())
        t_range = t_max - t_min

        anims = []
        for dot in t_samples:
            # using pfp here makes it independent of the axes the curve is attached to. Good!
            target = curve.pfp((t_axis.p2n(dot.get_center()) - t_min) / t_range)
            anims.append(ApplyMethod(dot.move_to, target))
        self.play(*anims, **kwargs)


# develop this further independent of GraphScene, preferably using Axes
class SingleIntegralScene(GraphScene):
    CONFIG = {
        "function": lambda x: 2 * np.sin(x) + 2,
        "graph_limits": (0, 6),
        "integral_limits": (1, 5),
        "graph_color": GOLD_E,
        "graph_kwargs": {"stroke_width": 4, "step_size": 0.01},
        "gradient": (BLUE_D, GREEN_D),
        "n_rects_for_area": 200,
        "riemann_rects_style": {
            "stroke_width": 0.2,
            "stroke_color": BLACK,
            "fill_opacity": 0.8,
        },
    }

    def setup(self):
        super().setup()
        self.graph = self.get_graph(
            self.function, self.graph_color, *self.graph_limits, **self.graph_kwargs
        )
        self.area = self.get_riemann_rectangles(self.n_rects_for_area)

    # bcz the one in GraphScene doesn't work for non integer limits
    def get_riemann_rectangles(
        self,
        n_rects,
        x_limits=None,
        function=None,
        gradient=None,
        show_signed_area=True,
        **style
    ):
        x_limits = x_limits or self.integral_limits
        function = function or self.function
        gradient = gradient or self.gradient
        style = dict(self.riemann_rects_style, **style)

        x_range, dx = np.linspace(*x_limits, n_rects, False, True)
        colors = color_gradient(gradient, len(x_range))
        rects = VGroup()
        rects.n_rects = n_rects

        for i, x in enumerate(x_range):
            dl = self.x_axis.n2p(x)
            dr = self.x_axis.n2p(x + dx)
            ul = self.coords_to_point(x, function(x))
            ur = ul + (dr - dl)
            color = colors[i]
            if ul[1] < self.coords_to_point(0, 0)[1] and show_signed_area:
                color = invert_color(color)
            rects.add(Polygon(ur, ul, dl, dr, color=color))
        return rects.set_style(**style)

    def update_riemann_rectangles(
        self, rects, step, n_iters, wait_time=0.5, *added_anims, **transform_kwargs
    ):
        for _ in range(n_iters):
            n_rects = len(rects) + step
            self.play(
                Transform(
                    rects, self.get_riemann_rectangles(n_rects), **transform_kwargs
                ),
                *added_anims
            )
            self.wait(wait_time)

    def raise_riemann_rectangles(
        self, rectangles, added_anims=None, **rect_anim_kwargs
    ):
        for rect in rectangles:
            rect.save_state()
            rect.stretch(0.000001, 1, about_point=self.coords_to_point(0, 0))

        anims = LaggedStartMap(Restore, rectangles, **rect_anim_kwargs)
        if added_anims is None:
            added_anims = []
        self.play(AnimationGroup(anims, *added_anims))


class OpeningSceneSingleIntegrals(SingleIntegralScene):
    CONFIG = {
        "function": lambda x: 4 * np.sin(0.5 * x),
        "graph_limits": (-2, 10),
        "integral_limits": (0.01, 9),  # dk why it behaves weird when lower limit is 0
        "y_min": -4,
        "y_max": 4,
        "y_axis_height": 5,
        "x_min": -2,
        "graph_origin": 4 * LEFT + DOWN,
        "axes_color": WHITE,
    }

    def construct(self):
        title = Text("Single Integrals").scale(1.5).to_edge(UP)
        title.set_color_by_gradient(*[r.get_color() for r in self.area])
        title.add(Underline(title))
        riemann_rects = self.get_riemann_rectangles(8)

        self.add(title)
        self.wait()
        self.play(ShowCreation(self.axes), run_time=2)
        self.wait()
        self.play(ShowCreation(self.graph))
        self.wait()
        self.play(ShowCreation(self.area), run_time=4)
        self.wait(2)

        [rect.save_state() for rect in self.area]
        self.play(
            self.area.stretch,
            0.00000001,
            1,
            {
                "about_point": self.coords_to_point(0, 0)
            },  # can be any point on the x axis
            run_time=2,
            lag_ratio=0,
        )
        self.wait()
        self.raise_riemann_rectangles(riemann_rects, run_time=2, lag_ratio=0.25)
        self.wait(2)
        self.update_riemann_rectangles(
            riemann_rects, 30, 6, lag_ratio=0.15, run_time=0.75
        )
        self.wait(2)

        ip_space = Rectangle(
            self.area.get_width(),
            0.25,
            fill_opacity=0.4,
            fill_color=YELLOW,
            stroke_width=0,
        )
        ip_space.next_to(self.area.get_left(), buff=0)
        ip_space.save_state()
        ip_space.stretch(0.0000001, 0, about_point=ip_space.get_left())

        self.play(
            AnimationGroup(
                ApplyMethod(riemann_rects.set_opacity, 0.4, run_time=0.4),
                Restore(ip_space, run_time=3),
                lag_ratio=1,
            )
        )
        self.wait(2)


class OpeningSceneLineIntegrals(ScalarLineIntegralScene):
    CONFIG = {
        "curve_t_func": lambda t: np.array([t, 2 * np.sin(t), 0]),
        "scalar_field": lambda x, y: np.cos(x) * np.sin(y) + 2,
    }

    def construct(self):
        frame = self.camera.frame
        ip_space_rect = ScreenRectangle(
            height=8, stroke_width=0, fill_opacity=0.4, fill_color=YELLOW
        )
        color_map = {"x": X_COLOR, "y": Y_COLOR, "f": SCALAR_FIELD_COLOR}
        f_xy = TexText(
            "f(x,y)", "=", "cos(x)sin(y)+2", tex_to_color_map=color_map
        ).add_background_rectangle()
        f_xy.to_corner(UR, buff=0.1)
        f_xy.fix_in_frame()

        self.plane.x_axis.set_stroke(X_COLOR, 3, recurse=False)
        self.plane.y_axis.set_stroke(Y_COLOR, 3, recurse=False)

        self.add(self.plane)
        self.wait()
        self.play(
            Succession(
                GrowFromCenter(ip_space_rect, run_time=3),
                FadeOut(ip_space_rect, run_time=0.2),
            )
        )
        self.wait()
        self.play(
            Write(f_xy, run_time=2),
            ApplyMethod(frame.set_euler_angles, rad(45), rad(60), run_time=8),
            ShowCreation(self.curve, run_time=8),
            ShowCreation(self.area.set_opacity(0.35), run_time=8),
        )
        self.wait()
        self.clear()

        # three_d_sample_curve = get_parametric_curve(
        #     self.axes,
        #     lambda t: 2 * np.array([np.cos(t), np.sin(t), 0.1 * t]),
        #     t_range=[-2 * TAU, 2 * TAU, 0.01],
        #     color=GOLD_E,
        # )

        # frame.add_updater(lambda f, dt: f.increment_theta(dt * 0.02))
        # self.add(frame)

        # self.play(
        #     AnimationGroup(
        #         FadeIn(self.axes, lag_ratio=0, run_time=0.5),
        #         ShowCreation(three_d_sample_curve, run_time=2),
        #         lag_ratio=1,
        #     )
        # )
        # self.wait(2)
        # self.clear()

        integrals = Group(*list(map(ImageMobject, ["one_d.png", "two_d.png"])))
        for img in integrals:
            img.add(SurroundingRectangle(img, buff=0, color=WHITE))
        integrals.arrange(buff=0.5).set_width(FRAME_WIDTH - 1).to_edge(DOWN, buff=2)

        frame.clear_updaters()
        frame.set_euler_angles(0, 0)
        frame.save_state()
        frame.move_to(integrals[0]).match_width(integrals[0]).match_height(integrals[0])

        self.play(FadeIn(integrals[0]))
        self.wait(2)
        self.play(Restore(frame, run_time=2))
        self.play(LaggedStartMap(FadeIn, integrals[1:], UP, run_time=2, lag_ratio=0.25))
        self.wait()

        line_integrals_text = Text("Line Integrals").scale(2).to_edge(UP)
        line_integrals_text.set_color_by_gradient(*self.riemann_gradient)
        line_integrals_text.add(Underline(line_integrals_text))
        self.play(Write(line_integrals_text), run_time=2)
        self.wait(6)
        self.play(
            frame.move_to,
            integrals[1],
            frame.match_width,
            integrals[1],
            frame.match_height,
            integrals[1],
            run_time=4,
        )
        self.wait(3)


class ScalarFieldAndTheGoal(ScalarLineIntegralScene):
    CONFIG = {
        "curve_t_func": lambda t: np.array([t, 2 * np.sin(t), 0]),
        "scalar_field": lambda x, y: np.cos(x) * np.sin(y) + 2,
    }

    def construct(self):
        frame = self.camera.frame
        frame.save_state()

        title = Text("Scalar Fields", color=SCALAR_FIELD_COLOR).scale(1.5).to_edge(UP)
        title.add_background_rectangle(buff=0.25)
        color_map = {"x": X_COLOR, "y": Y_COLOR, "f": SCALAR_FIELD_COLOR}
        f_xy = TexText("f(x,y)", "=", "cos(x)sin(y)+2", tex_to_color_map=color_map)
        f_xy.set_width(4).add_background_rectangle().to_corner(UR)

        self.plane.x_axis.set_stroke(X_COLOR, 3, recurse=False)
        self.plane.y_axis.set_stroke(Y_COLOR, 3, recurse=False)

        self.add(self.plane, title, f_xy)
        self.wait()
        self.show_scalar_field()

        f_xy.fix_in_frame()
        sample_spheres = self.get_sample_input_spheres(
            (-3, 4, 1), (-3, 4, 1), radius=0.08, color=SCALAR_FIELD_COLOR
        )
        surface = self.get_parametric_surface(
            color=SCALAR_FIELD_COLOR, u_range=[-3, 3], v_range=[-3, 3]
        )
        mesh = SurfaceMesh(surface, color=SCALAR_FIELD_COLOR)
        surface.set_shadow(0.4).set_gloss(0.3)
        self.play(
            FadeOut(title), ShowCreation(sample_spheres, lag_ratio=0.2), run_time=2
        )
        self.wait()
        self.raise_sample_spheres_to_output(
            sample_spheres,
            added_anims=[
                ApplyMethod(frame.set_euler_angles, rad(-20), rad(60)),
                ApplyMethod(self.plane.set_opacity, 0.25),
            ],
            run_time=5,
            lag_ratio=0.1,
        )
        self.wait()
        self.play(ShowCreation(surface.set_opacity(0.5)), run_time=2)
        self.wait()
        self.play(FadeOut(sample_spheres), Restore(frame), run_time=2)

        self.play(
            ApplyMethod(frame.set_euler_angles, rad(45), rad(60)),
            ShowCreation(self.curve),
            ShowCreation(self.area.set_opacity(0.25)),
            run_time=10,
        )
        self.wait(2)

        # take a moment to digest the figure
        frame.add_updater(lambda f, dt: f.increment_theta(dt * 0.05))
        self.add(frame)
        self.wait(8)

        frame.clear_updaters()
        self.play(
            frame.set_euler_angles,
            rad(0),
            rad(70),
            self.area.set_opacity,
            0.8,
            FadeOut(surface),
            run_time=2,
        )
        self.wait()

        self.area.save_state()
        self.curve.save_state()

        flat_area = self.get_flattened_area(5 * LEFT)
        flat_curve = self.get_flattened_curve(5 * LEFT)

        self.play(
            Transform(self.area, flat_area),
            Transform(self.curve, flat_curve),
            run_time=5,
        )
        self.wait(3)
        self.play(Restore(self.area), Restore(self.curve))
        self.play(Transform(self.area, flat_area), Transform(self.curve, flat_curve))
        self.wait(2)

    def show_scalar_field(self):
        x_axis, y_axis = self.axes[:2]
        path = self.plane.get_parametric_curve(
            lambda t: [4 * np.cos(t), 1.75 * np.sin(t), 0],
            t_range=[PI / 4, TAU + PI / 4],
        )
        tracer = Sphere(radius=0.1).move_to(path.point_from_proportion(0))

        x_line = always_redraw(
            lambda: get_x_line_to_point(y_axis, tracer.get_center(), color=X_COLOR)
        )
        y_line = always_redraw(
            lambda: get_y_line_to_point(x_axis, tracer.get_center(), color=Y_COLOR)
        )

        def get_fxy():
            x = x_axis.p2n(tracer.get_center())
            y = y_axis.p2n(tracer.get_center())
            fxy = DecimalNumber(self.scalar_field(x, y), color=SCALAR_FIELD_COLOR)
            fxy.add_background_rectangle()
            return fxy.next_to(tracer, np.array([x, y, 0]), buff=0.02)

        fxy = always_redraw(lambda: get_fxy())

        self.play(
            AnimationGroup(
                ShowCreation(VGroup(x_line, y_line)),
                GrowFromCenter(tracer),
                run_time=0.5,
                lag_ratio=1,
            )
        )
        self.play(Write(fxy), run_time=0.5)
        self.wait()
        self.play(MoveAlongPath(tracer, path, run_time=8, rate_func=double_smooth)),
        self.play(FadeOut(Group(tracer, x_line, y_line, fxy)))
        self.wait()


class ApproximatingCurvedArea(ScalarLineIntegralScene):
    CONFIG = {
        "curve_t_func": lambda t: np.array([t, 2 * np.sin(t), 0]),
        "scalar_field": lambda x, y: np.cos(x) * np.sin(y) + 2,
        "t_axis_kwargs": {
            "include_numbers": True,
            "width": 6,
            "color": T_COLOR,
            "decimal_number_config": {"height": 0.18},
            "line_to_number_direction": UP,
        },
        "t_samples_kwargs": {"radius": 0.025, "color": WHITE},
    }

    def setup(self):
        super().setup()
        self.f_xy = TexText(
            "f(x,y)",
            "=",
            "cos(x)sin(y)+2",
            tex_to_color_map={
                "x": X_COLOR,
                "y": Y_COLOR,
                "f": SCALAR_FIELD_COLOR,
                "r": CURVE_COLOR,
            },
        )

        r_t = TexText("r(t)", "=", "[", "t", ",", " 2sin(t)]")
        r_t[0][0].set_color(CURVE_COLOR)
        r_t[0][2].set_color(T_COLOR)
        r_t[3].set_color(X_COLOR)
        r_t[-1][:-1].set_color(Y_COLOR)
        r_t[-1][-3].set_color(T_COLOR)
        self.r_t = r_t

        delta_s = TexText(
            "\\triangle s", "=", "\sqrt{\\triangle x^{2} + \\triangle y^{2}}"
        )
        delta_s[0].set_color(self.riemann_gradient[0])
        delta_s[2][2:5].set_color(X_COLOR)
        delta_s[2][6:9].set_color(Y_COLOR)
        self.delta_s = delta_s

        f_rt = TexText(
            "f(r(t))",
            "=",
            "cos(t)sin(2sin(t))",
            "+",
            "2",
        )
        f_rt[0][0].set_color(SCALAR_FIELD_COLOR)
        f_rt[0][2].set_color(CURVE_COLOR)
        f_rt[0][4].set_color(T_COLOR)
        f_rt[2][4].set_color(X_COLOR)
        f_rt[2][10:14].set_color(Y_COLOR)
        f_rt[2][15].set_color(T_COLOR)
        self.f_rt = f_rt

        approx_area_tex = TexText("\sum f(r(t))\\triangle s")
        approx_area_tex[0][1].set_color(SCALAR_FIELD_COLOR)
        approx_area_tex[0][3].set_color(CURVE_COLOR)
        approx_area_tex[0][5].set_color(T_COLOR)
        approx_area_tex[0][8:].set_color(self.riemann_gradient[0])
        self.approx_area_tex = approx_area_tex

        integral_c_tex = TexText("\int_{C}f(r(t))ds")
        integral_c_tex[0][9:].set_color(self.riemann_gradient[0])
        integral_c_tex[0][1].set_color(CURVE_COLOR)
        integral_c_tex[0][2].set_color(SCALAR_FIELD_COLOR)
        integral_c_tex[0][4].set_color(CURVE_COLOR)
        integral_c_tex[0][6].set_color(T_COLOR)
        self.integral_c_tex = integral_c_tex

        integral_gt = TexText("\int_{-3}^{3}g(t)dt").match_height(integral_c_tex)
        t_indices = [
            1,
            2,
            3,
            6,
            8,
            9,
        ]  # bcz tex_to_color_map weirdly generates different tex
        [integral_gt[0][i].set_color(T_COLOR) for i in t_indices]
        self.integral_gt = integral_gt

        self.plane.x_axis.set_stroke(X_COLOR, 3, recurse=False)
        self.plane.y_axis.set_stroke(Y_COLOR, 3, recurse=False)
        self.t_axis.add(
            TexText("t", color=T_COLOR).next_to(self.t_axis.pfp(1), buff=0.1)
        )

    def construct(self):
        frame = self.camera.frame
        self.t_axis.add_background_rectangle(buff=0.1).to_corner(UL)

        f_xy = self.f_xy
        f_xy.set_width(4).add_background_rectangle().to_corner(UR)

        r_t = self.r_t
        r_t.add_background_rectangle()
        r_t.match_height(f_xy).next_to(f_xy, DOWN, aligned_edge=LEFT)

        self.add(self.plane, f_xy)
        self.wait()
        self.trace_curve()
        self.wait(2)

        self.t_axis.fix_in_frame()
        self.plane.save_state()
        f_xy.fix_in_frame()
        r_t.fix_in_frame()

        self.raise_riemann_rectangles(
            self.area,
            [
                ApplyMethod(frame.set_euler_angles, rad(0), rad(70), run_time=3),
                ApplyMethod(self.plane.set_opacity, 0.2, run_time=3),
            ],
            run_time=3,
            lag_ratio=0,
        )
        self.wait()

        rs_style = dict(stroke_width=0.05, fill_opacity=0.9, stroke_color=BLACK)
        riemann_sum = self.get_riemann_sum(6, **rs_style)
        self.raise_riemann_rectangles(
            riemann_sum,
            [ApplyMethod(self.area.set_opacity, 0.1)],
            run_time=1.5,
            lag_ratio=0.1,
        )
        self.wait(2)

        # bases of rects
        self.play(
            FadeOut(self.area),
            self.plane.restore,
            frame.to_default_state,
            riemann_sum.stretch,
            0.01,
            2,
            {"about_point": self.plane.c2p(0, 0)},
            riemann_sum.set_stroke,
            {"width": 4},
            riemann_sum.set_color_by_gradient,
            *self.riemann_gradient,
            run_time=2
        )
        self.wait()

        t_samples = self.get_samples_on_t_axis(
            len(riemann_sum) + 1, radius=0.05, color=WHITE
        )
        t_samples.fix_in_frame()
        t_samples_copy = t_samples.copy()
        t_samples_copy.save_state()
        dt_brace = Brace(t_samples[:2], buff=0.05)
        dt_brace.fix_in_frame()
        dt_label = TexText("\\triangle t", color=T_COLOR).scale(0.65)
        dt_label.add_background_rectangle(opacity=0.4)
        dt_label.match_height(self.r_t).next_to(dt_brace, DOWN, aligned_edge=LEFT)
        dt_label.fix_in_frame()

        self.play(Indicate(self.t_axis, scale_factor=1.1, color=T_COLOR))
        self.play(ShowCreation(t_samples), ShowCreation(t_samples_copy))
        self.wait(0.5)
        self.play(Write(dt_brace), Write(dt_label))
        self.wait()
        self.show_parametric_function_map(t_samples_copy, run_time=2)
        self.wait(2)

        delta_s = self.delta_s
        delta_s.scale(0.8).to_edge().shift(0.5 * UP)
        delta_s.add_background_rectangle()

        delta_x_line = Line(
            t_samples_copy[1].get_center(),
            [t_samples_copy[0].get_x(), t_samples_copy[1].get_y(), 0],
            color=X_COLOR,
        )
        delta_y_line = Line(t_samples_copy[0], delta_x_line.get_end(), color=Y_COLOR)

        delta_s_label = TexText("\\triangle s", color=riemann_sum[0].get_color())
        delta_s_label.add_background_rectangle().scale(0.65).next_to(
            riemann_sum[0].get_nadir(), UR, 0.1
        )
        delta_x_label = TexText(
            "\\triangle x", color=X_COLOR
        ).add_background_rectangle()
        delta_x_label.scale(0.65).next_to(delta_x_line, DOWN, buff=0.1)
        delta_y_label = TexText(
            "\\triangle y", color=Y_COLOR
        ).add_background_rectangle()
        delta_y_label.scale(0.65).next_to(delta_y_line, LEFT, buff=0.1)

        self.play(Indicate(riemann_sum[0]))
        self.wait(0.5)
        self.play(Write(delta_s_label), run_time=0.5)
        self.wait(2)
        self.play(ShowCreation(delta_x_line), GrowFromCenter(delta_x_label))
        self.play(ShowCreation(delta_y_line), GrowFromCenter(delta_y_label))
        self.wait(2)
        self.play(Write(delta_s, run_time=4))
        self.wait(0.75)
        self.play(
            *map(
                FadeOut,
                [
                    delta_x_label,
                    delta_y_label,
                    delta_s_label,
                    delta_x_line,
                    delta_y_line,
                ],
            ),
            delta_s.match_width,
            r_t,
            delta_s.next_to,
            r_t,
            DOWN,
            {"aligned_edge": LEFT},
            run_time=0.75
        )  # n28
        self.wait()

        f_rt = self.f_rt
        f_rt.match_height(f_xy).next_to(dt_label, 3 * RIGHT)
        f_rt.fix_in_frame()

        # crank up riemann_rects
        delta_s.fix_in_frame()
        self.area.set_opacity(0.1)
        frame.generate_target()
        frame.target.set_euler_angles(0, rad(70))
        frame.target.shift(2 * UP + 2.5 * RIGHT)
        self.raise_riemann_rectangles(
            self.area,
            [
                LaggedStartMap(Restore, riemann_sum, lag_ratio=0.1, run_time=3),
                MoveToTarget(frame, run_time=3),
                ApplyMethod(self.plane.set_opacity, 0.2, run_time=3),
                FadeOut(t_samples_copy),
            ],
            run_time=0.5,
        )
        self.wait(4)
        self.play(Write(f_rt), run_time=4)
        self.wait(3)

        approx_area_tex = self.approx_area_tex
        approx_area_tex.add_background_rectangle()
        approx_area_tex.fix_in_frame()
        approx_area_tex.next_to(delta_s, 2 * DOWN, aligned_edge=LEFT)

        integral_c_tex = self.integral_c_tex
        # integral_c_tex.add_background_rectangle()
        integral_c_tex.fix_in_frame()
        integral_c_tex.move_to(approx_area_tex)

        self.play(Write(approx_area_tex), run_time=4)
        self.wait(3)

        self.update_riemann_rectangles(
            riemann_sum,
            20,
            6,
            run_time=0.75,
            style=rs_style,
            dt_brace=dt_brace,
            t_samples=t_samples,
        )
        self.wait(2)
        self.play(
            AnimationGroup(
                FadeOutToPoint(approx_area_tex, DOWN),
                FadeIn(integral_c_tex, 0.5 * UP),
                lag_ratio=0.1,
                run_time=1.5,
            )
        )
        self.wait(3)
        self.play(Indicate(integral_c_tex[0][1], scale_factor=1.35))
        self.wait(2)
        self.play(Indicate(self.curve, scale_factor=1.1), run_time=1.5)  # n53

        # transition scene
        integral_c_tex.save_state()
        self.wait(4)
        self.play(
            Succession(
                Indicate(integral_c_tex[0]),
                ApplyMethod(integral_c_tex.to_corner, DR, 1.5),
                run_time=2,
            )
        )
        self.wait()

        question_bubble = ThoughtBubble(height=3, width=5, fill_opacity=0.2)
        # question_bubble.next_to(integral_c_tex, DL, 0.2)
        question_bubble.pin_to(integral_c_tex)
        question_bubble.write("How to evaluate this?")
        question_bubble.fix_in_frame()
        question_bubble.content.fix_in_frame()

        self.play(
            GrowFromPoint(question_bubble, question_bubble.get_corner(DR)),
            run_time=0.75,
        )
        self.play(Write(question_bubble.content), run_time=2)
        self.wait(2)
        self.play(Indicate(integral_c_tex[0][2:9]))
        self.wait()
        self.play(Indicate(integral_c_tex[0][-2:]))
        self.wait(8)

        idea = Text("May be by leveraging ", "t", "?", tex_to_color_map={"t": T_COLOR})
        question_bubble.position_mobject_inside(idea)
        idea.fix_in_frame()

        self.play(
            AnimationGroup(
                FadeOutToPoint(question_bubble.content),
                Write(idea),
                lag_ratio=0.2,
                run_time=3,
            )
        )
        self.wait(3)  # n65

        # promising reasons
        t_range_line = Line(self.t_axis.pfp(0), self.t_axis.pfp(1))
        t_range_line.fix_in_frame()
        self.play(
            AnimationGroup(
                ShowCreationThenFadeOut(t_range_line, run_time=4),
                FadeOut(VGroup(question_bubble, idea), run_time=0.5),
                Restore(integral_c_tex),
                lag_ratio=1,
            )
        )
        self.wait()

        self.play(
            LaggedStart(
                *[
                    ApplyMethod(
                        r.stretch,
                        0.9,
                        2,
                        {"about_point": r.get_nadir()},
                        rate_func=there_and_back,
                    )
                    for r in riemann_sum
                ],
                lag_ratio=0.025,
                run_time=2
            )
        )
        self.wait()
        self.play(Indicate(integral_c_tex[0][2:9]))
        self.wait(2)  # n 71

        # the equivalence and rescaling
        integral_gt = self.integral_gt
        # integral_gt.add_background_rectangle()
        integral_gt.fix_in_frame()
        integral_gt.to_edge(RIGHT)
        equals = TexText("=").next_to(integral_gt, LEFT, 0.2)
        equals.fix_in_frame()

        self.wait(3)
        self.play(
            AnimationGroup(
                ApplyMethod(integral_c_tex.next_to, equals, LEFT, 0.2),
                Write(equals),
                lag_ratio=1,
                run_time=2,
            )
        )
        self.wait()
        self.play(Write(integral_gt), run_time=2)
        self.wait(5)

        surr_rect = SurroundingRectangle(VGroup(integral_c_tex, equals, integral_gt))
        surr_rect.fix_in_frame()
        self.play(ShowCreationThenFadeOut(surr_rect), run_time=2)  # n77
        self.wait(5)

    def trace_curve(self):
        t_dot = SmallDot(self.t_axis.pfp(0))
        curve_dot = SmallDot(self.curve.pfp(0))
        curve_dot.add_updater(lambda d: d.move_to(self.curve.points[-1]))

        self.play(Write(self.t_axis), FadeIn(t_dot, 5), run_time=2)
        self.wait()
        self.add(curve_dot)
        self.play(
            AnimationGroup(
                Write(self.r_t, run_time=4),
                ShowCreation(self.curve, run_time=8),
                ApplyMethod(t_dot.move_to, self.t_axis.pfp(1), run_time=8),
            )
        )
        self.play(FadeOut(t_dot), FadeOut(curve_dot), run_time=0.2)

    def get_dt_brace_label(self, t_samples):
        dt_brace = BraceLabel(t_samples[:2], "\\triangle t", DOWN, buff=0.1)
        dt_brace.label.set_color(T_COLOR)
        dt_brace.label.add_background_rectangle(opacity=0.4)
        dt_brace.label.match_height(self.r_t)
        dt_brace.fix_in_frame()
        return dt_brace


class RescalingExample(Scene):
    def construct(self):
        w_tracker = ValueTracker(4)
        h_tracker = ValueTracker(3)
        rescaled_width = 2
        x_unit = 0.75
        y_unit = 0.6

        rect_style = dict(fill_color=GOLD_E, stroke_color=GOLD_E, fill_opacity=0.4)
        rect = Rectangle(
            w_tracker.get_value() * x_unit, h_tracker.get_value() * y_unit, **rect_style
        )
        rescaled_rect = Rectangle(rescaled_width * x_unit, 6 * y_unit, **rect_style)

        a_brace = Brace(rect)
        b_brace = Brace(rect, RIGHT)
        a_label = Text("a", color=BLUE_E).next_to(a_brace, DOWN, 0.15)
        b_label = Text("b", color=SCALAR_FIELD_COLOR).next_to(b_brace, RIGHT, 0.15)
        rect_group = VGroup(rect, a_brace, a_label, b_brace, b_label)

        w_brace = Brace(rescaled_rect)
        w_label = (
            Text("w", color=T_COLOR).next_to(w_brace, DOWN, 0.15).set_color(T_COLOR)
        )
        h_brace = Brace(rescaled_rect, LEFT)
        h_label = Text("h").next_to(h_brace, LEFT, 0.15)
        rescaled_rect_group = VGroup(rescaled_rect, w_brace, w_label, h_brace, h_label)

        VGroup(rect_group, rescaled_rect_group).arrange(
            buff=5, aligned_edge=DOWN
        ).to_edge(DOWN, buff=0.75)

        for r in [rect, rescaled_rect]:
            r.save_state()
            r.stretch(0.00001, 1, about_point=rect.get_top())

        self.wait()
        self.play(Restore(rect, run_time=1.5))
        self.play(
            Write(a_brace),
            GrowFromCenter(a_label),
            Write(b_brace),
            GrowFromCenter(b_label),
            run_time=0.75,
        )
        self.wait()

        question = Text("Construct a new rectangle with same area, but with a width w")
        question[0][-1].set_color(T_COLOR)
        question.to_edge(UP)

        self.play(FadeIn(question, lag_ratio=0.25, run_time=3))
        self.wait()
        self.play(Restore(rescaled_rect))
        self.play(
            Write(VGroup(h_brace, w_brace)),
            GrowFromCenter(h_label),
            GrowFromCenter(w_label),
        )
        self.wait()
        self.play(Indicate(h_label, scale_factor=1.4))
        self.wait()

        equate_area_text = (
            Text("a", ".", "b", " = ", "w", ".", "h").shift(0.5 * UP).scale(1.25)
        )
        equate_area_text[0].set_color(BLUE_E)
        equate_area_text[2].set_color(SCALAR_FIELD_COLOR)
        equate_area_text[4].set_color(T_COLOR)

        h_text = (
            TexText("h", " = ", "\\frac{a.b}{w}")
            .scale(1.25)
            .next_to(equate_area_text, UP, aligned_edge=LEFT)
        )
        h_text[2][0].set_color(BLUE_E)
        h_text[2][2].set_color(SCALAR_FIELD_COLOR)
        h_text[2][4].set_color(T_COLOR)

        self.play(Indicate(question[0][26:34]))
        self.wait(2)
        self.play(
            AnimationGroup(
                TransformFromCopy(a_label, equate_area_text[0]),
                TransformFromCopy(b_label, equate_area_text[2]),
                Write(equate_area_text[3]),
                TransformFromCopy(w_label, equate_area_text[-3]),
                TransformFromCopy(h_label, equate_area_text[-1]),
                lag_ratio=1,
                run_time=2.5,
            )
        )
        self.wait(3)
        self.play(Write(h_text), run_time=2)
        self.wait(0.5)

        def rect_upd(rect):
            rect.stretch_to_fit_width(
                w_tracker.get_value() * x_unit, about_point=rect.get_left()
            )
            rect.stretch_to_fit_height(
                h_tracker.get_value() * y_unit, about_point=rect.get_bottom()
            )

        def rescaled_rect_upd(rect):
            h = h_tracker.get_value() * y_unit * w_tracker.get_value() / rescaled_width
            rect.stretch_to_fit_height(h, about_point=rect.get_bottom())

        rect.add_updater(rect_upd)
        a_brace.add_updater(
            lambda b: b.stretch_to_fit_width(
                rect.get_width(), about_point=rect.get_left()
            ).next_to(rect, DOWN)
        )
        a_label.add_updater(lambda a: a.next_to(a_brace, DOWN, 0.15))
        b_brace.add_updater(
            lambda b: b.stretch_to_fit_height(
                rect.get_height(), about_point=rect.get_bottom()
            ).next_to(rect)
        )
        b_label.add_updater(lambda b: b.next_to(b_brace, RIGHT, 0.15))
        self.add(rect, a_brace, a_label, b_brace, b_label)

        rescaled_rect.add_updater(rescaled_rect_upd)
        h_brace.add_updater(
            lambda h: h.stretch_to_fit_height(
                rescaled_rect.get_height(), about_point=rescaled_rect.get_bottom()
            ).next_to(rescaled_rect, LEFT)
        )
        h_label.add_updater(lambda l: l.next_to(h_brace, -RIGHT, 0.15))
        self.add(rescaled_rect, h_brace, h_label)

        self.play(w_tracker.set_value, 7, h_tracker.set_value, 2.5, run_time=6)
        self.wait(0.25)
        self.play(w_tracker.set_value, 1, h_tracker.set_value, 5, run_time=6)
        self.wait(2)


class TheYurekaScene(ApproximatingCurvedArea):
    def setup(self):
        super().setup()
        self.area.set_opacity(0.1)
        for mob in [
            self.f_xy,
            self.r_t,
            self.f_rt,
            self.delta_s,
            self.integral_c_tex,
            self.integral_gt,
            self.t_axis,
        ]:
            mob.add_background_rectangle(opacity=0.5)
            mob.fix_in_frame()
        self.f_xy.set_width(4)
        self.r_t.match_height(self.f_xy)
        self.delta_s.match_height(self.f_xy)
        self.f_rt.scale(0.65)
        VGroup(self.f_xy, self.delta_s).arrange(
            DOWN, aligned_edge=LEFT, buff=0.15
        ).to_corner(UR, 0.15)
        VGroup(self.f_rt, self.r_t).arrange(
            DOWN, aligned_edge=LEFT, buff=0.15
        ).to_corner(UL, buff=0.15)

    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(rad(0), rad(80))
        frame.shift(2.5 * UP + 3.5 * RIGHT)
        self.plane.save_state()
        self.plane.set_opacity(0.1)

        screen_rect = ScreenRectangle(
            height=FRAME_HEIGHT, stroke_width=0, fill_opacity=0.3, fill_color=BLACK
        )
        screen_rect.fix_in_frame()

        rs_style = dict(stroke_width=0.05, stroke_color=BLACK, fill_opacity=0.75)
        prev_riemann_sum = self.get_riemann_sum(126, **rs_style)
        t_samples = self.get_samples_on_t_axis(
            len(prev_riemann_sum) + 1, radius=0.015, color=WHITE
        )
        t_samples.fix_in_frame()
        dt_brace = Brace(t_samples[:2], buff=0.01)
        dt_brace.fix_in_frame()
        dt_label = (
            TexText("\\triangle t", color=T_COLOR)
            .scale(0.65)
            .next_to(dt_brace, DOWN, 0.1, aligned_edge=LEFT)
        )
        dt_label.fix_in_frame()
        t_group = Group(self.t_axis, t_samples, dt_brace, dt_label).to_corner(
            DR, buff=0.5
        )

        equivalence = VGroup(
            self.integral_c_tex, TexText("="), self.integral_gt
        ).arrange()
        equivalence.next_to(self.t_axis, UP, 3)
        equivalence.fix_in_frame()
        surr_rect = SurroundingRectangle(equivalence)
        surr_rect.fix_in_frame()
        riemann_sum = self.get_riemann_sum(6, **rs_style)
        rescaled_rs = self.get_rescaled_riemann_sum(riemann_sum)
        rescaled_rs.fix_in_frame()

        self.add(
            self.plane,
            self.curve,
            self.area,
            prev_riemann_sum,
            self.f_xy,
            self.r_t,
            self.delta_s,
            self.f_rt,
            *t_group,
            equivalence
        )
        self.wait(2.5)
        # ShowCreationThenFadeOut places rect on the xy plane
        self.play(ShowCreation(surr_rect, run_time=3))
        self.play(FadeOut(surr_rect, run_time=0.2))
        self.wait()
        self.play(
            prev_riemann_sum.stretch,
            0.0001,
            2,
            {"about_point": self.plane.c2p(0, 0)},
            run_time=2,
        )
        self.play(FadeOut(prev_riemann_sum, run_time=0.25))
        self.wait(0.5)
        self.raise_riemann_rectangles(
            riemann_sum,
            [
                ApplyMethod(
                    dt_brace.stretch_to_fit_width,
                    (self.t_max - self.t_min) * self.t_axis.unit_size / 6,
                    {"about_point": dt_brace.get_corner(UL)},
                    run_time=2,
                ),
                Transform(
                    t_samples,
                    self.get_samples_on_t_axis(7, radius=0.05, color=WHITE),
                    run_time=2,
                ),
            ],
            run_time=2,
        )
        self.wait()

        equivalence.generate_target()
        equivalence.target.center().to_edge().shift(2 * UP)
        for rect in rescaled_rs:
            rect.save_state()
            rect.stretch_to_fit_height(0.00001, about_point=rect.get_bottom())

        self.play(
            MoveToTarget(equivalence),
            LaggedStartMap(Restore, rescaled_rs, lag_ratio=0.1, run_time=4),
        )
        self.wait(2)

        for rect, rescaled_rect in zip(riemann_sum, rescaled_rs):
            self.play(
                Indicate(rect, scale_factor=1.01),
                Indicate(rescaled_rect, scale_factor=1.01),
                run_time=0.25,
            )
            self.wait(0.1)
        self.wait(3)
        self.play(Indicate(dt_label))
        self.wait(2)
        self.play(
            LaggedStart(
                *[
                    ApplyMethod(rect.shift, 0.2 * OUT, rate_func=there_and_back)
                    for rect in riemann_sum
                ],
                lag_ratio=0.1,
                run_time=2
            )
        )
        self.wait(0.5)
        self.play(
            LaggedStart(
                *[
                    ApplyMethod(rect.shift, 0.2 * UP, rate_func=there_and_back)
                    for rect in rescaled_rs
                ],
                lag_ratio=0.1,
                run_time=2
            ),
            Indicate(dt_label),
        )
        self.wait(2)

        # will u ever learn how to deal with eqns ???
        new_heights_delta_t = TexText(
            "g(t)", "=", "f(r(t))\\frac{\\triangle s}{\\triangle t}"
        ).scale(0.75)
        new_heights_delta_t.next_to(rescaled_rs, UP)
        new_heights_delta_t[0][2].set_color(T_COLOR)
        new_heights_delta_t[2][0].set_color(SCALAR_FIELD_COLOR)
        new_heights_delta_t[2][2].set_color(CURVE_COLOR)
        new_heights_delta_t[2][4].set_color(T_COLOR)
        new_heights_delta_t[2][7:9].set_color(BLUE_E)
        new_heights_delta_t[2][-2:].set_color(T_COLOR)
        new_heights_delta_t.fix_in_frame()

        self.play(
            LaggedStart(
                *[
                    ApplyMethod(
                        r.stretch,
                        0.85,
                        1,
                        {"about_point": r.get_bottom()},
                        rate_func=there_and_back,
                    )
                    for r in rescaled_rs
                ],
                lag_ratio=0.05,
                run_time=3
            ),
            Indicate(self.integral_gt[1][4:8]),
            Write(new_heights_delta_t, run_time=5),
        )
        self.wait(2)
        self.play(Indicate(self.delta_s[1:]))
        self.wait(2)

        delta_s_over_t = TexText(
            "\sqrt{\left(\\frac{\\triangle x}{\\triangle t} \\right)^{2} + \left(\\frac{\\triangle y}{\\triangle t} \\right)^{2}}"
        ).scale(0.45)
        delta_s_over_t[0][3:5].set_color(X_COLOR)
        delta_s_over_t[0][6:8].set_color(T_COLOR)
        delta_s_over_t[0][12:14].set_color(Y_COLOR)
        delta_s_over_t[0][15:17].set_color(T_COLOR)
        delta_s_over_t.fix_in_frame()
        delta_s_over_t.next_to(new_heights_delta_t[2][6], buff=0.1)

        self.play(
            AnimationGroup(
                FadeOutToPoint(new_heights_delta_t[2][7:]),
                FadeIn(delta_s_over_t, 0.25 * UP),
                lag_ratio=0.5,
                run_time=2,
            )
        )
        new_heights_delta_t[2][7:].set_opacity(0)
        self.wait()
        self.play(
            AnimationGroup(
                FadeOut(VGroup(self.f_xy, self.delta_s)),
                ApplyMethod(VGroup(new_heights_delta_t, delta_s_over_t).to_corner, UR),
                lag_ratio=0.75,
                run_time=2,
            )
        )
        self.wait(3)

        # crank up the rectangles to infinity(-ish)
        n_rects = len(riemann_sum)
        step = 15
        radius = 0.05

        for _ in range(8):
            n_rects += step
            dt = (self.t_max - self.t_min) * self.t_axis.unit_size / n_rects
            new_riemann_sum = self.get_riemann_sum(n_rects, **rs_style)
            new_rescaled_riemann_sum = self.get_rescaled_riemann_sum(new_riemann_sum)
            new_t_samples = self.get_samples_on_t_axis(
                n_rects + 1, radius=radius, color=WHITE
            )
            radius *= 0.75
            self.play(
                Transform(riemann_sum, new_riemann_sum, lag_ratio=0.15),
                Transform(rescaled_rs, new_rescaled_riemann_sum, lag_ratio=0.15),
                Transform(t_samples, new_t_samples),
                ApplyMethod(
                    dt_brace.stretch_to_fit_width,
                    dt,
                    {"about_point": dt_brace.get_corner(UL)},
                ),
            )
            self.wait(0.35)
        self.wait(2)
        self.play(Indicate(delta_s_over_t[0][3:8]))
        self.wait()
        self.play(Indicate(delta_s_over_t[0][12:17]))
        self.wait(2)

        deriv_sqrt = TexText("\sqrt{x'(t)^2+y'(t)^2}")
        deriv_sqrt[0][2].set_color(X_COLOR)
        deriv_sqrt[0][9].set_color(Y_COLOR)
        deriv_sqrt[0][5].set_color(T_COLOR)
        deriv_sqrt[0][12].set_color(T_COLOR)
        deriv_sqrt.scale(0.7).next_to(new_heights_delta_t[2][6], buff=0.1)
        deriv_sqrt.fix_in_frame()
        # self.add(deriv_sqrt)
        self.play(
            AnimationGroup(
                FadeOutToPoint(delta_s_over_t),
                FadeIn(deriv_sqrt),
                lag_ratio=0.5,
                run_time=2,
            )
        )
        self.wait(4)
        self.play(Indicate(self.integral_c_tex[1]))
        self.wait(2)
        self.play(Indicate(self.integral_gt[1]))
        self.wait(4)


class Thanks3B1B(Scene):
    def construct(self):
        made_with = Text("Made with ", "Manim (shaders)")
        gratitude = Text("Sincere thanks to ", "Grant Sanderson")
        message = (
            VGroup(made_with, gratitude)
            .set_width(FRAME_WIDTH - 2)
            .arrange(DOWN, buff=1.25)
        )
        for text in message:
            text[1].set_color_by_gradient(BLUE, GREY_BROWN)  # hmm so 3Blue1GreyBrown ?

        self.wait()
        self.play(Write(made_with))
        self.wait()
        self.play(Write(gratitude, run_time=3))
        self.wait(2)
        self.play(FadeOut(VGroup(*self.mobjects)))
        self.wait(6)

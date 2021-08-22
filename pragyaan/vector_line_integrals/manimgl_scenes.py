from manimlib import *

from utils import ellipse

from ..scalar_line_integrals.functions import get_parametric_curve
from ..scalar_line_integrals.scenes import (
    CURVE_COLOR,
    T_COLOR,
    X_COLOR,
    Y_COLOR,
    OpeningSceneLineIntegrals,
    ScalarLineIntegralScene,
)
from .manimgl_animations import ConstantAreaAnimation, GrowVectors, ShrinkVectors

CAMERA_CONFIG = dict(samples=32, anti_alias_width=1.50)

DARK_GREY = "#444444"

FRAME_RECT = ScreenRectangle(
    height=8,
    stroke_width=0,
    fill_opacity=0.6,
    fill_color="#111111",
)
FRAME_RECT.fix_in_frame()

FIELD_BACKGROUND = Surface(
    uv_func=lambda u, v: [u, v, 0],
    u_range=[-10, 10],
    v_range=[-6, 6],
    color=DARK_GREY,
    opacity=0.75,
    gloss=0.0,
    shadow=1.0,
)


class IntroPrevVideo(OpeningSceneLineIntegrals):
    CONFIG = dict(
        camera_config=CAMERA_CONFIG,
        plane_config=dict(faded_line_ratio=1),
    )

    def construct(self):
        frame = self.camera.frame
        scalar_field = self.get_parametric_surface(
            u_range=[-3, 3],
            v_range=[-3, 3],
            color=GREY,
            opacity=1,
            shadow=0.4,
            gloss=0.1,
        )
        for axis, col in zip(self.plane.axes, [X_COLOR, Y_COLOR]):
            axis.set_stroke(col, width=4)

        plane_bg = Surface(
            uv_func=lambda u, v: [u, v, 0],
            u_range=[-15, 15],
            v_range=[-15, 15],
            color=DARK_GREY,
            opacity=0.75,
            gloss=0,
            shadow=1,
        )

        self.add(plane_bg, self.plane, self.curve)

        self.wait(0.25)
        self.play(
            LaggedStart(
                FadeIn(FRAME_RECT),
                ApplyMethod(frame.set_euler_angles, -20 * DEGREES, 60 * DEGREES),
                FadeIn(scalar_field),
                run_time=3,
                lag_ratio=0.5,
            )
        )
        self.play(
            ShowCreation(self.area),
            ApplyMethod(frame.set_euler_angles, 15 * DEGREES, 75 * DEGREES),
            run_time=4,
        )
        self.play(FadeOut(scalar_field, run_time=0.5))
        self.play(
            Transform(self.area, self.get_flattened_area(6 * LEFT)),
            Transform(self.curve, self.get_flattened_curve(6 * LEFT)),
            run_time=2,
        )
        self.wait(0.25)

        frame.generate_target()
        frame.target.set_euler_angles(30 * DEGREES, 72 * DEGREES)
        frame.target.shift(LEFT + 3 * DOWN + OUT)

        axes_origin = 3 * LEFT + 6 * DOWN
        self.t_axis.shift(axes_origin - self.t_axis.n2p(0))
        y_axis = NumberLine([-1, 6], unit_size=0.75)
        y_axis_origin = y_axis.n2p(0)
        y_axis.rotate(PI / 2, about_point=y_axis_origin).rotate(
            PI / 2, axis=RIGHT, about_point=y_axis_origin
        )
        y_axis.shift(axes_origin - y_axis_origin)

        # get_rescaled_riemann_sum is a pathetic method, refactor!
        rescaled_area = self.get_rescaled_riemann_sum(self.area)
        for rect in rescaled_area:
            rect.scale(y_axis.get_unit_size(), about_edge=DOWN)
        rescaled_area.rotate(PI / 2, axis=RIGHT, about_point=axes_origin)
        rescaled_area.next_to(
            self.t_axis.n2p(-3), RIGHT, buff=0, aligned_edge=IN + LEFT
        )

        arrow = CurvedArrow(
            self.area.get_right(), rescaled_area.get_right(), angle=-TAU / 8
        )

        self.play(MoveToTarget(frame))
        self.play(
            ShowCreation(rescaled_area, run_time=2),
            ShowCreation(self.t_axis),
            ShowCreation(y_axis),
            ShowCreation(arrow),
        )
        self.wait()
        # self.interact()


class VectorFieldSummary(OpeningSceneLineIntegrals):

    CONFIG = dict(
        camera_config=CAMERA_CONFIG,
        plane_config=dict(x_range=[-8, 8], y_range=[-5, 5], faded_line_ratio=1),
    )

    def setup(self):
        super().setup()
        for axis, col in zip(self.plane.axes, [X_COLOR, Y_COLOR]):
            axis.set_stroke(col, width=2, recurse=False)

        self.title = Text(
            "Vector Fields", color=np.tile([WHITE, DARK_GREY, GREY], 4)[:-1]
        )
        self.title.add_background_rectangle(buff=0.25, opacity=0.75)
        self.title.background_rectangle.round_corners(radius=0.25)
        self.title.scale(1.5).to_edge(UP, buff=0.025)

        self.field = VectorField(
            self.field_func, self.plane, length_func=lambda l: 0.7, step_multiple=1
        )
        self.true_field = VectorField(
            self.field_func, self.plane, length_func=lambda l: l, step_multiple=1
        ).set_color(WHITE)

        x_range = self.plane.x_range[:2]
        y_range = self.plane.y_range[:2]

        self.field_background = Surface(
            uv_func=lambda u, v: [u, v, 0],
            u_range=np.array(x_range) * 1.15,
            v_range=np.array(y_range) * 1.15,
            color=DARK_GREY,
            opacity=0.75,
            gloss=0.0,
            shadow=1.0,
        )

        self.spheres_at_tails = self.get_sample_input_spheres(
            [x_range[0], x_range[1] + 1],
            [y_range[0], y_range[1] + 1],
            radius=0.1,
            gloss=0.5,
            shadow=0.1,
        )

        self.scalar_field_surface = self.get_parametric_surface(
            u_range=x_range,
            v_range=y_range,
            color=DARK_GREY,
            opacity=0.75,
            shadow=0.5,
            gloss=0.15,
        )

        self.field_func_text = Tex(
            "\overrightarrow{F}",
            "(",
            "x",
            ",",
            "y",
            ")",
            "=",
            "[",
            "-y",
            ",",
            "x",
            "]",
            tex_to_color_map=dict(x=X_COLOR, y=Y_COLOR),
        )
        self.frame = self.camera.frame

    @staticmethod
    def field_func(*point: float):
        return np.array([-point[1], point[0], 0])

    def construct(self):
        self.frame.scale(1 / 0.65)
        self.frame.set_euler_angles(phi=40 * DEGREES)

        self.title.fix_in_frame()

        self.add(self.field_background, self.plane, self.field, self.title)
        self.wait(0.25)
        self.play(
            ApplyWave(self.title, run_time=1.5),
            ShrinkVectors(
                self.field, lag_ratio=0.01, run_time=1.5, rate_func=there_and_back
            ),
        )
        self.wait(0.25)

        self.field_func_text.scale(1.35).to_edge(UP, buff=0.15)
        self.field_func_text.fix_in_frame()

        self.title.generate_target()
        self.title.target.scale(0.75).to_corner(UL, buff=0.15)

        self.play(
            # will you let me complete my video please, since when is this broken?!
            # FadeOut(self.title),
            AnimationGroup(
                MoveToTarget(self.title),
                FadeIn(
                    self.field_func_text[:6], 0.25 * DOWN, scale=1.015, lag_ratio=0.05
                ),
                lag_ratio=0.5,
                run_time=0.8,
            )
        )
        self.wait()
        self.play(Indicate(self.field_func_text[2:5]))
        self.wait()

        self.play(
            AnimationGroup(
                ShrinkVectors(self.field, scale_factor=0.01, save_state=True),
                LaggedStartMap(GrowFromCenter, self.spheres_at_tails),
                lag_ratio=0.5,
                run_time=2,
            )
        )
        self.wait(2)

        self.play(
            FadeIn(self.field_func_text[6:], 0.25 * DOWN, scale=1.015, lag_ratio=0.05)
        )
        self.wait(0.5)
        self.play(LaggedStartMap(Restore, self.field, run_time=2, lag_ratio=0.05))
        self.wait(2)

        self.quick_scalar_field_tour()
        # back to vector field
        self.play(
            FadeOut(self.scalar_field_surface),
            *map(
                Restore,
                [self.frame, self.spheres_at_tails, self.title, self.field_func_text],
            ),
            run_time=2,
        )
        self.play(LaggedStartMap(Restore, self.field, run_time=2, lag_ratio=0.05))
        self.wait(2)

        self.field.save_state()
        self.play(Transform(self.field, self.true_field, lag_ratio=0.025, run_time=3))
        self.wait(0.25)
        self.play(Restore(self.field, run_time=3, lag_ratio=0.025))
        self.wait(4)

        # self.interact()

    def quick_scalar_field_tour(self):
        scalar_field_text = Text(
            "Scalar Fields", color=np.tile([WHITE, DARK_GREY, GREY], 4)[:-1]
        )
        scalar_field_text.add_background_rectangle(buff=0.25, opacity=0.75)
        scalar_field_text.background_rectangle.round_corners(radius=0.25)
        scalar_field_text.scale(1.5).to_edge(UP, buff=0.025)
        scalar_field_text.fix_in_frame()

        self.frame.save_state()
        self.spheres_at_tails.save_state()
        self.field_func_text.save_state()
        self.title.save_state()

        self.play(
            ShrinkVectors(self.field, scale_factor=0.01, run_time=1, save_state=True)
        )
        self.raise_sample_spheres_to_output(
            self.spheres_at_tails,
            added_anims=[
                ApplyMethod(self.title.shift, 4 * UP, run_time=1),
                GrowFromCenter(scalar_field_text, lag_ratio=0.025, run_time=0.5),
                ApplyMethod(self.field_func_text.shift, 4 * UP, run_time=1),
                ApplyMethod(self.frame.set_euler_angles, -10 * DEGREES, 70 * DEGREES),
            ],
            run_time=8,
        )
        self.play(ShowCreation(self.scalar_field_surface, run_time=2))
        self.play(ApplyMethod(scalar_field_text.shift, 2 * UP))


class Prerequisites(Scene):
    CONFIG = dict(camera_config=CAMERA_CONFIG)
    force_vector_length = 5
    force_angle = PI / 6
    displacement_color = GOLD_E
    force_color = GREEN_E
    ground_color = "#003B73"

    def setup(self):
        self.t2c = dict(S=self.displacement_color, F=self.force_color)
        self.frame = self.camera.frame
        # order matters!
        self.setup_ground()
        self.setup_block()
        self.setup_force_vector()
        self.setup_force_projection_vector()
        self.setup_displacement_tex()
        self.setup_formula()

    def setup_ground(self):
        self.ground_surface = Surface(
            uv_func=lambda u, v: [u, v, 0],
            u_range=[-15, 15],
            v_range=[-10, 10],
            gloss=0.25,
            shadow=0.85,
            opacity=0.15,
            color=self.ground_color,
        )
        # hmm, choose a smooth texture or just use the surface above?
        self.ground = TexturedSurface(self.ground_surface, "grass", shadow=0.75)

        self.base = Prism(color=self.ground_color, opacity=0.15, gloss=0.0, shadow=0.75)
        self.base.match_width(self.ground_surface).match_height(self.ground_surface)
        self.base.set_depth(1, stretch=True)
        self.base.shift(0.5 * self.base.get_depth() * IN)

    def setup_block(self):
        self.block = Cube(color=MAROON_E, gloss=0.25, shadow=0.15)
        self.block.move_to([-10, 0, 0]).shift(0.5 * self.block.side_length * OUT)

        self.block_trace = TracedPath(
            self.block.get_center, stroke_color=GOLD_E, stroke_width=10
        )

    def setup_force_vector(self):
        self.force_vector = Vector(
            self.force_vector_length * RIGHT, color=self.force_color
        )
        self.force_vector.rotate(PI / 2, axis=RIGHT).rotate(self.force_angle, axis=DOWN)
        self.add_force_vector_updater(self.force_vector)

        self.force_vector_tex = (
            Tex("\overrightarrow{F}", tex_to_color_map=self.t2c)
            .scale(1.25)
            .rotate(PI / 2, axis=RIGHT)
        )
        self.force_vector_tex.add_updater(
            lambda text: text.next_to(
                self.force_vector, direction=OUT + RIGHT, buff=0.25
            )
        )

    def setup_force_projection_vector(self):
        self.force_projection_vector = Vector().rotate(PI / 2, axis=RIGHT)
        self.force_projection_vector.set_length(self.force_vector.length_over_dim(0))
        self.force_projection_vector.shift(
            self.block.get_center() - self.force_projection_vector.get_start()
        )
        self.add_force_vector_updater(self.force_projection_vector)

        self.force_projection_tex = (
            Tex("\overrightarrow{F}", ".", "\hat{S}", tex_to_color_map=self.t2c)
            .scale(1.25)
            .rotate(PI / 2, axis=RIGHT)
        )
        self.force_projection_tex.add_updater(
            lambda tex: tex.next_to(
                self.force_projection_vector, direction=OUT + RIGHT, buff=0.25
            )
        )

        self.projection_line = DashedLine(
            self.force_vector.get_end(), self.force_projection_vector.get_end()
        )
        self.projection_line.add_updater(
            lambda l: l.put_start_and_end_on(
                self.force_vector.get_end(), self.force_projection_vector.get_end()
            )
        )

    def setup_displacement_tex(self):
        self.displacement_vector_tex = (
            Tex("\overrightarrow{S}", color=self.displacement_color)
            .scale(1.25)
            .rotate(PI / 2, axis=RIGHT)
        )
        self.displacement_vector_tex.add_updater(
            # lambda text: text.next_to(self.block_trace, OUT, buff=0.25)
            lambda text: text.next_to(
                self.block_trace.get_end(), (5 * LEFT + OUT) * 1.25
            )
        )

    def setup_formula(self):
        self.work_text = Group(
            Text("Work done by "),
            Tex("\overrightarrow{F}", tex_to_color_map=self.t2c),
        ).arrange(buff=0.1, aligned_edge=DOWN)
        self.work_text.fix_in_frame()

        self.work_formula = Tex(
            "=",
            "(",
            "\overrightarrow{F}",
            ".",
            "\hat{S}",
            ")",
            "*",
            "|",
            "\overrightarrow{S}",
            "|",
            tex_to_color_map=self.t2c,
        )
        self.work_formula.fix_in_frame()

        self.formula = (
            Group(self.work_text, self.work_formula)
            .arrange(buff=0.2)
            .to_corner(UL, buff=0.25)
        )

    def add_force_vector_updater(self, force_vector):
        force_vector.add_updater(
            lambda f: f.shift(self.block.get_center() - force_vector.get_start())
        )

    def construct(self, block_velocity=1.5, frame_rotation_velocity=-0.02):
        self.frame.scale(1 / 0.5)
        self.frame.set_euler_angles(phi=70 * DEGREES)
        self.frame.add_updater(
            lambda f, dt: f.increment_theta(frame_rotation_velocity * dt)
        )

        self.block.set_opacity(0.95)
        init_block = self.block.copy().set_opacity(0.75)

        self.block.add_updater(lambda b, dt: b.shift(block_velocity * dt * RIGHT))

        self.force_vector_tex.scale(1.5)
        self.displacement_vector_tex.scale(1.5)

        self.formula_rect = SurroundingRectangle(self.formula)
        self.formula_rect.fix_in_frame()

        self.add(
            # self.ground_surface,
            self.formula,
            self.base,
            self.ground,
            init_block,
            self.block,
            self.block_trace,
            self.force_vector,
            self.force_projection_vector,
            self.projection_line,
            self.force_vector_tex,
            self.force_projection_tex,
            self.displacement_vector_tex,
            self.frame,
        )
        self.show_prerequisites()

    def show_prerequisites(self):
        self.wait(4)
        self.play(ShowCreationThenFadeOut(self.formula_rect))
        self.wait(0.5)

        self.block.suspend_updating()
        self.play(
            Indicate(self.work_formula[2:7]),
            TransformFromCopy(
                self.force_projection_vector,
                self.force_vector,
                rate_func=there_and_back,
            ),
            run_time=2,
        )
        self.block.resume_updating()
        self.wait(4)
        # self.interact()


class StraightLineWork(Prerequisites):
    def show_prerequisites(self):
        pass

    def construct(self):
        super().construct(block_velocity=1.25, frame_rotation_velocity=-0.01)
        rect = SurroundingRectangle(
            self.work_formula[1:8], stroke_width=1, fill_opacity=0.25, buff=0.05
        )
        rect.fix_in_frame()

        self.remove(
            self.force_projection_vector,
            self.projection_line,
            self.force_projection_tex,
        )
        self.wait(4)
        self.block.suspend_updating()

        self.play(
            AnimationGroup(
                AnimationGroup(
                    ShowCreation(self.projection_line),
                    GrowFromEdge(rect, LEFT),
                    GrowFromEdge(self.force_projection_vector, LEFT),
                    run_time=4,
                ),
                Write(self.force_projection_tex),
                lag_ratio=0.75,
            )
        )

        self.block.resume_updating()
        self.wait()

        rect.generate_target()
        rect.target = SurroundingRectangle(
            self.work_formula[9:], stroke_width=1, fill_opacity=0.25, buff=0.05
        )
        rect.target.fix_in_frame()

        self.play(MoveToTarget(rect))
        self.wait(4)
        # self.interact()


class ProductAsArea(Scene):
    CONFIG = dict(camera_config=CAMERA_CONFIG)

    def construct(self):
        t2c = {"2": BLUE_E, "4": YELLOW_E}

        product = Tex("(", "2", "*", "4", ")", tex_to_color_map=t2c).scale(3)
        equiv = Tex("\equiv").scale(3)
        rect = Rectangle(width=2, height=4, stroke_width=1, fill_opacity=0.5)
        rect.set_color([t2c[key] for key in t2c])
        prod_equiv_area = (
            Group(product, equiv, rect).arrange(buff=2).to_edge(DOWN, buff=1.5)
        )

        rect_braces = []
        for text, direction in zip([*product[1::2]], [DOWN, RIGHT]):
            brace = BraceLabel(rect, text.tex_string, direction)
            brace.label.set_color(text.get_color())
            rect_braces.append(brace)

        area_text = Text("As this area").next_to(rect, UP)
        product_text = Text("Think of this product...").next_to(product, UP)
        product_text.shift((area_text.get_y() - product_text.get_y()) * UP)

        self.add(FIELD_BACKGROUND)
        self.play(
            AnimationGroup(
                Write(product[:: len(product.tex_strings) - 1], lag_ratio=0),
                LaggedStart(
                    *[FadeIn(text, scale=1 / 1.5) for text in product[1:4]],
                    lag_ratio=0.25,
                ),
                lag_ratio=0.1,
            )
        )
        self.play(FadeIn(product_text, scale=1 / 1.25, lag_ratio=0.05, run_time=1.75))
        self.wait(0.25)
        self.play(FadeIn(area_text, scale=1 / 1.25, lag_ratio=0.05, run_time=1.25))
        self.play(
            AnimationGroup(
                GrowFromPoint(rect, point=rect.get_corner(UL)),
                LaggedStartMap(
                    GrowFromCenter,
                    Group(*[brace.brace for brace in rect_braces]),
                    lag_ratio=0,
                ),
                run_time=1.5,
                lag_ratio=0.75,
            )
        )
        self.play(
            TransformFromCopy(product[1], rect_braces[0].label, path_arc=-PI / 2),
            TransformFromCopy(product[3], rect_braces[1].label, path_arc=PI / 2),
            run_time=0.75,
        )
        self.wait(2)


class RescaleWhileMaintaingArea(Scene):
    CONFIG = dict(camera_config=CAMERA_CONFIG)
    initial_width = 2
    initial_height = 8
    colors = [BLUE, GREEN]  # width_text, height_text
    rectangle_style = dict(stroke_width=0, fill_opacity=0.75, shadow=0.5, gloss=0.25)

    def setup(self):
        self.axes = Axes(
            [0, 6],
            [0, 24, 4],
            width=FRAME_X_RADIUS + 4,
            height=FRAME_HEIGHT - 1,
            axis_config=dict(include_numbers=True),
            y_axis_config=dict(line_to_number_direction=UP),
        )
        self.axes.get_axis_labels("w", "h")
        self.axes.to_corner(DL, buff=0.25)

        self.rectangle = Rectangle(
            width=self.initial_width * self.x_unit,
            height=self.initial_height * self.y_unit,
            fill_color=self.colors,
            **self.rectangle_style,
        )
        self.rectangle.next_to(self.axes.get_origin(), UR, buff=0, aligned_edge=DL)

        brace_buff = 0.1
        self.rectangle_braces = self.get_rectangle_braces(
            self.rectangle, ["w", "h"], [UP, RIGHT], self.colors, buff=brace_buff
        )
        self.add_rectangle_brace_updaters(brace_buff)

        self.rectangle_copy = self.rectangle.copy()
        self.rectangle_copy_braces = self.get_rectangle_braces(
            self.rectangle_copy,
            [self.initial_width, self.initial_height],
            [UP, RIGHT],
            self.colors,
        )

        self.rectangle_copy_group = VGroup(
            self.rectangle_copy, self.rectangle_copy_braces
        )
        self.rectangle_copy_group.add_background_rectangle(
            color=DARK_GREY, opacity=0.75, buff=0.25, shadow=0.8, gloss=0.25
        )
        self.rectangle_copy_group.background_rectangle.round_corners(radius=0.25)
        self.rectangle_copy_group.to_corner(UR, buff=0.1)

        self.t2c = {
            "h": self.colors[1],
            "w": self.colors[0],
            f"{self.initial_width}": self.colors[0],
            f"{self.initial_height}": self.colors[1],
        }
        self.area_equation = Tex(
            "h",
            "*",
            "w",
            "=",
            str(self.initial_width),
            "*",
            str(self.initial_height),
            tex_to_color_map=self.t2c,
        )
        self.new_height = VGroup(
            Tex("h", tex_to_color_map=self.t2c),
            Tex("="),
            VGroup(
                Tex(
                    str(self.initial_width),
                    "*",
                    str(self.initial_height),
                    tex_to_color_map=self.t2c,
                ),
                Line(0.5 * LEFT, 0.5 * RIGHT),
                Tex("w", tex_to_color_map=self.t2c),
            ).arrange(DOWN, buff=0.2),
        ).arrange(buff=0.25)

    @property
    def x_unit(self):
        return self.axes.x_axis.get_unit_size()

    @property
    def y_unit(self):
        return self.axes.y_axis.get_unit_size()

    @staticmethod
    def get_rectangle_braces(
        rectangle, brace_labels, brace_directions, label_colors, **kwargs
    ):
        braces = VGroup()
        for color, direction, label in zip(
            label_colors, brace_directions, brace_labels
        ):
            brace = BraceLabel(
                rectangle, text=str(label), brace_direction=direction, **kwargs
            )
            brace.label.set_color(color)
            braces.add(brace)
        return braces

    def add_rectangle_brace_updaters(self, brace_buff):
        def brace_upd(brace, dim):
            new_length = self.rectangle.length_over_dim(dim)
            scale_factor = new_length / brace.brace.length_over_dim(dim)

            brace.brace.rescale_to_fit(new_length, dim, stretch=True)
            brace.label.scale(scale_factor)
            brace.next_to(self.rectangle, brace.brace_direction, buff=brace_buff)

        for brace, dim in zip(self.rectangle_braces, [0, 1]):
            brace.dim = dim
            brace.add_updater(lambda brace: brace_upd(brace, brace.dim))

    def change_width(self, target_width, **kwargs):
        self.play(
            ConstantAreaAnimation(self.rectangle, self.axes, target_width, **kwargs)
        )

    def construct(self):
        self.add(
            FIELD_BACKGROUND,
            self.axes,
            self.rectangle,
        )
        self.wait()

        self.play(
            LaggedStart(
                FadeIn(self.rectangle_copy_group.background_rectangle, scale=1 / 1.25),
                TransformFromCopy(
                    self.rectangle, self.rectangle_copy, run_time=1.25, path_arc=PI / 2
                ),
                lag_ratio=0.05,
            )
        )
        self.play(
            LaggedStartMap(
                GrowFromCenter,
                self.rectangle_copy_braces,
                lag_ratio=0.01,
                run_time=0.75,
            )
        )
        self.wait()

        self.play(*map(GrowFromCenter, self.rectangle_braces))

        trace = TracedPath(
            lambda: self.rectangle.get_corner(UR),
            stroke_color=self.colors[1],
            stroke_width=4,
        )
        self.add(trace)

        self.change_width(0.75)
        self.change_width(5.25, run_time=2)
        self.change_width(3, run_time=1.25)
        self.wait()

        eqn_group = Group(self.area_equation, self.new_height).scale(1.25)
        eqn_group.arrange(DOWN, buff=1).move_to(trace)

        self.play(
            FadeIn(self.area_equation, scale=1 / 1.25, lag_ratio=0.05, run_time=1.5)
        )
        self.wait(0.5)
        self.play(FadeIn(self.new_height, scale=1 / 1.25, lag_ratio=0.05, run_time=2))
        self.wait(4)

        # self.interact()


class VectorFieldLineIntegrals(ScalarLineIntegralScene):
    CONFIG = dict(
        camera_config=CAMERA_CONFIG,
        plane_config=dict(
            x_range=[-10, 10],
            y_range=[-6, 6],
            faded_line_ratio=1,
            axis_config=dict(stroke_width=1),
        ),
        field_kwargs=dict(step_multiple=1, length_func=lambda l: 0.75),
    )

    @staticmethod
    def t_func(t):
        pass

    @staticmethod
    def field_func(*point: np.ndarray):
        pass

    @property
    def x_unit(self):
        return self.plane.x_axis.get_unit_size()

    @property
    def y_unit(self):
        return self.plane.y_axis.get_unit_size()

    def get_rectangle_height(self, t, dt):
        r_t = self.t_func(t)
        r_t_plus_dt = self.t_func(t + dt)
        force_vect = self.field_func(*r_t)
        unit_displacement = normalize(r_t_plus_dt - r_t)

        return np.dot(force_vect, unit_displacement)

    def change_in_t_animation(self, target_t, **kwargs):
        return ApplyMethod(self.t_tracker.set_value, target_t, **kwargs)

    def get_riemann_sum(self, n_rects, gradient=None, **rect_style):
        if gradient is None:
            gradient = self.riemann_gradient
        style = dict(self.area_style, **rect_style)

        rects = VGroup()
        t_range, dt = np.linspace(
            self.t_min, self.t_max, n_rects, endpoint=False, retstep=True
        )

        for t in t_range:
            r_t = self.t_func(t)
            r_t_plus_dt = self.t_func(t + dt)

            force_vect = self.field_func(*r_t)
            unit_displacement = normalize(r_t_plus_dt - r_t)
            height = np.dot(force_vect, unit_displacement)

            dl = self.c2p(r_t)
            dr = self.c2p(r_t_plus_dt)
            ul = self.c2p([*r_t[:2], height])
            ur = ul + (dr - dl)
            rects.add(Polygon(ur, ul, dl, dr, **style))

        rects.set_color_by_gradient(*gradient)
        return rects

    def get_rescaled_riemann_sum(self, riemann_sum, new_axes, **style):
        x_unit = new_axes.x_axis.get_unit_size()
        y_unit = new_axes.y_axis.get_unit_size()
        t_range, dt = np.linspace(
            self.t_min, self.t_max, len(riemann_sum), endpoint=False, retstep=True
        )
        style = dict(self.area_style, **style)
        rescaled_sum = VGroup()

        for rect, t in zip(riemann_sum, t_range):
            r_t = self.t_func(t)
            r_t_plus_dt = self.t_func(t + dt)

            height = np.dot(self.field_func(*r_t), normalize(r_t_plus_dt - r_t))
            width = np.linalg.norm(r_t_plus_dt - r_t)

            rescaled_rect = Rectangle(
                width=dt * x_unit,
                height=((width * height) / dt) * y_unit,
                color=rect.get_color(),
                **style,
            )
            rescaled_rect.next_to(
                new_axes.x_axis.n2p(t),
                direction=UR if height > 0 else DR,
                buff=0,
                aligned_edge=LEFT,
            )
            rescaled_sum.add(rescaled_rect)
        rescaled_sum.set_style(**style)
        return rescaled_sum

    def shrink_riemann_sum(self, riemann_sum, factor=0.01, dim=2, save_state=True):
        about_edge = [LEFT, DOWN, IN][dim]
        for rect in riemann_sum:
            if save_state:
                rect.save_state()
            rect.stretch(factor, dim=dim, about_edge=about_edge)
        return self

    @property
    def particle_updater(self):
        def func(particle):
            particle.move_to(self.c2p(self.t_func(self.t_tracker.get_value())))
            # particle.move_to(self.curve.get_end())

        return func

    @property
    def curve_updater(self):
        def func(curve):
            curve.pointwise_become_partial(
                curve.starting_curve, 0, self.t_tracker_alpha
            )

        return func

    @property
    def t_tracker_alpha(self):
        return (self.t_tracker.get_value() - self.t_min) / (self.t_max - self.t_min)

    @property
    def force_vector_updater(self):
        def force_upd(force_vector):
            t = self.t_tracker.get_value()
            point = self.t_func(t)
            field_output = self.field_func(*point)
            field_output_norm = np.linalg.norm(field_output)
            rgba_array = np.array(
                [
                    [
                        *self.field.value_to_rgb(field_output_norm),
                        force_vector.opacity,
                    ]
                ]
            )

            force_vector.set_length(np.linalg.norm(self.c2p(field_output)))
            force_vector.set_angle(angle_of_vector(self.c2p(field_output)))
            force_vector.set_rgba_array(rgba_array)
            force_vector.shift(self.c2p(point) - force_vector.get_start())

        return force_upd

    @property
    def displacement_vector_updater(self, dt=0.01):
        def disp_upd(disp_vector):
            t = self.t_tracker.get_value()
            r_t = self.c2p(self.t_func(t))
            angle = angle_of_vector(self.c2p(self.t_func(t + dt) - r_t))

            disp_vector.set_angle(angle)
            disp_vector.shift(r_t - disp_vector.get_start())

        return disp_upd

    def get_force_vector_rgba(self, t):
        point = self.t_func(t)
        field_output = self.field_func(*point)
        field_output_norm = np.linalg.norm(field_output)
        rgba_array = np.array(
            [
                [
                    *self.field.value_to_rgb(field_output_norm),
                    self.force_vector.opacity,
                ]
            ]
        )
        return rgba_array

    def get_force_vector_length(self, t):
        point = self.t_func(t)
        field_output = self.field_func(*point)
        return np.linalg.norm(self.c2p(field_output))

    def setup(self):
        self.t_tracker = ValueTracker(self.t_min)
        self.add(self.t_tracker)

        self.t_axis = NumberLine(x_range=[self.t_min, self.t_max], **self.t_axis_kwargs)
        self.t_axis.fix_in_frame()

        self.setup_axes()

        self.curve = get_parametric_curve(
            self.axes,
            self.t_func,
            t_range=[self.t_min, self.t_max, 0.01],
            **self.curve_kwargs,
        )
        self.curve.starting_curve = self.curve.copy()
        self.curve.add_updater(self.curve_updater)

        self.field = VectorField(
            func=self.field_func, coordinate_system=self.plane, **self.field_kwargs
        )

        self.force_vector = Vector()
        self.force_vector.add_updater(self.force_vector_updater)

        self.displacement_vector = Vector().set_color(self.curve.get_color())
        self.displacement_vector.add_updater(self.displacement_vector_updater)

        self.area = self.get_riemann_sum(self.n_rects_for_area)
        self.frame = self.camera.frame


class VectorLineIntegralsScenes(VectorFieldLineIntegrals):
    CONFIG = dict(
        t_min=PI,
        t_max=TAU,
        t_axis_kwargs=dict(
            width=8,
            stroke_width=4,
            include_numbers=True,
            decimal_number_config=dict(num_decimal_places=2),
            numbers_with_elongated_ticks=[PI, TAU],
            longer_tick_multiple=2,
        ),
        curve_kwargs=dict(stroke_width=8),
        n_rects_for_area=1000,
    )
    ellipse_width = 8
    ellipse_height = 5
    x_color = X_COLOR
    y_color = Y_COLOR
    t_color = T_COLOR

    @staticmethod
    def field_func(*point: float):
        x, y = point[:2]
        return np.array([x - y, x + y, 0])

    def t_func(self, theta):
        return ellipse(self.ellipse_width / 2, self.ellipse_height / 2, theta)

    @property
    def t_tracker_dot_updater(self):
        def dot_upd(sphere):
            sphere.move_to(self.t_axis.n2p(self.t_tracker.get_value()))

        return dot_upd

    @property
    def vector_straight_path_updater(self):
        def upd(vect):
            vect.shift(self.particle.get_center() - vect.get_start())

        return upd

    def move_particle_along_straight_lines(
        self,
        riemann_sum,
        update_t_tracker=True,
        update_displacement_vector=True,
        update_force_vector=True,
        reverse=False,
        **kwargs,
    ):
        n_rects = len(riemann_sum)
        t_vals, dt = np.linspace(
            self.t_min, self.t_max, n_rects, endpoint=False, retstep=True
        )
        vect_direction = 1

        if reverse:
            riemann_sum = riemann_sum[::-1]
            t_vals = t_vals[::-1]
            vect_direction = -1

        paths = []
        anims = []

        if update_force_vector:
            self.force_vector.add_updater(self.vector_straight_path_updater)

        if update_displacement_vector:
            self.displacement_vector.add_updater(self.vector_straight_path_updater)

        for index, t in enumerate(t_vals):
            start = self.c2p(self.t_func(t))
            end = self.c2p(self.t_func(t + dt))
            target_t_alpha = (index + 1) / n_rects
            if reverse:
                start, end = end, start
                target_t_alpha = 1 - target_t_alpha

            path = Line(start, end).set_opacity(0)
            paths.append(path)

            # anims
            anims = []
            if update_t_tracker:
                anims.append(
                    ApplyMethod(
                        self.t_tracker.set_value,
                        interpolate(self.t_min, self.t_max, target_t_alpha),
                    )
                )
            if update_displacement_vector:
                self.displacement_vector.set_angle(
                    angle_of_vector((end - start) * vect_direction)
                )
            if update_force_vector:
                self.force_vector.set_angle(
                    angle_of_vector((end - start) * vect_direction)
                )

            anims.append(MoveAlongPath(self.particle, path))
            self.play(*anims, rate_func=linear, **kwargs)

    def parametric_function_map_animation(
        self, t_samples, frame_scale_factor=1, **kwargs
    ):
        # why is frame scale needed??
        anims = []
        rate_func = kwargs.pop("rate_func", smooth)

        for sphere in t_samples:
            t = self.t_axis.p2n(sphere.get_center())
            anims.append(
                ApplyMethod(
                    sphere.move_to,
                    self.c2p(self.t_func(t)) * frame_scale_factor,
                    rate_func=rate_func,
                )
            )
        return LaggedStart(*anims, **kwargs)

    def setup_field_func_tex(self):
        self.field_func_tex = Tex(
            "\overrightarrow{F}",
            "(",
            "x",
            ",",
            "y",
            ")",
            "=",
            "[",
            "x",
            "-",
            "y",
            ",",
            "x",
            "+",
            "y",
            "]",
        ).set_color_by_tex_to_color_map(self.t2c)
        self.field_func_tex.scale(0.85)
        self.field_func_tex.add_background_rectangle(opacity=0.9, buff=0.1)
        self.field_func_tex.background_rectangle.round_corners(0.25)
        self.field_func_tex.fix_in_frame()
        self.field_func_tex.to_corner(UL, buff=0.01)

    def setup_curve_tex(self):
        self.curve_tex = Tex(
            "\overrightarrow{r}",
            "(",
            "t",
            ")",
            "=",
            "[",  # 5
            "4",
            "cos",
            "(",
            "t",
            ")",
            ",",
            "2.5",  # 12
            "sin",
            "(",
            "t",
            ")",
            "]",
        )
        t2c = dict(self.t2c, **dict(t=T_COLOR, r=CURVE_COLOR))
        self.curve_tex.set_color_by_tex_to_color_map(t2c)
        self.curve_tex[6:8].set_color(self.x_color)
        self.curve_tex[12:14].set_color(self.y_color)

        self.curve_tex.scale(0.85)
        self.curve_tex.add_background_rectangle(opacity=0.9, buff=0.1)
        self.curve_tex.background_rectangle.round_corners(0.25)
        self.curve_tex.fix_in_frame()
        self.curve_tex.next_to(self.field_func_tex, DOWN, buff=0, aligned_edge=LEFT)

    def setup_question(self):
        self.question = (
            VGroup(
                Text("Find the work done by the field in"),
                Text("moving a particle along the curve."),
            )
            .scale(0.85)
            .arrange(DOWN, buff=0.15, aligned_edge=LEFT)
            .add_background_rectangle(
                opacity=0.9,
                buff=0.15,
                stroke_width=1,
                stroke_opacity=1,
                stroke_color=WHITE,
            )
        ).set_opacity(0.75)
        self.question.background_rectangle.round_corners(0.25)
        self.question.fix_in_frame()
        self.question.to_corner(UR, buff=0.05)

    def setup_assumptions_text(self):
        # was Paragraph removed?
        text_buff = 0.15
        num_to_text_buff = 0.2

        text = Text("Assumptions:")
        assumption_numbers = VGroup(Text("1."), Text("2."))
        assumption1 = VGroup(
            Text("Particle travels along the straight lines"),
            Text("connecting points on the curve."),
        )
        assumption2 = VGroup(
            Text("Force acting on the particle remains"),
            Text("constant along a given line."),
        )
        num_text_groups = []
        for number, assumption in zip(assumption_numbers, [assumption1, assumption2]):
            assumption.arrange(DOWN, buff=text_buff, aligned_edge=LEFT)
            group = VGroup(number, assumption).arrange(
                buff=num_to_text_buff,  # aligned_edge=UP
            )
            num_text_groups.append(group)

        self.assumptions = VGroup(text, *num_text_groups).scale(0.75)
        self.assumptions.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        self.assumptions.add_background_rectangle(
            buff=0.2, stroke_color=WHITE, stroke_width=1, stroke_opacity=1
        )
        self.assumptions.background_rectangle.round_corners(0.25)
        self.assumptions.to_corner(UR, buff=0.05)
        self.assumptions.fix_in_frame()

        self.assumptions.assumption1 = assumption1
        self.assumptions.assumption2 = assumption2
        self.assumptions.title = text

    def setup_t_axis(self):
        self.t_axis.add_background_rectangle(
            buff=0.2, stroke_color=WHITE, stroke_width=1, stroke_opacity=1
        )
        self.t_axis.background_rectangle.round_corners(0.25)
        self.t_tracker_sphere.fix_in_frame()
        Group(self.t_axis, self.t_tracker_sphere).move_to(1.5 * UP)
        self.t_axis.fix_in_frame()

    def t_range_broadcast_animations(
        self, small_radius, big_radius, n_samples, **kwargs
    ):
        # animations should have a parameter to fix their mobjects in frame
        t_vals = np.linspace(self.t_min, self.t_max, n_samples, endpoint=True)
        range_indicate_anims = [
            Broadcast(
                point,
                small_radius=small_radius,
                big_radius=big_radius,
                color=self.t_color,
            )
            for point in map(self.t_axis.n2p, t_vals)
        ]
        for broadcast in range_indicate_anims:
            anims = broadcast.animations
            for anim in anims:
                anim.mobject.saved_state.fix_in_frame()

        return LaggedStart(*range_indicate_anims, **kwargs)

    def setup(self):
        super().setup()
        for axis, col in zip(self.plane.axes, [X_COLOR, Y_COLOR]):
            axis.set_stroke(width=4, color=col)

        self.t_axis = NumberLine(
            [self.t_min, self.t_max, (self.t_max - self.t_min) / 4],
            **self.t_axis_kwargs,
        )

        self.t_axis.label = (
            Tex("t", color=self.t_color)
            .scale(1.75)
            .next_to(self.t_axis.n2p(self.t_max), buff=0.3)
        )
        self.t_axis.add(self.t_axis.label)

        self.t_tracker_sphere = Sphere(radius=0.125, color=self.t_color)
        self.t_tracker_sphere.add_updater(self.t_tracker_dot_updater)

        self.t2c = dict(
            x=X_COLOR,
            y=Y_COLOR,
        )

        self.background = Surface(
            uv_func=lambda u, v: [u, v, 0],
            u_range=np.array(self.plane.x_range[:2]) * 1.15,
            v_range=np.array(self.plane.y_range[:2]) * 1.15,
            color=DARK_GREY,
            opacity=0.25,
            gloss=0.0,
            shadow=1.0,
        )

        self.title = Text(
            "Line Integrals of Vector Fields",
        ).scale(1.35)
        self.title.fix_in_frame()

        self.particle = Sphere(
            radius=0.2, color=PINK, opacity=1, gloss=0.25, shadow=0.5
        )
        self.particle.move_to(self.curve.point_from_proportion(self.t_tracker_alpha))
        self.particle.add_updater(self.particle_updater)


class TypicalApproach(VectorLineIntegralsScenes):
    def construct(self):
        self.frame.scale(1 / 0.6).shift(0.75 * UP)
        self.frame.set_euler_angles(phi=40 * DEGREES)

        self.title.to_edge(UP, buff=0.25)
        self.t_axis.to_corner(UL)

        self.add(self.background, self.plane)
        self.wait(0.25)
        self.play(
            LaggedStart(
                *[FadeIn(mob, scale=1 / 1.25) for mob in self.title],
                lag_ratio=0.1,
                run_time=2.5,
            )
        )
        self.wait(0.5)
        self.play(GrowVectors(self.field, run_time=1.5, lag_ratio=0.05))
        self.wait(0.1)
        self.play(
            AnimationGroup(
                ApplyMethod(self.field.set_opacity, 0.5, run_time=1),
                FadeIn(self.particle, scale=1 / 2, run_time=0.5),
                GrowVectors(
                    VGroup(self.force_vector, self.displacement_vector),
                    run_time=0.5,
                ),
                lag_ratio=0.5,
            )
        )
        self.wait(0.25)

        self.add(self.curve)
        self.play(
            self.change_in_t_animation((self.t_max + self.t_min) / 2, run_time=2.5)
        )
        self.wait(0.5)
        self.play(self.change_in_t_animation(self.t_max, run_time=2.5))
        self.wait(1.5)
        self.play(self.change_in_t_animation(self.t_min, run_time=1.5))

        self.play(
            self.change_in_t_animation(self.t_max),
            run_time=4,
        )

        self.frame.generate_target()
        self.frame.target.shift(UP)
        self.frame.target.set_euler_angles(phi=55 * DEGREES)

        self.play(
            ShowCreation(self.area),
            MoveToTarget(self.frame),
            run_time=3,
        )

        self.frame.add_updater(lambda frame, dt: frame.increment_theta(0.025 * dt))
        self.add(self.frame)

        flat_area = self.get_flattened_area(5.05 * LEFT)
        flat_curve = self.get_flattened_curve(5.05 * LEFT)

        self.curve.save_state()
        self.play(
            Transform(self.area, flat_area),
            Transform(self.curve, flat_curve),
            run_time=1,
        )

        # why does the curve come back? non_time_updaters broken??
        # print(self.curve.time_based_updaters, self.curve.non_time_updaters)
        # self.curve.clear_updaters()  # even this doesn't work?! What's happening??
        self.remove(self.curve)
        self.show_single_integral()
        # self.interact()

    def show_single_integral(self):

        axes = Axes(
            x_range=[3, 7, 1],
            y_range=[0, 16, 4],
            height=6,
            width=6,
            axis_config=dict(include_numbers=True),
            y_axis_config=dict(line_to_number_direction=UP),
        )
        axes.x_axis.shift(
            axes.y_axis.n2p(axes.y_axis.x_min) - axes.x_axis.n2p(axes.x_axis.x_min)
        )
        axes.fix_in_frame()
        axes.to_corner(DL, buff=0.25)

        rescaled_riemann_sum = self.get_rescaled_riemann_sum(
            self.area, axes, fill_opacity=0.35
        )
        rescaled_riemann_sum.fix_in_frame()

        self.play(ApplyMethod(self.frame.shift, 4.5 * LEFT + 1.5 * DOWN, run_time=0.75))
        self.wait(0.25)
        self.play(
            AnimationGroup(
                ShowCreation(axes),
                LaggedStart(
                    *[GrowFromEdge(mob, DOWN) for mob in rescaled_riemann_sum],
                    lag_ratio=0,
                ),
                lag_ratio=0.25,
                run_time=1,
            )
        )
        self.wait(0.15)
        self.play(
            ApplyWave(self.area, amplitude=0.5, direction=OUT),
            ApplyWave(rescaled_riemann_sum, amplitude=0.5),
        )
        self.wait(8)


class TheQuestion(VectorLineIntegralsScenes):
    CONFIG = dict(curve_kwargs=dict(stroke_width=8))

    def construct(self):
        self.frame.scale(1 / 0.7)

        self.add(self.plane)
        self.wait(0.25)

        self.show_field()
        self.show_question()
        # self.interact()

    def show_field(self):
        self.setup_field_func_tex()
        self.play(GrowVectors(self.field, lag_ratio=0.01, run_time=1.75))
        self.wait(0.05)  # Bug spotted!
        self.play(
            ApplyMethod(self.field.set_opacity, 0.5, run_time=0.5),
            FadeIn(self.field_func_tex, scale=1 / 1.25, lag_ratio=0.05, run_time=1.5),
        )
        self.wait()

    def show_question(self):
        self.setup_curve_tex()
        self.setup_question()

        self.play(
            FadeIn(self.particle, scale=1 / 1.25),
            GrowArrow(self.force_vector),  # why doesn't this animate!?
            GrowArrow(self.displacement_vector)
            # GrowVectors([self.displacement_vector, self.force_vector], lag_ratio=0),
        )
        self.wait(0.15)

        self.setup_t_axis()
        self.play(
            *map(
                lambda mob: FadeIn(mob, scale=1 / 1.25, lag_ratio=0),
                [self.question, self.t_axis, self.t_tracker_sphere],
            ),
            run_time=1.5,
        )

        self.add(self.curve)

        self.play(
            AnimationGroup(
                self.change_in_t_animation(self.t_max, run_time=6),
                FadeIn(self.curve_tex, scale=1 / 1.25, lag_ratio=0.05, run_time=2),
                lag_ratio=0.5,
            )
        )
        self.wait(0.5)

        self.play(
            self.t_range_broadcast_animations(0.1, 0.8, 2, lag_ratio=0.5, run_time=2.5)
        )
        self.wait(0.25)
        self.play(
            ApplyWave(self.question, direction=DOWN),
            self.change_in_t_animation(
                (self.t_min + self.t_max) / 2,
                rate_func=there_and_back,
            ),
            run_time=3,
        )
        self.wait(4)


class ApproximationScene(VectorLineIntegralsScenes):
    CONFIG = dict(t_axis_kwargs=dict(width=5))

    def construct(self):
        self.frame.scale(1 / 0.7)
        self.setup_field_func_tex()
        self.setup_curve_tex()
        self.setup_question()
        self.setup_t_axis()
        self.setup_assumptions_text()

        self.curve_copy = self.curve.starting_curve.copy().set_stroke(opacity=0.5)
        Group(self.t_axis, self.t_tracker_sphere).center().to_edge(
            LEFT, buff=0.1
        ).shift(1.5 * UP)

        self.add(
            self.plane,
            self.field.set_opacity(0.25),
            # self.force_vector,
            self.displacement_vector,
            self.particle,
            self.field_func_tex,
            self.curve_tex,
            self.curve_copy,
            self.t_axis,
            self.t_tracker_sphere,
        )

        self.assumptions[2:].set_opacity(0.5)
        self.wait(3)
        self.play(FadeIn(self.assumptions, scale=1 / 1.25))
        self.play(
            ShowPassingFlashWithThinningStrokeWidth(
                self.curve_copy,
                time_width=1,
                n_segments=20,
            ),
            ApplyWave(
                self.curve_copy,
                amplitude=0.15,
            ),
            ApplyMethod(self.assumptions[2].set_opacity, 1, lag_ratio=1, run_time=2),
            run_time=2,
        )

        self.riemann_sum = self.get_riemann_sum(4, stroke_width=4)
        self.shrink_riemann_sum(self.riemann_sum)
        self.play(ShowCreation(self.riemann_sum, lag_ratio=0, run_time=0.35))

        for mob in [self.particle, self.force_vector, self.displacement_vector]:
            mob.clear_updaters()
        self.bring_to_front(self.particle, self.displacement_vector)

        self.play(
            ApplyMethod(
                self.displacement_vector.set_angle,
                angle_of_vector(-op.sub(*self.riemann_sum[0].get_vertices()[2:])),
                run_time=0.5,
            )
        )
        self.wait(0.15)

        self.move_particle_along_straight_lines(
            self.riemann_sum, update_force_vector=False, run_time=1
        )
        self.wait(2)

        # r_t func map
        self.t_samples = self.get_samples_on_t_axis(
            len(self.riemann_sum) + 1,
            radius=0.075,
            # color=WHITE,
            gloss=0.75,
            shadow=0.25,
        )
        self.t_samples.fix_in_frame()

        self.play(
            self.t_range_broadcast_animations(
                0.1, 0.6, len(self.riemann_sum) + 1, lag_ratio=0.0
            ),
            LaggedStart(*[FadeIn(sph, scale=1 / 2) for sph in self.t_samples]),
            run_time=2,
        )
        self.wait(0.1)

        self.play(
            self.parametric_function_map_animation(
                self.t_samples,
                frame_scale_factor=0.7,  # why is this needed?
                run_time=3,
                rate_func=there_and_back_with_pause,
                lag_ratio=0.01,
            )
        )
        self.wait()
        self.move_particle_along_straight_lines(
            self.riemann_sum,
            update_force_vector=False,
            reverse=True,
            run_time=0.5,
        )
        self.wait()
        # assumption2
        # self.interact()

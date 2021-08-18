from manimlib import *

from ..scalar_line_integrals.scenes import X_COLOR, Y_COLOR, OpeningSceneLineIntegrals

CAMERA_CONFIG = dict(samples=32, anti_alias_width=1.50)

DARK_GREY = "#444444"

FRAME_RECT = ScreenRectangle(
    height=8,
    stroke_width=0,
    fill_opacity=0.6,
    fill_color="#111111",
)
FRAME_RECT.fix_in_frame()


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
    def field_func(*point: np.ndarray):
        return np.array([-point[1], point[0], 0])

    def vector_shrink_animation(
        self,
        field=None,
        scale_factor=0.5,
        run_time=2,
        lag_ratio=0,
        save_state=False,
        **kwargs
    ):
        if field is None:
            field = self.field
        anims = []

        for vect in field:
            if save_state:
                vect.save_state()
            anim = ApplyMethod(
                vect.scale, scale_factor, {"about_point": vect.get_start()}, **kwargs
            )
            anims.append(anim)

        return LaggedStart(*anims, run_time=run_time, lag_ratio=lag_ratio)

    def construct(self):
        self.frame.scale(1 / 0.65)
        self.frame.set_euler_angles(phi=40 * DEGREES)

        self.title.fix_in_frame()

        self.add(self.field_background, self.plane, self.field, self.title)
        self.wait(0.25)
        self.play(
            ApplyWave(self.title, run_time=1.5),
            self.vector_shrink_animation(
                lag_ratio=0.01, run_time=1.5, rate_func=there_and_back
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
                self.vector_shrink_animation(scale_factor=0.01, save_state=True),
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
            self.vector_shrink_animation(scale_factor=0.01, run_time=1, save_state=True)
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


#

from manimlib import *

from ..scalar_line_integrals.scenes import (
    CURVE_COLOR,
    T_COLOR,
    X_COLOR,
    Y_COLOR,
    OpeningSceneLineIntegrals,
)

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
        camera_config=dict(samples=32, anti_alias_width=1.50),
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

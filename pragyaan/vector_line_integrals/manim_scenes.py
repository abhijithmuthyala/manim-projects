from manim import *
from manim.opengl import *
from manim_fonts import RegisterFont

from functions import *
from manim_mobjects import *

NORTH_POLE_COLOR = MAROON_E
SOUTH_POLE_COLOR = BLUE_E
POLE_COLORS = [NORTH_POLE_COLOR, SOUTH_POLE_COLOR]


class RecollectBarMagneticField(Scene):
    def setup(self):
        self.field_background = OpenGLSurface(
            lambda u, v: [u, v, 0],
            [-10, 10],
            [-6, 6],
            color=DARK_GRAY,
            opacity=0.75,
            gloss=0.0,
            shadow=1.0,
        )
        self.plane = NumberPlane(
            [-10, 10], [-6, 6], x_length=20, y_length=12, faded_line_ratio=2
        )
        self.setup_magnet()

        self.compass = OpenGLMagneticCompass(
            annulus_kwargs=dict(stroke_color=np.tile([YELLOW_E, GREEN_E], 4)),
            shield_depth=0.5,
            shield_kwargs=dict(color=DARK_GRAY, opacity=0.25, gloss=0.5, shadow=0.25),
        )
        self.compass.shift(4 * RIGHT)

        self.field_func = get_magnetic_field_func([(3 * UP, 1), (3 * DOWN, -1)])

    def setup_magnet(self):
        self.magnet = OpenGLVGroup()
        self.magnet_pole_labels = OpenGLGroup()

        for label, color, direction in zip(["N", "S"], POLE_COLORS, [UP, DOWN]):
            pole = OpenGLCuboid(x_length=1, y_length=3.5, z_length=1, stroke_width=0)
            pole.set_fill(color, opacity=0.75)

            pole_label = OpenGLTex(label)
            pole_label.shift(
                pole.get_height() * direction / 2 + pole.get_depth() * OUT / 2
            )
            pole.label = pole_label

            self.magnet_pole_labels.add(pole.label)
            self.magnet.add(pole)

        self.magnet.arrange(DOWN, buff=0)

    def construct(self):
        with RegisterFont("Merienda") as fonts:
            prompt = OpenGLText("Remember this experiment...?", font=fonts[0])
        prompt.to_corner(UL)
        prompt_bg = (
            BackgroundRectangle(prompt, GREY, 2, 1, 0.25, buff=0.25)
            .round_corners()
            .move_to(prompt)
        )

        self.play(FadeIn(self.field_background))
        self.wait(0.75)
        self.play(
            AnimationGroup(
                GrowFromPoint(prompt_bg, prompt_bg.get_left()),
                FadeIn(prompt, scale=1.25, lag_ratio=0.05),
                lag_ratio=0.15,
                run_time=2.0,
            )
        )
        self.wait(0.75)
        self.play(
            OpenGLGroup(prompt, prompt_bg).animate().scale(0.6).to_corner(UL, buff=0.25)
        )
        self.wait(0.25)
        self.play(
            LaggedStart(
                AnimationGroup(
                    *[
                        GrowFromPoint(pole, pole.get_edge_center(edge_dir))
                        for pole, edge_dir in zip(self.magnet, [DOWN, UP])
                    ]
                ),
                FadeIn(self.magnet_pole_labels, scale=1.35),
                lag_ratio=0.95,
                run_time=1.5,
            )
        )
        self.wait(0.25)
        self.play(Create(self.compass, lag_ratio=0, run_time=1))
        self.play(
            self.compass.point_at_angle_animation(
                angle_of_vector(self.field_func(self.compass.annulus.get_center())),
                run_time=1,
                rate_func=rate_functions.ease_out_elastic,
            )
        )
        self.wait()
        self.interactive_embed()

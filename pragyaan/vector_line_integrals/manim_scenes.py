from functions import *
from manim import *
from manim.opengl import *
from manim_fonts import RegisterFont
from manim_mobjects import *

from mini_projects.viviani_theorem.mobjects import Blob

NORTH_POLE_COLOR = MAROON_E
SOUTH_POLE_COLOR = BLUE_E
POLE_COLORS = [NORTH_POLE_COLOR, SOUTH_POLE_COLOR]


FIELD_BACKGROUND = OpenGLSurface(
    lambda u, v: [u, v, 0],
    [-10, 10],
    [-6, 6],
    color=DARK_GRAY,
    opacity=0.75,
    gloss=0.0,
    shadow=1.0,
)


class BarmagneticFieldScene(Scene):
    def setup(self):
        self.setup_magnet()

        self.compass = OpenGLMagneticCompass(
            annulus_kwargs=dict(stroke_color=np.tile([YELLOW_E, GREEN_E], 4)),
            include_shield=False,
            # would've loved to have it, but had to drop unfortunately due to some issues I don't understand.
            # shield_depth=0.5,
            # shield_kwargs=dict(color=DARK_GRAY, opacity=0.25, gloss=0.5, shadow=0.25),
        )
        self.compass.shift(4 * RIGHT)

        self.field_func = get_magnetic_field_func([(3 * UP, 1), (3 * DOWN, -1)])
        self.field = ArrowVectorField(
            self.field_func, delta_x=1, delta_y=1, length_func=lambda l: 0.5
        )

        self.spheres_at_vector_tails = self.get_spheres_at_vector_tails(
            self.field, gloss=0.5, shadow=0.25
        )

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

    @staticmethod
    def get_spheres_at_vector_tails(
        vectors: Iterable[OpenGLArrow], radius=0.10, color=GREY, **kwargs
    ):
        spheres = OpenGLGroup()
        for vect in vectors:
            sphere = OpenGLSphere(radius=radius, color=color, **kwargs)
            sphere.move_to(vect.get_start())
            spheres.add(sphere)
        return spheres


class RecollectBarMagneticField(BarmagneticFieldScene):
    def setup(self):
        super().setup()

    def construct(self):
        with RegisterFont("Merienda") as fonts:
            prompt = OpenGLText("Remember this experiment...?", font=fonts[0])
        prompt.to_corner(UL)
        prompt_bg = (
            BackgroundRectangle(prompt, GREY, 2, 1, 0.25, buff=0.25)
            .round_corners()
            .move_to(prompt)
        )

        self.play(FadeIn(FIELD_BACKGROUND))
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
            OpenGLGroup(prompt, prompt_bg).animate.scale(0.6).to_corner(UL, buff=0.25)
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
                self.compass.center_hinge.get_center(),
                self.field_func,
                run_time=1,
                rate_func=rate_functions.ease_out_elastic,
            ),
        )
        self.wait(0.75)
        self.play(FadeOut(OpenGLGroup(prompt, prompt_bg), shift=UP, run_time=0.35))

        self.show_field()
        # self.interactive_embed()

    def show_field(self):
        self.field.shift(0.05 * IN)  # how do you set z-index with OpenGLRenderer?

        self.play(
            LaggedStart(
                self.camera.animate(run_time=4)
                .scale(4 / 3)
                .set_euler_angles(theta=-5 * DEGREES, phi=50 * DEGREES),
                LaggedStartMap(GrowArrow, self.field, lag_ratio=0.15, run_time=4),
                lag_ratio=0.25,
            ),
        )

        self.camera.add_updater(lambda cam, dt: cam.increment_theta(dt * 0.025))
        self.add(self.camera)

        self.compass.add_updater(self.compass.pointer_updater_func(self.field_func))
        self.add(*self.compass)

        self.wait(0.5)

        compass_scale_factor = 0.5
        compass_path_radius = (
            self.magnet.get_height() / 2
            + compass_scale_factor * self.compass.annulus.outer_radius
            + 1
        )
        # compass_path = Blob(
        #     radius=compass_path_radius, min_scale=1.0, max_scale=1.35, n_samples=15
        # )
        compass_path = OpenGLCircle(radius=compass_path_radius)

        self.play(
            self.compass.animate()
            .scale(compass_scale_factor)
            .move_to(compass_path.get_points()[0])
        )
        self.play(
            MoveAlongPath(
                self.compass, compass_path, run_time=10, rate_func=double_smooth
            )
        )
        self.wait(0.25)

        self.play(
            AnimationGroup(
                LaggedStart(
                    *[
                        vect.animate(rate_func=there_and_back).scale(
                            0.25, about_point=vect.get_start()
                        )
                        for vect in self.field
                    ],
                    lag_ratio=0.025,
                    run_time=3.5,
                ),
                LaggedStart(
                    *[
                        GrowFromPoint(sph, sph.get_center())
                        for sph in self.spheres_at_vector_tails
                    ],
                    run_time=3.5,
                    lag_ratio=0.025,
                ),
                lag_ratio=0,
            )
        )
        self.wait(4)

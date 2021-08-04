"""
TODO: Figure out why this doesn't work when the unit_size of axes is altered
"""

from math import degrees as deg
from math import radians as rad

from manimlib import *

plane_config = dict(
    # replace with x_min = -15, x_max = 15 if using master branch
    x_range=(-15, 15),
    y_range=(-15, 15),
    axis_config={"stroke_width": 0.6},
)

z_axis_config = dict(
    include_numbers=True,
    include_ticks=True,
    line_to_number_buff=0.25,
    line_to_number_direction=UP,
    numbers_to_exclude=[0],
    unit_size=1,
)


class DemonstrateParametricSurfaces(ThreeDScene):
    CONFIG = {
        "plane_config": plane_config,
        "z_axis_config": z_axis_config,
        "x_range": (0, 1),
        "y_range": (0, 1),
        # no.of rects along x & y axes within the x and y range
        "resolution": (5, 5),
        "surface_rects_style": {
            "fill_opacity": 0.75,
            "stroke_opacity": 0.8,
            "stroke_width": 1,
        },
        "surface_gradient": (MAROON_D, GREEN_D, BLUE_D),
        "gloss": 0,
        "shadow": 0.5,
        "apply_function_kwargs": {"run_time": 10, "lag_ratio": 1},
    }

    def setup(self):
        self.setup_axes()
        self.setup_xy_space_rectangles()

    def setup_axes(self):
        plane = NumberPlane(**self.plane_config)
        z_axis = NumberLine(**self.z_axis_config).shift(plane.c2p(0, 0))
        z_axis.rotate_about_zero(axis=z_axis.get_unit_vector())
        z_axis.rotate_about_zero(axis=DOWN)
        if hasattr(z_axis, "numbers"):
            [num.rotate(PI / 2, UP) for num in z_axis.numbers]
        self.plane = plane
        self.z_axis = z_axis
        self.origin_sphere = Sphere(radius=0.12).move_to(plane.c2p(0, 0))

    def setup_xy_space_rectangles(self):
        surface_rects = VGroup()
        x_vals = np.linspace(*self.x_range, self.resolution[0], endpoint=False)
        y_vals = np.linspace(*self.y_range, self.resolution[1], endpoint=False)

        dx = x_vals[1] - x_vals[0]
        dy = y_vals[1] - y_vals[0]
        width = dx * self.plane.x_axis.unit_size
        height = dy * self.plane.y_axis.unit_size

        for x in x_vals:
            for y in y_vals:
                rect = Rectangle(width, height)
                rect.shift(self.plane.c2p(x + dx / 2, y + dy / 2))
                surface_rects.add(rect)

        surface_rects.set_style(**self.surface_rects_style)
        surface_rects.set_color_by_gradient(*self.surface_gradient)
        surface_rects.set_gloss(self.gloss).set_shadow(self.shadow)
        self.surface_rects = surface_rects

    def get_euler_angles_group(self):
        euler_angles = (
            VGroup(
                *[
                    DecimalNumber(deg(angle), num_decimal_places=1)
                    for angle in self.camera.frame.euler_angles
                ]
            )
            .arrange(DOWN)
            .to_corner(UR, buff=0.5)
        )
        euler_angles.fix_in_frame()
        return euler_angles

    def add_euler_angle_updaters(self, euler_angles):
        theta, phi, gamma = euler_angles
        frame = self.camera.frame

        # why doesn't this work in a loop? Add this method to source?
        theta.add_updater(lambda t: t.set_value(deg(frame.euler_angles[0])))
        phi.add_updater(lambda p: p.set_value(deg(frame.euler_angles[1])))
        gamma.add_updater(lambda g: g.set_value(deg(frame.euler_angles[2])))
        self.add(theta, phi, gamma)

    def c2p(self, x, y, z):
        point = np.zeros(3, dtype=float)
        axes = (*self.plane.axes, self.z_axis)
        for i, num, axis in zip((0, 1, 2), (x, y, z), axes):
            point[i] += axis.n2p(num)[i]
        return point

    def show_xy_space_rects(self, anim_style=FadeIn, **kwargs):
        self.play(AnimationGroup(*map(anim_style, self.surface_rects), **kwargs))

    def show_what_apply_function_does(self, added_anims=[], **kwargs):
        kwargs = dict(self.apply_function_kwargs, **kwargs)

        def func(rects):
            [r.apply_function(self.function) for r in rects]
            return rects

        self.play(
            AnimationGroup(
                ApplyFunction(func, self.surface_rects, lag_ratio=kwargs["lag_ratio"]),
                *added_anims,
                run_time=kwargs["run_time"]
            )
        )

    def function(self, point):
        return self.c2p(*self.parametric_function(point))

    def get_resolution_braces(self, brace_directions):
        return VGroup(
            *[
                BraceText(self.surface_rects, str(res), vect)
                for res, vect in zip(self.resolution, brace_directions)
            ]
        )

    def parametric_function(self, point):
        pass  # to be implemented in sub-class


class SphereDemo(DemonstrateParametricSurfaces):
    CONFIG = {
        "x_range": (0, PI),
        "y_range": (0, TAU),
        "resolution": (20, 40),
    }

    def construct(self):
        frame = self.camera.frame
        frame.shift(3 * UR)
        rects = self.surface_rects
        rects.save_state()
        res_braces = self.get_resolution_braces([DOWN, LEFT])
        ea = self.get_euler_angles_group()
        theta, phi, gamma = ea
        ea.scale(0.5).add_background_rectangle(buff=0.2).to_corner(UR)
        ea.fix_in_frame()

        gratitude = Tex("Thank you ", "Grant Sanderson", "!").scale(1.25)
        gratitude[1].set_color_by_gradient(BLUE_D, GREY_BROWN)
        gratitude.to_corner(UL).add_background_rectangle()
        gratitude.fix_in_frame()

        self.add_euler_angle_updaters([theta, phi, gamma])
        self.add(self.plane, ea)
        self.wait(5)
        # self.embed()  # activates interactive window, operated by ipython

    def parametric_function(self, point):
        x, y = point[:2]
        return np.array([np.cos(y) * np.sin(x), np.sin(y) * np.sin(x), np.cos(x)])


class SurfaceDemo(DemonstrateParametricSurfaces):
    CONFIG = {
        "x_range": (-4, 4),
        "y_range": (-4, 4),
        "resolution": (40, 40),
    }

    def construct(self):
        frame = self.camera.frame
        rects = self.surface_rects
        rects.save_state()
        res_braces = self.get_resolution_braces([DOWN, LEFT])
        ea = self.get_euler_angles_group()
        theta, phi, gamma = ea
        ea.scale(0.5).add_background_rectangle(buff=0.2).to_corner(UR)
        ea.fix_in_frame()

        self.add(self.plane, ea)
        self.add_euler_angle_updaters([theta, phi, gamma])
        self.wait(5)
        self.embed()

    @staticmethod
    def parametric_function(point):
        x, y = point[:2]
        return np.array([x, y, np.cos(y) * np.sin(x) + 3])

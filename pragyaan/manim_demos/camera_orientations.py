from math import degrees

from manimlib import *

plane = NumberPlane(
    x_range=(-10, 10),
    y_range=(-10, 10),
    background_line_style={"stroke_color": GREY},
    y_axis_config={
        "stroke_color": BLUE_E,
    },
    x_axis_config={
        "stroke_color": YELLOW,
    },
)


class CameraOrientations(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        colors = [MAROON_D, GREEN_E, PURPLE]
        tracker_texts = ["theta", "phi", "gamma"]

        tracker_groups = VGroup(
            *[
                VGroup(TexText(text + " ="), DecimalNumber(degrees(val)).scale(0.8))
                .arrange(RIGHT)
                .set_color(col)
                for text, val, col in zip(tracker_texts, frame.euler_angles, colors)
            ]
        ).arrange(1.5 * DOWN, aligned_edge=LEFT)
        # tracker_groups.fix_in_frame()

        for axis, label, point in zip(plane.axes, ["x", "y"], [RIGHT, UP]):
            vect = Vector(point)
            vect.add(Tex(label).next_to(vect, UR, buff=0))
            vect.set_color(axis.get_color())
            axis.add(vect)
            axis.vect = vect

        title = TexText("Euler Angles", " :")
        title[0].set_color_by_gradient(*colors)
        title.add(Underline(title[0]))
        title.next_to(tracker_groups, UP, aligned_edge=LEFT)

        group = VGroup(title, tracker_groups).to_corner(UL, 0.25)
        group.add_background_rectangle("#111111", buff=0.2)
        group.fix_in_frame()

        self.add(plane, group, title, Line3D(3 * IN, 3 * OUT, color=WHITE))
        self.wait(2)

        # why doesn't this work in a loop ??
        tracker_groups[0][-1].add_updater(
            lambda d: d.set_value(degrees(frame.euler_angles[0]))
        )
        tracker_groups[1][-1].add_updater(
            lambda d: d.set_value(degrees(frame.euler_angles[1]))
        )
        tracker_groups[2][-1].add_updater(
            lambda d: d.set_value(degrees(frame.euler_angles[2]))
        )

        self.play(frame.set_phi, 70 * DEGREES, run_time=6, rate_func=there_and_back)
        self.wait()
        self.play(frame.set_phi, -70 * DEGREES, run_time=6, rate_func=there_and_back)
        self.wait()
        self.play(frame.set_theta, 70 * DEGREES, run_time=6, rate_func=there_and_back)
        self.wait()
        self.play(frame.set_theta, -70 * DEGREES, run_time=6, rate_func=there_and_back)
        self.wait()
        self.play(frame.shift, 2 * DR, run_time=4, rate_func=there_and_back)
        self.wait()
        self.play(
            frame.set_theta, 45 * DEGREES, frame.set_phi, 45 * DEGREES, run_time=4
        )
        self.wait()
        self.play(frame.set_gamma, 60 * DEGREES, run_time=6, rate_func=there_and_back)
        self.wait()
        self.play(frame.set_gamma, -60 * DEGREES, run_time=6, rate_func=there_and_back)
        self.wait()
        self.play(frame.set_theta, 0, frame.set_phi, 0, run_time=2)
        self.wait()
        self.play(
            frame.set_theta,
            45 * DEGREES,
            frame.set_phi,
            45 * DEGREES,
            frame.set_gamma,
            45 * DEGREES,
            run_time=8,
            rate_func=there_and_back,
        )
        self.wait(4)

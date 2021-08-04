from manim.constants import TAU
from manim.mobject.geometry import Circle, Dot, Line


class LissajousCircle(Circle):
    def __init__(
        self,
        radius=1,
        speed=0.5,
        point_type=Dot,
        point_kwargs={},
        include_radius_line=True,
        radius_line_kwargs={},
        start_angle=0,
        **circle_kwargs
    ):
        circle_kwargs["radius"] = radius
        super().__init__(**circle_kwargs)

        self.speed = speed
        self.theta = start_angle
        self.include_radius_line = include_radius_line
        point = self.point_from_proportion(self.theta / TAU)
        self.dot = point_type(point=point, **point_kwargs)
        if include_radius_line:
            radius_line = Line(self.get_center(), point, **radius_line_kwargs)
            self.radius_line = radius_line
            self.add(radius_line)
        self.add(self.dot)

    def update_point(self, dt, speed=None):
        speed = speed or self.speed
        self.theta += speed * dt
        if self.theta > TAU:
            self.theta -= TAU
            self.cycle_incremented = (
                True  # not a good name for what this is meant for, change.
            )
        else:
            self.cycle_incremented = False
        self.dot.move_to(self.point_from_proportion(self.theta / TAU))
        if self.include_radius_line:
            self.radius_line.set_angle(self.theta)

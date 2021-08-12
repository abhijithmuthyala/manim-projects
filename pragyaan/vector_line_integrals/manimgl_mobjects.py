import numbers

import numpy as np
from manimlib.constants import LEFT, PI, RIGHT
from manimlib.mobject.geometry import Line
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.bezier import interpolate
from manimlib.utils.space_ops import rotate_vector


class Ground(VGroup):
    def __init__(
        self,
        length: float = 10,
        hash_lines_length: float = 0.25,
        hash_lines_angle: float = 5 * PI / 4,
        num_hash_lines: int = 20,
        ground_line_style: dict = None,
        hash_line_style: dict = None,
        **kwargs
    ):
        if ground_line_style is None:
            ground_line_style = {}

        ground = Line(**ground_line_style)
        ground.set_length(length)
        self.ground_line = ground
        super().__init__(ground, **kwargs)

        if hash_line_style is None:
            hash_line_style = ground.get_style()
            for key, value in hash_line_style.items():
                if isinstance(value, (numbers.Number, np.ndarray)):
                    hash_line_style[key] = value * 0.50

        hash_lines = self.get_hash_lines(
            hash_lines_angle, hash_lines_length, num_hash_lines, **hash_line_style
        )
        self.hash_lines = hash_lines
        self.add(hash_lines)

    def get_hash_lines(self, angle: float, length: float, n_lines: int, **style):
        hash_lines = VGroup()

        left_end, right_end = map(self.get_edge_center, [LEFT, RIGHT])
        for alpha in np.linspace(0, 1, n_lines, endpoint=True):
            start_point = interpolate(left_end, right_end, alpha)
            end_point = start_point + length * rotate_vector(RIGHT, angle)
            hash_lines.add(Line(start=start_point, end=end_point, **style))

        return hash_lines

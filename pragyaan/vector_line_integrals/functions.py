from typing import Callable

import numpy as np


# model the field as if it were generated by some electric charges.
# Superpose the field due to individual charges
def get_magnetic_field_func(charge_position_magnitude_pairs):
    def field_approx_func(point: np.array):
        vector = np.zeros(3)

        for charge_position, charge_magnitude in charge_position_magnitude_pairs:
            charge_to_point = point - charge_position
            point_distance = np.linalg.norm(charge_to_point)

            if point_distance < 0.1:
                continue
            else:
                charge_to_point /= point_distance ** 3
                charge_to_point *= charge_magnitude

            vector += charge_to_point

        return vector

    return field_approx_func


def get_compass_path(
    field_func: Callable[[np.ndarray], np.ndarray],
    starting_point: np.array,
    distance_along_vector: float = 0.25,
    distance_threshold: float = 0.1,
):
    path = [starting_point]
    point = starting_point

    while 1:
        vector = field_func(point)
        norm = np.linalg.norm(vector)
        point = point + (vector / norm) * distance_along_vector
        if len(path) > 1 and (abs(path[-1][0] - path[0][0]) < distance_threshold):
            break
        else:
            path.append(point)
    return path

from manimlib import *
from manimlib.scene.vector_space_scene import *


class IntroScene(LinearTransformationScene):

    CONFIG = {
        "include_background_plane": False,
        "include_foreground_plane": False,
        "show_coordinates": True,
        "background_line_style": {
            "stroke_width": 3,
        },
        "show_basis_vectors": False,
        "i_hat_color": "#d40b37",
        "j_hat_color": "#d4b90b",
        "back_basis_cols": [BLUE, GREEN],
        "fore_basis_cols": ["#d40b37", "#d4b90b"],
        "t_matrix": [[2, 1], [-1, 1]],
        "a_b_cols": [BLUE, GREEN],
        "det_col": YELLOW_D,
    }

    def construct(self):

        back_grid, fore_grid = self.background_plane, self.plane
        back_basis = self.get_basis_vectors(*self.back_basis_cols)
        fore_basis = self.get_basis_vectors(*self.fore_basis_cols)
        back_sq = self.get_unit_square().set_color_by_gradient(*self.back_basis_cols)
        fore_sq = self.get_unit_square().set_color_by_gradient(*self.fore_basis_cols)

        standard_basis_text = (
            Text("standard basis")
            .to_corner(UP + RIGHT)
            .set_color_by_gradient(*self.back_basis_cols)
        )
        trans_basis_text = (
            Text("transformed basis")
            .next_to(standard_basis_text, DOWN)
            .shift(0.3 * LEFT)
            .set_color_by_gradient(*self.fore_basis_cols)
        )

        back_mobs = VGroup(back_grid, back_basis, back_sq, standard_basis_text)
        fore_mobs = VGroup(fore_grid, fore_basis, fore_sq, trans_basis_text)

        goal = Text("Goal", color=MAROON).scale(2).to_edge(UP)
        arrow = (
            Vector(RIGHT, color=BLUE_D)
            .rotate(axis=IN, about_point=ORIGIN, angle=PI / 2)
            .next_to(goal, DOWN)
        )
        text = (
            Text("Visualize determinant of a composite matrix")
            .set_color_by_gradient(self.det_col, *self.a_b_cols)
            .set_width(FRAME_WIDTH - 2)
            .next_to(arrow, DOWN)
        )
        goals_group = VGroup(goal, arrow, text)

        context = (
            TexText("det(BA)", " = ", "det(B).det(A)")
            .set_width(FRAME_WIDTH - 2)
            .next_to(text, 2 * DOWN)
        )
        det_s = VGroup(context[0][:3], context[-1][:3], context[-1][7:10]).set_color(
            self.det_col
        )
        A_s = VGroup(context[0][-2], context[-1][-2])
        B_s = VGroup(context[0][-3], context[-1][4])
        A_s.set_color(self.a_b_cols[0])
        B_s.set_color(self.a_b_cols[1])
        context.add_background_rectangle(opacity=0.2, color=BLUE, buff=0.25)

        self.wait(3)
        self.play(Write(goal, lag_ratio=0.3), ShowCreation(arrow))
        self.play(Write(text), lag_ratio=0.3, run_time=2)
        self.wait()

        self.play(Write(context), lag_ratio=0.25, run_time=6)
        self.wait(2)
        self.play(FadeOut(context, lag_ratio=0.25), run_time=2)
        self.play(FadeOut(goals_group, lag_ratio=0.3), FadeIn(back_mobs))
        self.wait()

        self.play(
            GrowFromPoint(fore_basis, ORIGIN),
            GrowFromPoint(fore_sq, ORIGIN),
            FadeIn(fore_grid),
        )

        trans_matrix = Matrix(self.t_matrix).set_column_colors(*self.fore_basis_cols)
        self.moving_vectors += fore_basis
        self.transformable_mobjects += [fore_grid, fore_sq]
        self.move_matrix_columns(self.t_matrix, run_time=1.25)
        self.play(ShowCreation(trans_basis_text))
        self.wait()

        self.play(*[ApplyMethod(mob.fade, darkness=0.01) for mob in self.mobjects])
        grant = (
            ImageMobject("3b1b.png")
            .set_width(FRAME_WIDTH * 0.9)
            .set_height(FRAME_HEIGHT * 0.7)
        )
        eola = (
            Text("Essence Of Linear Algebra -", "3Blue1Brown")
            .set_width(FRAME_WIDTH - 1)
            .next_to(grant, UP)
        )
        eola.add_background_rectangle(buff=0.2)
        eola[1].set_color(TEAL_E)
        eola[2][0].set_color(BLUE_D)
        eola[2][5].set_color(GREY_BROWN)
        self.play(FadeIn(grant), ShowCreation(eola, lag_ratio=0.3), run_time=2)
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])


class AreasGettingScaled(LinearTransformationScene):

    CONFIG = {
        "show_coordinates": True,
        "background_line_style": {
            "stroke_width": 3,
        },
        "show_basis_vectors": False,
        "i_hat_color": BLUE,
        "j_hat_color": GREEN,
        "back_basis_cols": [BLUE, GREEN],
        "fore_basis_cols": ["#d40b37", "#d4b90b"],
        "t_matrix": [[2, 0], [1, 2]],
        "t_i_matrix": [[2, 0], [0, 1]],
        "t_j_matrix": [[1, 0], [1, 2]],
        "a_b_cols": [BLUE, GREEN],
        "det_col": YELLOW_D,
    }

    def construct(self):

        back_grid, fore_grid = self.background_plane, self.plane
        back_basis = self.get_basis_vectors(*self.back_basis_cols)
        fore_basis = self.get_basis_vectors(*self.fore_basis_cols)
        back_sq = self.get_unit_square().set_color_by_gradient(*self.back_basis_cols)
        fore_sq = self.get_unit_square().set_color_by_gradient(*self.fore_basis_cols)

        fore_mobs = VGroup(fore_grid, fore_sq, fore_basis)
        back_mobs = VGroup(back_grid, back_basis, back_sq)

        standard_basis_text = (
            Text("standard basis")
            .to_corner(UP + RIGHT)
            .set_color_by_gradient(*self.back_basis_cols)
        )
        trans_basis_text = (
            Text("transformed basis")
            .next_to(standard_basis_text, DOWN)
            .shift(0.3 * LEFT)
            .set_color_by_gradient(*self.fore_basis_cols)
        )

        self.add(back_grid, back_basis, back_sq, standard_basis_text)
        self.wait()

        a_equals = Text("A", "=")
        a_equals[0].set_color(self.a_b_cols[0]).scale(1.5)
        matrix = (
            Matrix(
                np.array(self.t_matrix).transpose(), include_background_rectangle=True
            )
            .scale(0.75)
            .set_column_colors(*self.fore_basis_cols)
        )
        a_matrix = VGroup(a_equals, matrix).arrange_submobjects().shift(UP + 2 * LEFT)

        self.play(
            Write(a_equals), FadeIn(matrix.background_rectangle), Write(matrix.brackets)
        )
        self.wait()
        self.play(Write(matrix.get_columns()[0]))
        self.wait(0.5)
        self.play(Write(matrix.get_columns()[1]))
        self.wait()

        self.moving_vectors += fore_basis
        self.transformable_mobjects += [fore_grid, fore_sq]

        self.play(*[GrowFromPoint(mob, ORIGIN) for mob in fore_mobs[1:]])
        self.wait()

        self.remove(fore_basis, fore_grid)
        self.play(WiggleOutThenIn(back_basis[0]))
        self.add(fore_basis, fore_grid)
        self.apply_transposed_matrix(
            self.t_i_matrix,
            run_time=1.2,
            added_anims=[
                ShowCreationThenFadeAround(matrix.get_columns()[0], opacity=0.5)
            ],
        )
        self.wait(0.25)
        self.remove(*self.moving_vectors, fore_grid)
        self.play(WiggleOutThenIn(back_basis[1]))
        self.add(fore_grid, fore_basis)
        self.apply_transposed_matrix(
            self.t_j_matrix,
            run_time=1.2,
            added_anims=[ShowCreationThenFadeAround(matrix.get_columns()[1])],
        )
        self.play(Write(trans_basis_text, lag_ratio=0.3))
        self.wait()

        self.wait(3)
        self.play(ApplyWave(back_sq, amplitude=0.5), run_time=2)
        self.play(ApplyWave(fore_sq, amplitude=0.5), run_time=2)
        self.wait()

        self.play(
            ApplyMethod(a_matrix.to_corner, UP + LEFT),
            FadeOut(standard_basis_text),
            FadeOut(trans_basis_text),
        )
        self.play(
            ApplyMethod(back_sq.shift, 4 * LEFT),
            ApplyMethod(back_basis.shift, 4 * LEFT),
        )

        curved_arrow = CurvedArrow(
            back_sq.get_right() + 0.2 * RIGHT,
            fore_sq.get_left() + 0.2 * RIGHT,
            angle=-PI / 4,
        )
        question_mark = Text("X ?").set_color(self.det_col).next_to(curved_arrow, UP)
        question_mark[0][0].set_color(WHITE)
        scaled_area = VGroup(curved_arrow, question_mark)
        self.play(ShowCreation(scaled_area))
        self.wait(4)

        fade_mobs = [back_grid, fore_grid]
        self.play(*[ApplyMethod(mob.fade, darkness=0.1) for mob in fade_mobs])

        transformed_rect = Polygon(
            ORIGIN,
            [0.5, 1, 0],
            [1.5, 1, 0],
            [1, 0, 0],
            stroke_color=back_sq.get_stroke_color(),
            fill_color=back_sq.get_fill_color(),
            fill_opacity=back_sq.get_fill_opacity(),
        )
        transformed_rects = [
            transformed_rect,
            transformed_rect.copy().shift(RIGHT),
            transformed_rect.copy().shift(UP + 0.5 * RIGHT),
            transformed_rect.copy().shift(UP + 1.5 * RIGHT),
        ]

        for index, rect in enumerate(transformed_rects):
            factor = (
                Text(f"{index+1}", color=self.det_col)
                .scale(1.5)
                .next_to(question_mark[0][0])
            )
            self.play(
                TransformFromCopy(back_sq, rect), Transform(question_mark[0][1], factor)
            )
            self.wait(0.5)

        self.wait()

        det_a = TexText("det(A)", " = ").scale(1.5).next_to(a_matrix, 2 * RIGHT)
        det_a[0][:3].set_color(self.det_col)
        det_a[0][4].set_color(self.a_b_cols[0])
        self.play(Write(det_a))
        self.play(ApplyMethod(factor.copy().next_to, det_a, RIGHT))
        self.wait(3)


class AnyAreaScalesBySameFactor(LinearTransformationScene):

    CONFIG = {
        "include_background_plane": False,
        "include_foreground_plane": False,
        "show_coordinates": True,
        "background_line_style": {
            "stroke_width": 3,
        },
        "show_basis_vectors": False,
        "i_hat_color": "#d40b37",
        "j_hat_color": "#d4b90b",
        "back_basis_cols": [BLUE, GREEN],
        "fore_basis_cols": ["#d40b37", "#d4b90b"],
        "t_matrix": [[2, 0], [1, 2]],
        "t_i_matrix": [[2, 0], [0, 1]],
        "t_j_matrix": [[1, 0], [1, 2]],
        "a_b_cols": [BLUE, GREEN],
        "det_col": YELLOW_D,
    }

    def construct(self):

        back_grid, fore_grid = self.background_plane, self.plane
        back_basis = self.get_basis_vectors(*self.back_basis_cols)
        fore_basis = back_basis.copy()
        back_sq = self.get_unit_square().set_color_by_gradient(*self.back_basis_cols)
        fore_sq = back_sq.copy()

        # some transformable mobjects
        back_circ = (
            Circle(fill_color=TEAL_E, fill_opacity=0.3)
            .scale(0.75)
            .move_to(2 * LEFT + UP)
        )
        fore_circ = back_circ.copy()
        back_vects = VGroup(Vector(RIGHT + DOWN), Vector(LEFT + DOWN))
        back_vect_rect = Polygon(
            ORIGIN,
            RIGHT + DOWN,
            2 * DOWN,
            LEFT + DOWN,
            fill_color=TEAL_E,
            fill_opacity=0.3,
        )
        fore_vects = back_vects.copy()
        fore_vect_rect = back_vect_rect.copy()

        self.add_background_mobject(
            back_grid, back_sq, back_basis, back_circ, back_vects, back_vect_rect
        )
        self.add_foreground_mobjects(
            fore_grid, fore_basis, fore_sq, fore_circ, fore_vects, fore_vect_rect
        )

        self.moving_vectors += [*fore_basis, *fore_vects]
        self.transformable_mobjects += [fore_grid, fore_sq, fore_circ, fore_vect_rect]

        self.wait(2)
        self.apply_transposed_matrix(self.t_matrix)
        self.wait()

        fade_out_mobs = [
            back_grid,
            fore_grid,
            fore_basis,
            back_basis,
            back_vects,
            fore_vects,
        ]
        self.play(*[FadeOut(mob) for mob in fade_out_mobs])
        self.wait()

        self.play(
            ApplyMethod(back_sq.move_to, 2.5 * UP),
            ApplyMethod(fore_sq.move_to, -1.5 * UP),
            ApplyMethod(back_circ.move_to, 4 * LEFT + 2.5 * UP),
            ApplyMethod(fore_circ.move_to, 4 * LEFT - 1.5 * UP),
            ApplyMethod(back_vect_rect.move_to, -4 * LEFT + 2.5 * UP),
            ApplyMethod(fore_vect_rect.move_to, -4 * LEFT - 1.5 * UP),
        )

        self.wait()

        arrow = (
            Vector().rotate(axis=IN, angle=PI / 2).next_to(back_sq, DOWN).scale(1.25)
        )
        scale_factor = Text("X 4").next_to(arrow)
        det = VGroup(arrow, scale_factor)

        self.play(ShowCreation(det))
        self.wait()
        self.play(
            TransformFromCopy(det, det.copy().next_to(back_circ, DOWN)),
            TransformFromCopy(det, det.copy().next_to(back_vect_rect, DOWN)),
        )

        self.wait(4)

        self.play(*[FadeOut(mob) for mob in self.mobjects])


class PropertyOfLinTrans(LinearTransformationScene):

    CONFIG = {"t_i_matrix": [[2, 0], [0, 1]], "t_j_matrix": [[1, 0], [1, 2]]}

    def construct(self):

        inherent_props = (
            Text("Linear Transformations : ").set_color(TEAL_E).to_corner(UP + LEFT)
        )
        prop1 = Text("1. Keep grid lines parallel and evenly spaced").scale(0.75)
        prop2 = Text("2. Fix origin in place").scale(0.75)
        props = (
            VGroup(prop1, prop2)
            .arrange_submobjects(DOWN, aligned_edge=LEFT)
            .next_to(inherent_props, 2 * DOWN, aligned_edge=LEFT)
        )
        lin_trans = VGroup(inherent_props, props).add_background_rectangle(buff=0.2)

        self.add(lin_trans)

        self.wait()
        self.apply_transposed_matrix(self.t_i_matrix)
        self.wait(0.5)
        self.apply_transposed_matrix(self.t_j_matrix)
        self.wait(3)


class DeterminantOfMatrixB(LinearTransformationScene):

    CONFIG = {
        "show_coordinates": True,
        "background_line_style": {
            "stroke_width": 3,
        },
        "show_basis_vectors": False,
        "i_hat_color": BLUE,
        "j_hat_color": GREEN,
        "back_basis_cols": [BLUE, GREEN],
        "fore_basis_cols": ["#d40b37", "#d4b90b"],
        "t_matrix": [[2, 0], [-1, 1]],
        "t_i_matrix": [[2, 0], [0, 1]],
        "t_j_matrix": [[1, 0], [-1, 1]],
        "a_b_cols": [BLUE, GREEN],
        "det_col": YELLOW_D,
    }

    def construct(self):

        back_grid, fore_grid = self.background_plane, self.plane
        back_basis = self.get_basis_vectors(*self.back_basis_cols)
        fore_basis = self.get_basis_vectors(*self.fore_basis_cols)
        back_sq = self.get_unit_square().set_color_by_gradient(*self.back_basis_cols)
        fore_sq = self.get_unit_square().set_color_by_gradient(*self.fore_basis_cols)

        fore_mobs = VGroup(fore_grid, fore_sq, fore_basis)
        back_mobs = VGroup(back_grid, back_basis, back_sq)

        standard_basis_text = (
            Text("standard basis")
            .to_corner(UP + RIGHT)
            .set_color_by_gradient(*self.back_basis_cols)
        )
        trans_basis_text = (
            Text("transformed basis")
            .next_to(standard_basis_text, DOWN)
            .shift(0.3 * LEFT)
            .set_color_by_gradient(*self.fore_basis_cols)
        )

        self.add(back_grid, back_basis, back_sq, standard_basis_text)
        self.wait()

        b_equals = Text("B", "=")
        b_equals[0].set_color(self.a_b_cols[1]).scale(1.5)
        matrix = (
            Matrix(
                np.array(self.t_matrix).transpose(), include_background_rectangle=True
            )
            .scale(0.75)
            .set_column_colors(*self.fore_basis_cols)
        )
        b_matrix = VGroup(b_equals, matrix).arrange_submobjects().shift(UP + 4 * LEFT)

        self.play(
            Write(b_equals), FadeIn(matrix.background_rectangle), Write(matrix.brackets)
        )
        self.wait()
        self.play(Write(matrix.get_columns()[0]))
        self.play(Write(matrix.get_columns()[1]))
        self.wait()

        self.moving_vectors += fore_basis
        self.transformable_mobjects += [fore_grid, fore_sq]

        self.play(*[GrowFromPoint(mob, ORIGIN) for mob in fore_mobs[1:]])

        self.remove(fore_basis, fore_grid)
        self.play(WiggleOutThenIn(back_basis[0]))
        self.add(fore_basis, fore_grid)
        self.apply_transposed_matrix(
            self.t_i_matrix,
            run_time=1,
            added_anims=[
                ShowCreationThenFadeAround(matrix.get_columns()[0], opacity=0.5)
            ],
        )
        self.remove(*self.moving_vectors, fore_grid)
        self.play(WiggleOutThenIn(back_basis[1]))
        self.add(fore_grid, fore_basis)
        self.apply_transposed_matrix(
            self.t_j_matrix,
            run_time=1,
            added_anims=[ShowCreationThenFadeAround(matrix.get_columns()[1])],
        )
        self.play(Write(trans_basis_text, lag_ratio=0.3))
        self.wait()

        self.play(ApplyWave(back_sq, amplitude=0.5), run_time=2)
        self.play(ApplyWave(fore_sq, amplitude=0.5), run_time=2)
        self.wait()

        self.play(
            ApplyMethod(b_matrix.to_corner, UP + LEFT),
            FadeOut(standard_basis_text),
            FadeOut(trans_basis_text),
            ApplyMethod(back_sq.shift, 4 * LEFT),
            ApplyMethod(back_basis.shift, 4 * LEFT),
        )

        curved_arrow = CurvedArrow(
            back_sq.get_right() + 0.2 * RIGHT,
            fore_sq.get_left() + 0.2 * LEFT,
            angle=-PI / 4,
        )
        question_mark = Text("X ?").set_color(self.det_col).next_to(curved_arrow, UP)
        question_mark[0][0].set_color(WHITE)
        scaled_area = VGroup(curved_arrow, question_mark)
        self.play(ShowCreation(scaled_area))

        fade_mobs = [back_grid, fore_grid]
        self.play(*[ApplyMethod(mob.fade, darkness=0.1) for mob in fade_mobs])

        transformed_rect = Polygon(
            ORIGIN,
            [-0.5, 0.5, 0],
            [1.5, 0.5, 0],
            [2, 0, 0],
            stroke_color=back_sq.get_stroke_color(),
            fill_color=back_sq.get_fill_color(),
            fill_opacity=back_sq.get_fill_opacity(),
        )
        transformed_rects = [
            transformed_rect,
            transformed_rect.copy().shift(0.5 * (UP + LEFT)),
        ]

        for index, rect in enumerate(transformed_rects):
            factor = (
                Text(f"{index+1}", color=self.det_col)
                .scale(1.5)
                .next_to(question_mark[0][0])
                .add_background_rectangle()
            )
            self.play(
                TransformFromCopy(back_sq, rect), Transform(question_mark[0][1], factor)
            )
            self.wait(0.5)

        det_b = TexText("det(B)", " = ").scale(1.5).next_to(b_matrix, 2 * RIGHT)
        det_b[0][:3].set_color(self.det_col)
        det_b[0][4].set_color(self.a_b_cols[0])
        self.play(Write(det_b))
        self.play(ApplyMethod(factor.copy().next_to, det_b, RIGHT))
        self.wait(3)

        fade_mobs = [mob for mob in self.mobjects if mob is not back_grid]
        for mob in fade_mobs:
            mob.fade(0.5)

        self.play(ApplyWave(back_grid, amplitude=2), run_time=2)
        self.wait()


class WhatMatrixMultipilcationIs(LinearTransformationScene):

    CONFIG = {
        "include_background_plane": True,
        "include_foreground_plane": True,
        "background_plane_kwargs": {
            "background_line_style": {
                "stroke_width": 2,
            },
        },
        "show_coordinates": True,
        "show_basis_vectors": True,
        "show_unit_square": False,
        "a_mat": np.array([[2, 0], [1, 2]]),
        "b_mat": np.array([[2, 0], [-1, 1]]),
        "back_basis_cols": [BLUE, GREEN],
        "fore_basis_cols": ["#d40b37", "#d4b90b"],
        "a_b_cols": [BLUE, GREEN],
        "det_col": YELLOW_D,
        "i_hat_color": BLUE,
        "j_hat_color": GREEN,
    }

    def construct(self):

        back_grid, fore_grid = self.background_plane, self.plane

        # matrices a and b

        b_equals = Text("B =").scale(1.25)
        b_equals[0][0].set_color(self.a_b_cols[1])
        b_mat = (
            Matrix(self.b_mat.transpose(), include_background_rectangle=True)
            .set_column_colors(*self.back_basis_cols)
            .scale(0.75)
        )
        matrix_b = VGroup(b_equals, b_mat).arrange_submobjects().to_corner(UP + LEFT)

        a_equals = Text("A =").scale(1.25)
        a_equals[0][0].set_color(self.a_b_cols[0])
        a_mat = (
            Matrix(self.a_mat.transpose(), include_background_rectangle=True)
            .set_column_colors(*self.fore_basis_cols)
            .scale(0.75)
        )
        matrix_a = VGroup(a_equals, a_mat).arrange_submobjects().next_to(matrix_b)

        self.wait(2)
        self.add(matrix_b, matrix_a)
        self.wait()

        # bring mat's next to each other
        self.play(
            FadeOut(a_equals),
            FadeOut(b_equals),
            ApplyMethod(b_mat.to_corner, UP + LEFT),
        )
        self.play(ApplyMethod(a_mat.next_to, b_mat, buff=0.2))

        equals = Text("=").next_to(a_mat)
        dummy_matrix = (
            Matrix([[0, 0], [0, 0]], include_background_rectangle=True)
            .scale(0.75)
            .next_to(equals)
        )

        self.play(
            Write(equals),
            FadeIn(dummy_matrix.background_rectangle),
            Write(dummy_matrix.brackets),
        )
        self.wait(2)

        # show transformation
        self.add_transformable_mobject(fore_grid)
        text1 = (
            Text("Where do the basis vectors defined by A land on,")
            .next_to(b_equals, 2.5 * DOWN, aligned_edge=LEFT)
            .shift(3 * DOWN)
            .add_background_rectangle()
        )
        text2 = (
            Text("during the transformation B ?")
            .next_to(text1, DOWN, aligned_edge=LEFT)
            .add_background_rectangle()
        )
        text = VGroup(text1, text2).add_background_rectangle(buff=0.5)

        v1 = Vector(2 * RIGHT, color=self.fore_basis_cols[0])
        v2 = Vector(RIGHT + 2 * UP, color=self.fore_basis_cols[1])
        vects = VGroup(v1, v2)
        self.moving_vectors += [*vects]

        self.play(
            Write(text1),
            TransformFromCopy(a_mat, v1),
            TransformFromCopy(a_mat, v2),
            run_time=3,
        )
        self.wait(0.5)
        self.apply_transposed_matrix(self.b_mat, run_time=2, added_anims=[Write(text2)])
        self.wait()

        v1_landing_label = vector_coordinate_label(v1).next_to(v1)
        v2_landing_label = vector_coordinate_label(v2).next_to(
            v2, 0.4 * UP + 0.5 * RIGHT
        )
        for i, label in enumerate([v1_landing_label, v2_landing_label]):
            label.elements.set_color(self.fore_basis_cols[i])
        self.play(Write(v1_landing_label), GrowFromCenter(v2_landing_label))
        self.wait()

        v1_land_numbers = [num for num in v1_landing_label.copy().elements]
        v1_locs = [
            num.get_center()
            for num in [element for element in dummy_matrix.elements[::2]]
        ]

        v2_land_numbers = [num for num in v2_landing_label.copy().elements]
        v2_locs = [
            num.get_center()
            for num in [element for element in dummy_matrix.elements[1::2]]
        ]
        self.play(
            *[
                ApplyMethod(num.move_to, loc)
                for num, loc in zip(v1_land_numbers, v1_locs)
            ],
            *[
                ApplyMethod(num.move_to, loc)
                for num, loc in zip(v2_land_numbers, v2_locs)
            ],
            lag_ratio=1,
        )

        self.wait(3)
        self.play(FadeOut(v1_landing_label), FadeOut(v2_landing_label))
        # self.wait(3)


class ScaleFactorOfTransformingBasis(LinearTransformationScene):

    CONFIG = {
        "include_background_plane": True,
        "include_foreground_plane": True,
        "background_plane_kwargs": {
            "background_line_style": {
                "stroke_width": 1,
            },
        },
        "show_coordinates": True,
        "show_basis_vectors": False,
        "show_unit_square": False,
        "a_mat": np.array([[2, 0], [1, 2]]),
        "b_mat": np.array([[2, 0], [-1, 1]]),
        "back_basis_cols": [BLUE, GREEN],
        "fore_basis_cols": ["#d40b37", "#d4b90b"],
        "a_b_cols": [BLUE, GREEN],
        "det_col": YELLOW_D,
        "i_hat_color": BLUE,
        "j_hat_color": GREEN,
        "prod_mat": np.array([[4, 0], [0, 2]]),
    }

    def construct(self):

        back_grid, fore_grid = self.background_plane, self.plane
        back_sq = self.get_unit_square().set_color_by_gradient(*self.back_basis_cols)
        fore_sq = self.get_unit_square().set_color_by_gradient(*self.fore_basis_cols)
        back_basis = self.get_basis_vectors(*self.back_basis_cols)
        fore_basis = VGroup(
            Vector(2 * RIGHT, color=self.fore_basis_cols[0]),
            Vector(RIGHT + 2 * UP, color=self.fore_basis_cols[1]),
        )

        a_mat = (
            Matrix(self.b_mat.transpose(), include_background_rectangle=True)
            .scale(0.75)
            .to_corner(UP + LEFT, buff=0.3)
            .set_column_colors(*self.fore_basis_cols)
        )

        back_mobs = [back_grid, back_sq, *back_basis]
        fore_mobs = [fore_grid, fore_sq, *fore_basis]

        # apply the matrix a
        func = self.get_transposed_matrix_transformation(self.a_mat)
        for mob in fore_mobs[:2]:
            mob.apply_function(func)

        # copy mobjects --> use as transforming mobjects
        back_mobs_copy = VGroup(back_sq.copy(), back_basis.copy())
        fore_mobs_copy = VGroup(fore_sq.copy(), fore_basis.copy())

        self.moving_vectors += [*back_mobs_copy[1], *fore_mobs_copy[1]]
        self.transformable_mobjects += [back_mobs_copy[0], fore_mobs_copy[0], fore_grid]

        self.add(*back_mobs, *fore_mobs, *back_mobs_copy, *fore_mobs_copy, a_mat)
        self.wait()

        self.apply_transposed_matrix(self.b_mat, run_time=2)
        self.wait()

        back_squares = [back_sq, back_mobs_copy[0]]
        fore_squares = [fore_sq, fore_mobs_copy[0]]
        back_vects = [back_basis, back_mobs_copy[1]]
        fore_vects = [fore_basis, fore_mobs_copy[1]]

        self.play(
            *[
                ApplyMethod(mob.fade, darkness=1)
                for mob in self.mobjects
                if mob not in [*back_squares, *fore_squares, *back_vects, *fore_vects]
            ],
            *[
                ApplyMethod(mob.shift, 4.5 * LEFT + 1.25 * UP)
                for mob in [back_sq, *back_basis]
            ],
            *[
                ApplyMethod(mob.shift, 5.5 * LEFT - 2 * UP)
                for mob in [fore_sq, *fore_basis]
            ],
            *[
                ApplyMethod(mob.shift, RIGHT + 1.25 * UP)
                for mob in [back_mobs_copy[0], *back_mobs_copy[1]]
            ],
            *[
                ApplyMethod(mob.shift, -2 * UP)
                for mob in [fore_mobs_copy[0], *fore_mobs_copy[1]]
            ],
        )
        self.wait()

        # show scale factors
        rect1 = Polygon(
            RIGHT + 1.25 * UP,
            1.75 * UP + 0.5 * RIGHT,
            1.75 * UP + 2.5 * RIGHT,
            3 * RIGHT + 1.25 * UP,
        ).set_style(
            fill_opacity=back_sq.get_fill_opacity(), fill_color=back_sq.get_fill_color()
        )
        trans_rects1 = [rect1, rect1.copy().shift(0.5 * UP + 0.5 * LEFT)]

        factor = VGroup(
            Vector(1.5 * RIGHT, color=WHITE).shift(2.5 * LEFT + 1.65 * UP),
            Text("X 2").move_to(2 * LEFT + 2 * UP),
        )
        factor[1][0][1].set_color(YELLOW)
        factor_copy = factor.copy().shift(3 * DOWN)

        rect2 = Polygon(
            ORIGIN,
            2 * RIGHT,
            2 * RIGHT + 2 * DOWN,
            2 * DOWN,
            fill_color=fore_sq.get_fill_color(),
            fill_opacity=fore_sq.get_fill_opacity(),
        )
        trans_rects2 = [rect2, rect2.copy().shift(2 * RIGHT)]
        q_mark = Text("X ?").next_to(factor_copy[0], UP)

        self.play(ShowCreation(factor_copy[0]), Write(q_mark))
        self.wait(3)

        for rect in trans_rects1:
            self.play(TransformFromCopy(back_sq, rect))
            self.wait(0.5)
        self.play(Write(factor))
        self.wait(3)

        self.play(
            Transform(
                q_mark[0][-1],
                Text("2", color=YELLOW).move_to(q_mark[0][1].get_center()),
            )
        )
        self.wait()

        for rect in trans_rects2:
            self.play(TransformFromCopy(fore_sq, rect))
            self.wait(0.5)
        self.wait()

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=2, lag_ratio=0.3)


class FateOfUnitArea(LinearTransformationScene):

    CONFIG = {
        "include_background_plane": False,
        "include_foreground_plane": False,
        "background_plane_kwargs": {
            "background_line_style": {
                "stroke_width": 2,
            },
        },
        "show_coordinates": True,
        "show_basis_vectors": False,
        "show_unit_square": False,
        "a_mat": np.array([[2, 0], [1, 2]]),
        "b_mat": np.array([[2, 0], [-1, 1]]),
        "back_basis_cols": [BLUE, GREEN],
        "fore_basis_cols": ["#d40b37", "#d4b90b"],
        "a_b_cols": [BLUE, GREEN],
        "det_col": YELLOW_D,
        "i_hat_color": BLUE,
        "j_hat_color": GREEN,
        "prod_mat": np.array([[4, 0], [0, 2]]),
    }

    def construct(self):

        back_grid, fore_grid = self.background_plane, self.plane
        back_sq = self.get_unit_square().set_color_by_gradient(*self.back_basis_cols)
        fore_sq = self.get_unit_square().set_color_by_gradient(*self.back_basis_cols)
        back_basis = self.get_basis_vectors(*self.back_basis_cols)

        b_mat = (
            Matrix(self.b_mat.transpose(), include_background_rectangle=True)
            .scale(0.75)
            .set_column_colors(*self.fore_basis_cols)
            .to_corner(UP + LEFT)
        )
        a_mat = (
            Matrix(self.a_mat.transpose(), include_background_rectangle=True)
            .scale(0.75)
            .set_column_colors(*self.fore_basis_cols)
            .next_to(b_mat)
        )
        b_text = Text("B").next_to(b_mat, DOWN).set_color(self.a_b_cols[1])
        a_text = Text("A").next_to(a_mat, DOWN).set_color(self.a_b_cols[0])
        det_a = TexText("det(A) = 4").next_to(b_mat, 3.5 * DOWN + 0.1 * RIGHT)
        det_b = TexText("det(B) = 2").next_to(det_a, DOWN)
        det_a[0][:3].set_color(self.det_col)
        det_a[0][-1].set_color(self.det_col)
        det_a[0][4].set_color(self.a_b_cols[0])

        det_b[0][:3].set_color(self.det_col)
        det_b[0][-1].set_color(self.det_col)
        det_b[0][4].set_color(self.a_b_cols[1])

        stan_basis = VGroup(back_basis, back_sq)

        # copies get transformed
        back_sq_copy1 = back_sq.copy()
        back_basis_copy1 = back_basis.copy()

        self.moving_vectors += [*back_basis_copy1]
        self.transformable_mobjects += [fore_grid, back_sq_copy1]

        self.add(
            back_grid,
            fore_grid,
            back_basis,
            back_sq,
            b_mat,
            b_text,
            a_mat,
            a_text,
            det_a,
            det_b,
        )
        self.wait(4)
        self.play(ApplyWave(back_sq), amplitude=0.5)
        self.wait()

        self.apply_transposed_matrix(
            self.a_mat, run_time=1.5, added_anims=[Indicate(a_mat, scale_factor=1.1)]
        )
        self.wait(0.5)

        int_basis = VGroup(back_basis_copy1, back_sq_copy1)

        back_sq_copy2 = back_sq_copy1.copy()
        back_basis_copy2 = back_basis_copy1.copy()
        self.add(back_basis_copy2, back_sq_copy2)

        self.apply_transposed_matrix(
            self.b_mat, run_time=1.5, added_anims=[Indicate(b_mat, scale_factor=1.1)]
        )
        self.wait()
        self.add(back_basis_copy2)

        final_basis = VGroup(back_basis_copy2, back_sq_copy2)

        # bases = VGroup(stan_basis,int_basis,final_basis).arrange_submobjects(1.5*RIGHT)
        back_rect = Rectangle(
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            stroke_color=BLACK,
            fill_color=BLACK,
            fill_opacity=0.3,
        )

        self.play(
            FadeIn(back_rect),
            ApplyMethod(back_grid.fade, darkness=0.75),
            ApplyMethod(fore_grid.fade, darkness=0.75),
            ApplyMethod(stan_basis.move_to, 5 * LEFT + 1.5 * DOWN),
            ApplyMethod(final_basis.move_to, LEFT + 1.5 * DOWN),
            ApplyMethod(int_basis.move_to, 4 * RIGHT + 1.5 * DOWN),
        )
        self.wait()

        # what started off as a unit area...

        arrow_a = Arrow(
            back_sq.get_right() + 0.05 * RIGHT, back_sq_copy2.get_left() + 0.05 * LEFT
        )
        factor_a_copy = det_a[0][-1].copy().next_to(arrow_a, UP)
        cross_a = Text("X").next_to(factor_a_copy, LEFT, buff=0.15).scale(0.75)
        a = a_text.copy().next_to(arrow_a, DOWN)

        self.play(ApplyWave(back_sq), amplitude=0.5)
        self.wait(0.5)
        self.play(ShowCreation(arrow_a), Write(cross_a), Write(a))

        self.play(Flash(det_a[0][-1], radius=1))
        self.play(TransformFromCopy(det_a[0][-1], factor_a_copy))
        self.wait()

        arrow_b = Arrow(
            back_sq_copy2.get_right(), back_sq_copy1.get_left() + 0.05 * LEFT
        )
        factor_b_copy = det_b[0][-1].copy().next_to(arrow_b, UP)
        cross_b = Text("X").next_to(factor_b_copy, LEFT, buff=0.15).scale(0.75)
        b = b_text.copy().next_to(arrow_b, DOWN)

        self.play(ApplyWave(back_sq_copy2), amplitude=0.5)
        self.wait(0.5)
        self.play(ShowCreation(arrow_b), Write(cross_b), Write(b))

        self.play(Flash(det_b[0][-1], radius=1, color=WHITE))
        self.play(TransformFromCopy(det_b[0][-1], factor_b_copy))
        self.wait(3)

        det_ab = (
            TexText("det(BA) = det(B) X det(A)", include_background_rectangle=True)
            .scale(1.3)
            .move_to(3 * RIGHT + 2.5 * UP)
        )
        det_ab[0][14].scale(0.5)

        det_indices = [0, 1, 2, 8, 9, 10, 15, 16, 17]
        b_indices = [4, 12]
        a_indices = [5, -2]
        for i in det_indices:
            det_ab[0][i].set_color(self.det_col)
        for i in a_indices:
            det_ab[0][i].set_color(self.a_b_cols[0])
        for i in b_indices:
            det_ab[0][i].set_color(self.a_b_cols[1])

        self.play(ApplyWave(back_sq_copy1, amplitude=0.5))
        self.wait(2)
        self.play(TransformFromCopy(back_sq_copy1, det_ab[0][:8]))
        self.wait(2.5)

        factor_b_copy2 = factor_b_copy.copy().next_to(det_ab[0][7], buff=1)
        cross_copy = cross_a.copy().next_to(factor_b_copy2, buff=1)
        factor_a_copy2 = factor_a_copy.copy().next_to(cross_copy, buff=1)

        self.play(TransformFromCopy(factor_a_copy, factor_a_copy2))
        self.play(Write(cross_copy))
        self.play(TransformFromCopy(factor_b_copy, factor_b_copy2))
        self.wait(2)

        deter_a = TexText("det(A)").move_to(factor_a_copy2.get_center()).scale(1.3)
        deter_b = TexText("det(B)").move_to(factor_b_copy2.get_center()).scale(1.3)
        deter_a[0][:3].set_color(self.det_col)
        deter_b[0][:3].set_color(self.det_col)
        deter_a[0][-2].set_color(self.a_b_cols[0])
        deter_b[0][-2].set_color(self.a_b_cols[1])

        self.play(
            Transform(factor_a_copy2, deter_a), Transform(factor_b_copy2, deter_b)
        )

        self.wait(8)


class SeeIfFormulaMakesSense(LinearTransformationScene):

    CONFIG = {
        "include_background_plane": True,
        "include_foreground_plane": True,
        "background_plane_kwargs": {
            "background_line_style": {
                "stroke_width": 2,
            },
        },
        "show_coordinates": True,
        "show_basis_vectors": True,
        "show_unit_square": True,
        "a_mat": np.array([[1, 1], [-1, -1]]),
        "b_mat": np.array([[2, 1], [-1, 2]]),
        "back_basis_cols": [BLUE, GREEN],
        "fore_basis_cols": ["#d40b37", "#d4b90b"],
        "a_b_cols": [BLUE, GREEN],
        "det_col": YELLOW_D,
        "i_hat_color": BLUE,
        "j_hat_color": GREEN,
        "prod_mat": np.array([[4, 0], [0, 2]]),
    }

    def construct(self):

        back_grid, fore_grid = self.background_plane, self.plane
        back_sq = self.get_unit_square().set_color_by_gradient(*self.back_basis_cols)
        fore_sq = self.get_unit_square().set_color_by_gradient(*self.back_basis_cols)
        # back_basis = self.get_basis_vectors(*self.back_basis_cols)

        b_mat = (
            Matrix(self.b_mat.transpose(), include_background_rectangle=True)
            .scale(0.75)
            .set_column_colors(*self.fore_basis_cols)
            .to_corner(UP + LEFT)
        )
        a_mat = (
            Matrix(self.a_mat.transpose(), include_background_rectangle=True)
            .scale(0.75)
            .set_column_colors(*self.fore_basis_cols)
            .next_to(b_mat)
        )
        b_text = Text("B").next_to(b_mat, DOWN).set_color(self.a_b_cols[1])
        a_text = Text("A").next_to(a_mat, DOWN).set_color(self.a_b_cols[0])

        text = (
            Text("det(AB) = det(A).det(B)")
            .set_width(FRAME_X_RADIUS - 1)
            .move_to(3.5 * LEFT + UP)
            .add_background_rectangle()
        )

        self.add(a_mat, b_mat, b_text, a_text, text)
        self.moving_vectors += [*self.basis_vectors]
        self.transformable_mobjects += [back_sq, fore_grid]

        self.wait(6)

        self.apply_transposed_matrix(self.a_mat, run_time=1.5)
        self.wait(1.5)
        self.apply_transposed_matrix(self.b_mat, run_time=1.5)
        self.wait(3)

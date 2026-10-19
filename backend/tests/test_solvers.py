import pytest
from pydantic import ValidationError
from fractions import Fraction

from backend.models.schemas import LinearProgramRequest, parse_to_fraction
from backend.core.standard_simplex import StandardSimplexSolver
from backend.core.revised_simplex import RevisedSimplexSolver


class TestInputValidationAndSecurity:
    """Tests for input validation, type security, and error handling."""

    def test_valid_fraction_parsing(self):
        assert parse_to_fraction("3/4") == Fraction(3, 4)
        assert parse_to_fraction("-5/2") == Fraction(-5, 2)
        assert parse_to_fraction(5) == Fraction(5, 1)
        assert parse_to_fraction("2.5") == Fraction(5, 2)

    def test_invalid_fraction_division_by_zero(self):
        with pytest.raises(ValueError, match="División por cero"):
            parse_to_fraction("4/0")

    def test_invalid_text_rejection(self):
        with pytest.raises(ValueError):
            parse_to_fraction("abc")

    def test_empty_objective_rejection(self):
        with pytest.raises(ValidationError):
            LinearProgramRequest(
                objective_type="MAXIMIZE",
                c=[],
                A=[[1, 2]],
                constraint_types=["<="],
                b=[10]
            )

    def test_dimension_mismatch_c_and_A(self):
        # c has 3 vars, A row has 2
        with pytest.raises(ValidationError, match="Inconsistencia dimensional"):
            LinearProgramRequest(
                objective_type="MAXIMIZE",
                c=[1, 2, 3],
                A=[[1, 2]],
                constraint_types=["<="],
                b=[10]
            )

    def test_dimension_mismatch_A_and_b(self):
        # A has 2 rows, b has 1
        with pytest.raises(ValidationError, match="Inconsistencia dimensional"):
            LinearProgramRequest(
                objective_type="MAXIMIZE",
                c=[1, 2],
                A=[[1, 2], [3, 4]],
                constraint_types=["<=", "<="],
                b=[10]
            )

    def test_invalid_constraint_operator(self):
        with pytest.raises(ValidationError):
            LinearProgramRequest(
                objective_type="MAXIMIZE",
                c=[1, 2],
                A=[[1, 2]],
                constraint_types=["<>"],
                b=[10]
            )


class TestStandardVsRevisedSimplex:
    """Cross-validation between Standard Simplex and Revised Simplex."""

    def test_classic_maximization_problem(self):
        """
        Max Z = 3x1 + 5x2
        s.t.
          x1 <= 4
          2x2 <= 12
          3x1 + 2x2 <= 18
          x1, x2 >= 0
        Optimal: x1 = 2, x2 = 6, Z = 36
        """
        req = LinearProgramRequest(
            objective_type="MAXIMIZE",
            c=[3, 5],
            A=[
                [1, 0],
                [0, 2],
                [3, 2]
            ],
            constraint_types=["<=", "<=", "<="],
            b=[4, 12, 18],
            variable_names=["x1", "x2"]
        )

        std_res = StandardSimplexSolver(req).solve()
        rev_res = RevisedSimplexSolver(req).solve()

        assert std_res.status == "OPTIMAL"
        assert rev_res.status == "OPTIMAL"

        # Check optimal value
        assert std_res.optimal_value.fraction == "36"
        assert rev_res.optimal_value.fraction == "36"

        # Check decision variable values
        assert std_res.solution["x1"].fraction == "2"
        assert std_res.solution["x2"].fraction == "6"
        assert rev_res.solution["x1"].fraction == "2"
        assert rev_res.solution["x2"].fraction == "6"

    def test_fractional_optimal_values(self):
        """
        Max Z = 2x1 + 3x2
        s.t.
          x1 + 2x2 <= 8
          3x1 + 2x2 <= 14
        Optimal: x1 = 3, x2 = 5/2 (2.5), Z = 2*3 + 3*(5/2) = 6 + 15/2 = 27/2 = 13.5
        """
        req = LinearProgramRequest(
            objective_type="MAXIMIZE",
            c=[2, 3],
            A=[
                [1, 2],
                [3, 2]
            ],
            constraint_types=["<=", "<="],
            b=[8, 14],
            variable_names=["x1", "x2"]
        )

        std_res = StandardSimplexSolver(req).solve()
        rev_res = RevisedSimplexSolver(req).solve()

        assert std_res.status == "OPTIMAL"
        assert rev_res.status == "OPTIMAL"
        assert std_res.optimal_value.fraction == "27/2"
        assert rev_res.optimal_value.fraction == "27/2"
        assert std_res.solution["x1"].fraction == "3"
        assert std_res.solution["x2"].fraction == "5/2"
        assert rev_res.solution["x2"].fraction == "5/2"

    def test_two_phase_minimization_with_mixed_constraints(self):
        """
        Min Z = 4x1 + x2
        s.t.
          3x1 + x2 = 3
          4x1 + 3x2 >= 6
          x1 + 2x2 <= 4
        """
        req = LinearProgramRequest(
            objective_type="MINIMIZE",
            c=[4, 1],
            A=[
                [3, 1],
                [4, 3],
                [1, 2]
            ],
            constraint_types=["=", ">=", "<="],
            b=[3, 6, 4],
            variable_names=["x1", "x2"]
        )

        std_res = StandardSimplexSolver(req).solve()
        rev_res = RevisedSimplexSolver(req).solve()

        assert std_res.status == "OPTIMAL"
        assert rev_res.status == "OPTIMAL"
        assert std_res.optimal_value.fraction == rev_res.optimal_value.fraction
        assert std_res.solution["x1"].fraction == rev_res.solution["x1"].fraction
        assert std_res.solution["x2"].fraction == rev_res.solution["x2"].fraction


class TestEdgeCasesAndStability:
    """Tests for unbounded, infeasible, and degenerated problems."""

    def test_unbounded_problem(self):
        """
        Max Z = 2x1 + x2
        s.t.
          x1 - x2 <= 10
          2x1 <= 40
        x2 is completely unconstrained above, Z -> infinity
        """
        req = LinearProgramRequest(
            objective_type="MAXIMIZE",
            c=[2, 1],
            A=[
                [1, -1],
                [2, 0]
            ],
            constraint_types=["<=", "<="],
            b=[10, 40],
            variable_names=["x1", "x2"]
        )

        std_res = StandardSimplexSolver(req).solve()
        rev_res = RevisedSimplexSolver(req).solve()

        assert std_res.status == "UNBOUNDED"
        assert rev_res.status == "UNBOUNDED"

    def test_infeasible_problem(self):
        """
        Max Z = 3x1 + 2x2
        s.t.
          x1 + x2 <= 2
          x1 + x2 >= 4
        Contradictory constraints.
        """
        req = LinearProgramRequest(
            objective_type="MAXIMIZE",
            c=[3, 2],
            A=[
                [1, 1],
                [1, 1]
            ],
            constraint_types=["<=", ">="],
            b=[2, 4],
            variable_names=["x1", "x2"]
        )

        std_res = StandardSimplexSolver(req).solve()
        rev_res = RevisedSimplexSolver(req).solve()

        assert std_res.status == "INFEASIBLE"
        assert rev_res.status == "INFEASIBLE"

    def test_sensitivity_report_generated(self):
        req = LinearProgramRequest(
            objective_type="MAXIMIZE",
            c=[3, 5],
            A=[
                [1, 0],
                [0, 2],
                [3, 2]
            ],
            constraint_types=["<=", "<=", "<="],
            b=[4, 12, 18],
            variable_names=["x1", "x2"]
        )

        std_res = StandardSimplexSolver(req).solve()
        assert std_res.sensitivity_report is not None
        assert len(std_res.sensitivity_report.variables) == 2
        assert len(std_res.sensitivity_report.constraints) == 3
        shadow_prices = [c.shadow_price.fraction for c in std_res.sensitivity_report.constraints]
        assert any(sp != "0" for sp in shadow_prices)


class TestWordDocumentExercises:
    """Tests corresponding to the exact exercises in 'Metodo_Simplex_Revisado_COMPLETO_Listo_Entrega.docx'."""

    def test_introductory_example(self):
        """
        Ejemplo Introductorio:
        Max Z = 3x1 + 2x2
        s.t.
          x1 + x2 <= 4
          2x1 + x2 <= 5
          x1, x2 >= 0
        Expected: x1 = 1, x2 = 3, Z = 9
        """
        req = LinearProgramRequest(
            objective_type="MAXIMIZE",
            c=[3, 2],
            A=[[1, 1], [2, 1]],
            constraint_types=["<=", "<="],
            b=[4, 5],
            variable_names=["x1", "x2"]
        )
        rev_res = RevisedSimplexSolver(req).solve()
        std_res = StandardSimplexSolver(req).solve()

        assert rev_res.status == "OPTIMAL"
        assert std_res.status == "OPTIMAL"
        assert rev_res.optimal_value.fraction == "9"
        assert std_res.optimal_value.fraction == "9"
        assert rev_res.solution["x1"].fraction == "1"
        assert rev_res.solution["x2"].fraction == "3"

    def test_fishback_ejercicio_1(self):
        """
        Ejercicio 1 (Fishback 2010, p. 70, Ex. 1):
        Max Z = 3x1 + 2x2
        s.t.
          x1 <= 4
          x1 + 3x2 <= 15
          2x1 + x2 <= 10
          x1, x2 >= 0
        Expected: x1 = 3, x2 = 4, Z = 17, s1 = 1
        """
        req = LinearProgramRequest(
            objective_type="MAXIMIZE",
            c=[3, 2],
            A=[[1, 0], [1, 3], [2, 1]],
            constraint_types=["<=", "<=", "<="],
            b=[4, 15, 10],
            variable_names=["x1", "x2"]
        )
        rev_res = RevisedSimplexSolver(req).solve()
        std_res = StandardSimplexSolver(req).solve()

        assert rev_res.status == "OPTIMAL"
        assert std_res.status == "OPTIMAL"
        assert rev_res.optimal_value.fraction == "17"
        assert std_res.optimal_value.fraction == "17"
        assert rev_res.solution["x1"].fraction == "3"
        assert rev_res.solution["x2"].fraction == "4"

    def test_fishback_ejercicio_2(self):
        """
        Ejercicio 2 (Fishback 2010, p. 70, Ex. 2):
        Max Z = 4x1 + x2 + 5x3
        s.t.
          2x1 + x2 + 3x3 <= 14
          6x1 + 3x2 + 3x3 <= 22
          2x1 + 3x2 <= 14
          x1, x2, x3 >= 0
        Expected: x1 = 2, x2 = 0, x3 = 10/3, Z = 74/3, s3 = 10
        """
        req = LinearProgramRequest(
            objective_type="MAXIMIZE",
            c=[4, 1, 5],
            A=[[2, 1, 3], [6, 3, 3], [2, 3, 0]],
            constraint_types=["<=", "<=", "<="],
            b=[14, 22, 14],
            variable_names=["x1", "x2", "x3"]
        )
        rev_res = RevisedSimplexSolver(req).solve()
        std_res = StandardSimplexSolver(req).solve()

        assert rev_res.status == "OPTIMAL"
        assert std_res.status == "OPTIMAL"
        assert rev_res.optimal_value.fraction == "74/3"
        assert std_res.optimal_value.fraction == "74/3"
        assert rev_res.solution["x1"].fraction == "2"
        assert rev_res.solution["x2"].fraction == "0"
        assert rev_res.solution["x3"].fraction == "10/3"

    def test_fishback_ejercicio_3(self):
        """
        Ejercicio 3 (Fishback 2010, p. 70, Ex. 3):
        Min Z = 3x1 - 2x2
        s.t.
          x1 - 2x2 <= 2
          x1 + x2 <= 4
          x1, x2 >= 0
        Expected: x1 = 0, x2 = 4, Z = -8, s1 = 10
        """
        req = LinearProgramRequest(
            objective_type="MINIMIZE",
            c=[3, -2],
            A=[[1, -2], [1, 1]],
            constraint_types=["<=", "<="],
            b=[2, 4],
            variable_names=["x1", "x2"]
        )
        rev_res = RevisedSimplexSolver(req).solve()
        std_res = StandardSimplexSolver(req).solve()

        assert rev_res.status == "OPTIMAL"
        assert std_res.status == "OPTIMAL"
        assert rev_res.optimal_value.fraction == "-8"
        assert std_res.optimal_value.fraction == "-8"
        assert rev_res.solution["x1"].fraction == "0"
        assert rev_res.solution["x2"].fraction == "4"


class TestNetworkExercises:
    """Pruebas unitarias para los ejercicios de optimización en redes y asignación."""

    def test_asignacion_centrales_termicas_3x3(self):
        """
        Ejercicio de asignación:
        Empresas auxiliares A, B, C a Centrales térmicas 1, 2, 3.
        Esperado: Z* = 17, x1=1, x6=1, x8=1
        """
        req = LinearProgramRequest(
            objective_type="MINIMIZE",
            c=[10, 9, 5, 9, 8, 3, 6, 4, 7],
            A=[
                [1, 1, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1, 1],
                [1, 0, 0, 1, 0, 0, 1, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 1, 0],
                [0, 0, 1, 0, 0, 1, 0, 0, 1]
            ],
            constraint_types=["=", "=", "=", "=", "=", "="],
            b=[1, 1, 1, 1, 1, 1],
            variable_names=["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]
        )
        std_res = StandardSimplexSolver(req).solve()
        rev_res = RevisedSimplexSolver(req).solve()

        assert std_res.status == "OPTIMAL"
        assert rev_res.status == "OPTIMAL"
        assert std_res.optimal_value.fraction == "17"
        assert rev_res.optimal_value.fraction == "17"
        assert std_res.solution["x1"].fraction == "1"
        assert std_res.solution["x6"].fraction == "1"
        assert std_res.solution["x8"].fraction == "1"

    def test_asignacion_vendedores_zonas_max(self):
        """
        Ejercicio de asignación con maximización:
        Maximización de ganancias para 3 vendedores en 3 zonas.
        Esperado: Z* = 200
        """
        req = LinearProgramRequest(
            objective_type="MAXIMIZE",
            c=[40, 60, 50, 70, 30, 60, 50, 80, 40],
            A=[
                [1, 1, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1, 1],
                [1, 0, 0, 1, 0, 0, 1, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 1, 0],
                [0, 0, 1, 0, 0, 1, 0, 0, 1]
            ],
            constraint_types=["=", "=", "=", "=", "=", "="],
            b=[1, 1, 1, 1, 1, 1],
            variable_names=["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]
        )
        std_res = StandardSimplexSolver(req).solve()
        rev_res = RevisedSimplexSolver(req).solve()

        assert "OPTIMAL" in std_res.status
        assert "OPTIMAL" in rev_res.status
        assert std_res.optimal_value.fraction == "200"
        assert rev_res.optimal_value.fraction == "200"

    def test_flujo_costo_minimo_red4(self):
        """
        Ejercicio de flujo a costo mínimo:
        Envío de 4 unidades de nodo 1 a 4 con capacidades y transbordo.
        Esperado: Z* = 26
        """
        req = LinearProgramRequest(
            objective_type="MINIMIZE",
            c=[2, 4, 1, 5, 3],
            A=[
                [1, 1, 0, 0, 0],
                [-1, 0, 1, 1, 0],
                [0, -1, -1, 0, 1],
                [0, 0, 0, 1, 1],
                [1, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1]
            ],
            constraint_types=["=", "=", "=", "=", "<=", "<=", "<=", "<=", "<="],
            b=[4, 0, 0, 4, 3, 2, 2, 2, 4],
            variable_names=["x1", "x2", "x3", "x4", "x5"]
        )
        std_res = StandardSimplexSolver(req).solve()
        rev_res = RevisedSimplexSolver(req).solve()

        assert "OPTIMAL" in std_res.status
        assert "OPTIMAL" in rev_res.status
        assert std_res.optimal_value.fraction == "26"
        assert rev_res.optimal_value.fraction == "26"

    def test_flujo_costo_minimo_transporte(self):
        """
        Ejercicio de modelo de transporte como flujo a costo mínimo:
        Transporte de 2 plantas a 3 clientes como flujo a costo mínimo.
        Esperado: Z* = 350, x1=20, x3=20, x5=25, x6=5
        """
        req = LinearProgramRequest(
            objective_type="MINIMIZE",
            c=[4, 6, 8, 5, 3, 7],
            A=[
                [1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1],
                [1, 0, 0, 1, 0, 0],
                [0, 1, 0, 0, 1, 0],
                [0, 0, 1, 0, 0, 1]
            ],
            constraint_types=["=", "=", "=", "=", "="],
            b=[40, 30, 20, 25, 25],
            variable_names=["x1", "x2", "x3", "x4", "x5", "x6"]
        )
        std_res = StandardSimplexSolver(req).solve()
        rev_res = RevisedSimplexSolver(req).solve()

        assert std_res.status == "OPTIMAL"
        assert rev_res.status == "OPTIMAL"
        assert std_res.optimal_value.fraction == "350"
        assert rev_res.optimal_value.fraction == "350"
        assert std_res.solution["x1"].fraction == "20"
        assert std_res.solution["x3"].fraction == "20"
        assert std_res.solution["x5"].fraction == "25"
        assert std_res.solution["x6"].fraction == "5"



import time
from fractions import Fraction
from typing import List, Dict, Any, Optional, Tuple

from backend.models.schemas import (
    LinearProgramRequest,
    LinearProgramResponse,
    RevisedStep,
    RatioInfo,
    NumberValue,
    parse_to_fraction,
    fraction_to_number_value
)
from backend.core.fractions_helper import (
    create_identity_matrix,
    matrix_vector_mult,
    vector_matrix_mult,
    dot_product,
    invert_matrix_exact
)
from backend.core.sensitivity import compute_sensitivity_analysis


class RevisedSimplexSolver:
    def __init__(self, request: LinearProgramRequest):
        self.request = request
        self.is_maximize = request.objective_type.upper() in ["MAXIMIZE", "MAX"]
        self.max_iterations = request.max_iterations
        self.use_blands = request.use_blands_rule
        
        self.num_orig_vars = len(request.c)
        self.num_constraints = len(request.A)
        self.orig_var_names = request.variable_names or [f"x{i+1}" for i in range(self.num_orig_vars)]
        
        self.c_orig = [parse_to_fraction(val) for val in request.c]
        self.A_orig = [[parse_to_fraction(val) for val in row] for row in request.A]
        self.b_orig = [parse_to_fraction(val) for val in request.b]
        self.constraint_types = list(request.constraint_types)

    def solve(self) -> LinearProgramResponse:
        start_time = time.time()
        
        A_norm = [row[:] for row in self.A_orig]
        b_norm = self.b_orig[:]
        c_norm = self.c_orig[:]
        types_norm = self.constraint_types[:]
        
        for i in range(self.num_constraints):
            if b_norm[i] < 0:
                b_norm[i] = -b_norm[i]
                A_norm[i] = [-val for val in A_norm[i]]
                if types_norm[i] in ["<=", "<", "le"]:
                    types_norm[i] = ">="
                elif types_norm[i] in [">=", ">", "ge"]:
                    types_norm[i] = "<="

        col_names = self.orig_var_names[:]
        columns_dict: Dict[str, List[Fraction]] = {}
        cost_dict: Dict[str, Fraction] = {}
        
        for j, name in enumerate(self.orig_var_names):
            columns_dict[name] = [A_norm[i][j] for i in range(self.num_constraints)]
            cost_dict[name] = c_norm[j] if self.is_maximize else -c_norm[j]

        slack_count = 1
        surplus_count = 1
        art_count = 1
        basic_vars: List[str] = []
        needs_phase1 = False

        for i, ct in enumerate(types_norm):
            if ct in ["<=", "<", "le"]:
                s_name = f"s{slack_count}"
                slack_count += 1
                col_names.append(s_name)
                columns_dict[s_name] = [Fraction(1 if r == i else 0, 1) for r in range(self.num_constraints)]
                cost_dict[s_name] = Fraction(0, 1)
                basic_vars.append(s_name)
            elif ct in [">=", ">", "ge"]:
                needs_phase1 = True
                e_name = f"e{surplus_count}"
                surplus_count += 1
                col_names.append(e_name)
                columns_dict[e_name] = [Fraction(-1 if r == i else 0, 1) for r in range(self.num_constraints)]
                cost_dict[e_name] = Fraction(0, 1)
                
                a_name = f"a{art_count}"
                art_count += 1
                col_names.append(a_name)
                columns_dict[a_name] = [Fraction(1 if r == i else 0, 1) for r in range(self.num_constraints)]
                cost_dict[a_name] = Fraction(0, 1)
                basic_vars.append(a_name)
            elif ct in ["=", "eq"]:
                needs_phase1 = True
                a_name = f"a{art_count}"
                art_count += 1
                col_names.append(a_name)
                columns_dict[a_name] = [Fraction(1 if r == i else 0, 1) for r in range(self.num_constraints)]
                cost_dict[a_name] = Fraction(0, 1)
                basic_vars.append(a_name)

        B_inv = create_identity_matrix(self.num_constraints)
        steps: List[RevisedStep] = []

        # PHASE 1
        if needs_phase1:
            phase1_costs: Dict[str, Fraction] = {name: Fraction(0, 1) for name in col_names}
            for name in col_names:
                if name.startswith("a"):
                    phase1_costs[name] = Fraction(-1, 1)

            p1_status, B_inv, basic_vars = self._revised_simplex_loop(
                phase=1,
                col_names=col_names,
                basic_vars=basic_vars,
                columns_dict=columns_dict,
                cost_dict=phase1_costs,
                b_vector=b_norm,
                B_inv=B_inv,
                steps=steps,
                iteration_start=0
            )

            if p1_status == "UNBOUNDED":
                return self._build_response("UNBOUNDED", "El problema no está acotado en la Fase 1.", steps, start_time)

            xB = matrix_vector_mult(B_inv, b_norm)
            cB_p1 = [phase1_costs[bv] for bv in basic_vars]
            w_opt = dot_product(cB_p1, xB)
            
            if w_opt < Fraction(0, 1):
                return self._build_response("INFEASIBLE", "El problema es infactible (Fase 1 terminó con W > 0).", steps, start_time)

            for i, bv in enumerate(basic_vars):
                if bv.startswith("a") and xB[i] > Fraction(0, 1):
                    return self._build_response("INFEASIBLE", "El problema es infactible (variables artificiales no pudieron eliminarse).", steps, start_time)

            col_names = [name for name in col_names if not name.startswith("a")]
            iter_offset = len(steps)
        else:
            iter_offset = 0

        # PHASE 2
        p2_status, B_inv, basic_vars = self._revised_simplex_loop(
            phase=2 if needs_phase1 else 1,
            col_names=col_names,
            basic_vars=basic_vars,
            columns_dict=columns_dict,
            cost_dict=cost_dict,
            b_vector=b_norm,
            B_inv=B_inv,
            steps=steps,
            iteration_start=iter_offset
        )

        if p2_status == "UNBOUNDED":
            return self._build_response("UNBOUNDED", "La solución es no acotada.", steps, start_time)
        elif p2_status == "MAX_ITERATIONS_REACHED":
            return self._build_response("MAX_ITERATIONS_REACHED", "Se alcanzó el límite de iteraciones en el Simplex Revisado.", steps, start_time)

        # Solution Extraction
        xB = matrix_vector_mult(B_inv, b_norm)
        solution_dict: Dict[str, Fraction] = {name: Fraction(0, 1) for name in col_names}
        for i, bv in enumerate(basic_vars):
            if bv in solution_dict:
                solution_dict[bv] = xB[i]

        optimal_z_val = sum(self.c_orig[j] * solution_dict.get(self.orig_var_names[j], Fraction(0, 1)) for j in range(self.num_orig_vars))

        c_B = [cost_dict[bv] for bv in basic_vars]
        pi = vector_matrix_mult(c_B, B_inv)
        is_multiple = False
        for name in col_names:
            if name not in basic_vars:
                c_j = cost_dict[name]
                red_cost = c_j - dot_product(pi, columns_dict[name])
                if red_cost == Fraction(0, 1):
                    d_col = matrix_vector_mult(B_inv, columns_dict[name])
                    if any(val > Fraction(0, 1) for val in d_col):
                        is_multiple = True
                        break

        status = "MULTIPLE_OPTIMAL" if is_multiple else "OPTIMAL"
        msg = "Solución óptima múltiple encontrada por Simplex Revisado." if is_multiple else "Solución óptima global encontrada con éxito por Simplex Revisado."

        sensitivity_rep = compute_sensitivity_analysis(
            c_orig=self.c_orig,
            A_orig=self.A_orig,
            b_orig=self.b_orig,
            constraint_types=self.constraint_types,
            orig_var_names=self.orig_var_names,
            final_basic_vars=basic_vars,
            final_solution=solution_dict,
            is_maximize=self.is_maximize
        )

        sol_formatted = {k: fraction_to_number_value(v) for k, v in solution_dict.items()}

        return LinearProgramResponse(
            status=status,
            method_used="REVISED_SIMPLEX",
            message=msg,
            objective_type="MAXIMIZE" if self.is_maximize else "MINIMIZE",
            optimal_value=fraction_to_number_value(optimal_z_val),
            solution=sol_formatted,
            variable_names=self.orig_var_names,
            all_variable_names=col_names,
            revised_iterations=steps,
            sensitivity_report=sensitivity_rep,
            execution_time_ms=round((time.time() - start_time) * 1000, 2)
        )

    def _revised_simplex_loop(
        self,
        phase: int,
        col_names: List[str],
        basic_vars: List[str],
        columns_dict: Dict[str, List[Fraction]],
        cost_dict: Dict[str, Fraction],
        b_vector: List[Fraction],
        B_inv: List[List[Fraction]],
        steps: List[RevisedStep],
        iteration_start: int
    ) -> Tuple[str, List[List[Fraction]], List[str]]:
        
        m = self.num_constraints
        iteration = iteration_start

        while iteration - iteration_start < self.max_iterations:
            non_basic_vars = [name for name in col_names if name not in basic_vars]
            cB = [cost_dict[bv] for bv in basic_vars]
            
            xB = matrix_vector_mult(B_inv, b_vector)
            current_z = dot_product(cB, xB)
            pi = vector_matrix_mult(cB, B_inv)
            
            reduced_costs: Dict[str, Fraction] = {}
            improving_candidates: List[Tuple[str, Fraction]] = []
            
            for nb_var in non_basic_vars:
                Aj = columns_dict[nb_var]
                pi_Aj = dot_product(pi, Aj)
                rc = cost_dict[nb_var] - pi_Aj
                reduced_costs[nb_var] = rc
                
                if rc > Fraction(0, 1):
                    improving_candidates.append((nb_var, rc))

            current_step = RevisedStep(
                iteration=iteration,
                phase=phase,
                description="",
                basic_vars=basic_vars[:],
                non_basic_vars=non_basic_vars[:],
                cB=[fraction_to_number_value(v) for v in cB],
                B_inv=[[fraction_to_number_value(val) for val in row] for row in B_inv],
                xB=[fraction_to_number_value(v) for v in xB],
                current_Z=fraction_to_number_value(current_z if self.is_maximize or phase == 1 else -current_z),
                pi_multipliers=[fraction_to_number_value(v) for v in pi],
                reduced_costs={k: fraction_to_number_value(v) for k, v in reduced_costs.items()},
                is_optimal=len(improving_candidates) == 0
            )

            if len(improving_candidates) == 0:
                current_step.description = f"Fase {phase} completada: Óptimo alcanzado (todos los costos reducidos son <= 0)."
                steps.append(current_step)
                return "OPTIMAL", B_inv, basic_vars

            if self.use_blands:
                entering_var = min(improving_candidates, key=lambda pair: col_names.index(pair[0]))[0]
            else:
                entering_var = max(improving_candidates, key=lambda pair: pair[1])[0]

            current_step.entering_var = entering_var
            A_k = columns_dict[entering_var]
            current_step.entering_col_original = [fraction_to_number_value(v) for v in A_k]

            d = matrix_vector_mult(B_inv, A_k)
            current_step.transformed_col_d = [fraction_to_number_value(v) for v in d]

            ratios: List[RatioInfo] = []
            min_ratio = None
            pivot_row = None

            for i in range(m):
                d_i = d[i]
                xb_i = xB[i]
                
                ratio_info = RatioInfo(
                    row_index=i,
                    basic_var=basic_vars[i],
                    rhs=fraction_to_number_value(xb_i),
                    pivot_col_val=fraction_to_number_value(d_i),
                    is_valid=False,
                    is_minimum=False
                )

                if d_i > Fraction(0, 1):
                    ratio = xb_i / d_i
                    ratio_info.ratio = fraction_to_number_value(ratio)
                    ratio_info.is_valid = True

                    if min_ratio is None or ratio < min_ratio:
                        min_ratio = ratio
                        pivot_row = i
                
                ratios.append(ratio_info)

            if pivot_row is None:
                current_step.description = f"Problema No Acotado: La columna transformada d para '{entering_var}' no tiene elementos positivos."
                steps.append(current_step)
                return "UNBOUNDED", B_inv, basic_vars

            ratios[pivot_row].is_minimum = True
            current_step.ratios = ratios
            current_step.pivot_row = pivot_row
            leaving_var = basic_vars[pivot_row]
            current_step.leaving_var = leaving_var

            current_step.description = (
                f"Iteración {iteration} (Fase {phase}): Entra '{entering_var}' (costo reducido = {fraction_to_number_value(reduced_costs[entering_var]).fraction}) "
                f"y sale '{leaving_var}' (fila base {pivot_row+1})."
            )
            steps.append(current_step)

            pivot_elem = d[pivot_row]
            aug = [row[:] + [d[r]] for r, row in enumerate(B_inv)]
            
            for c in range(m + 1):
                aug[pivot_row][c] /= pivot_elem

            for r in range(m):
                if r != pivot_row:
                    factor = aug[r][m]
                    if factor != Fraction(0, 1):
                        for c in range(m + 1):
                            aug[r][c] -= factor * aug[pivot_row][c]

            B_inv = [[aug[r][c] for c in range(m)] for r in range(m)]
            basic_vars[pivot_row] = entering_var
            iteration += 1

        return "MAX_ITERATIONS_REACHED", B_inv, basic_vars

    def _build_response(self, status: str, message: str, steps: List[RevisedStep], start_time: float) -> LinearProgramResponse:
        return LinearProgramResponse(
            status=status,
            method_used="REVISED_SIMPLEX",
            message=message,
            objective_type="MAXIMIZE" if self.is_maximize else "MINIMIZE",
            optimal_value=None,
            solution=None,
            variable_names=self.orig_var_names,
            all_variable_names=self.orig_var_names,
            revised_iterations=steps,
            execution_time_ms=round((time.time() - start_time) * 1000, 2)
        )

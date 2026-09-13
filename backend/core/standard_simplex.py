import time
from fractions import Fraction
from typing import List, Dict, Any, Optional, Tuple

from backend.models.schemas import (
    LinearProgramRequest,
    LinearProgramResponse,
    TableauStep,
    RatioInfo,
    NumberValue,
    parse_to_fraction,
    fraction_to_number_value
)
from backend.core.sensitivity import compute_sensitivity_analysis


class StandardSimplexSolver:
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

        needs_phase1 = False
        for ct in types_norm:
            if ct in [">=", ">", "ge", "=", "eq"]:
                needs_phase1 = True
                break

        steps: List[TableauStep] = []
        col_names = self.orig_var_names[:]
        slack_map = {}
        surplus_map = {}
        art_map = {}
        
        slack_count = 1
        surplus_count = 1
        art_count = 1
        
        for i, ct in enumerate(types_norm):
            if ct in ["<=", "<", "le"]:
                name = f"s{slack_count}"
                slack_count += 1
                col_names.append(name)
                slack_map[i] = name
            elif ct in [">=", ">", "ge"]:
                e_name = f"e{surplus_count}"
                surplus_count += 1
                col_names.append(e_name)
                surplus_map[i] = e_name
                
                a_name = f"a{art_count}"
                art_count += 1
                col_names.append(a_name)
                art_map[i] = a_name
            elif ct in ["=", "eq"]:
                a_name = f"a{art_count}"
                art_count += 1
                col_names.append(a_name)
                art_map[i] = a_name

        total_cols = len(col_names)
        constraint_rows = [[Fraction(0, 1) for _ in range(total_cols)] for _ in range(self.num_constraints)]
        basic_vars = []
        
        for i in range(self.num_constraints):
            for j in range(self.num_orig_vars):
                constraint_rows[i][j] = A_norm[i][j]
            if i in slack_map:
                col_idx = col_names.index(slack_map[i])
                constraint_rows[i][col_idx] = Fraction(1, 1)
                basic_vars.append(slack_map[i])
            if i in surplus_map:
                col_idx = col_names.index(surplus_map[i])
                constraint_rows[i][col_idx] = Fraction(-1, 1)
            if i in art_map:
                col_idx = col_names.index(art_map[i])
                constraint_rows[i][col_idx] = Fraction(1, 1)
                basic_vars.append(art_map[i])

        rhs_rows = b_norm[:]

        # PHASE 1
        if needs_phase1:
            w_row = [Fraction(0, 1) for _ in range(total_cols)]
            w_rhs = [Fraction(0, 1)]
            
            for i in range(self.num_constraints):
                if i in art_map:
                    for j in range(total_cols):
                        if col_names[j] != art_map[i]:
                            w_row[j] -= constraint_rows[i][j]
                    w_rhs[0] -= rhs_rows[i]

            phase1_status, iters_taken = self._simplex_loop(
                phase=1,
                col_names=col_names,
                basic_vars=basic_vars,
                constraint_rows=constraint_rows,
                rhs_rows=rhs_rows,
                obj_row=w_row,
                obj_rhs=w_rhs,
                steps=steps,
                iteration_start=0
            )

            if phase1_status == "UNBOUNDED":
                return self._build_response("UNBOUNDED", "El problema no está acotado en la Fase 1.", steps, start_time)
            
            if w_rhs[0] < Fraction(0, 1):
                return self._build_response("INFEASIBLE", "El problema no tiene solución factible (Fase 1 terminó con W > 0).", steps, start_time)
            
            for i, bv in enumerate(basic_vars):
                if bv.startswith("a"):
                    if rhs_rows[i] > Fraction(0, 1):
                        return self._build_response("INFEASIBLE", "El problema es infactible (variables artificiales no pudieron eliminarse).", steps, start_time)
                    else:
                        for j in range(total_cols):
                            if not col_names[j].startswith("a") and constraint_rows[i][j] != Fraction(0, 1):
                                pivot_col = j
                                pivot_elem = constraint_rows[i][pivot_col]
                                for c in range(total_cols):
                                    constraint_rows[i][c] /= pivot_elem
                                rhs_rows[i] /= pivot_elem
                                for r in range(self.num_constraints):
                                    if r != i:
                                        f = constraint_rows[r][pivot_col]
                                        for c in range(total_cols):
                                            constraint_rows[r][c] -= f * constraint_rows[i][c]
                                        rhs_rows[r] -= f * rhs_rows[i]
                                basic_vars[i] = col_names[pivot_col]
                                break

            art_col_indices = [idx for idx, name in enumerate(col_names) if name.startswith("a")]
            art_col_indices.sort(reverse=True)
            for idx in art_col_indices:
                col_names.pop(idx)
                for r in range(self.num_constraints):
                    constraint_rows[r].pop(idx)
            
            total_cols = len(col_names)
            iter_offset = len(steps)
        else:
            iter_offset = 0

        # PHASE 2
        z_row = [Fraction(0, 1) for _ in range(total_cols)]
        z_rhs = [Fraction(0, 1)]
        
        for j in range(self.num_orig_vars):
            if self.is_maximize:
                z_row[j] = -c_norm[j]
            else:
                z_row[j] = c_norm[j]

        for i, bv in enumerate(basic_vars):
            if bv in col_names:
                bv_col = col_names.index(bv)
                factor = z_row[bv_col]
                if factor != Fraction(0, 1):
                    for j in range(total_cols):
                        z_row[j] -= factor * constraint_rows[i][j]
                    z_rhs[0] -= factor * rhs_rows[i]

        phase2_status, total_iters = self._simplex_loop(
            phase=2 if needs_phase1 else 1,
            col_names=col_names,
            basic_vars=basic_vars,
            constraint_rows=constraint_rows,
            rhs_rows=rhs_rows,
            obj_row=z_row,
            obj_rhs=z_rhs,
            steps=steps,
            iteration_start=iter_offset
        )

        if phase2_status == "UNBOUNDED":
            return self._build_response("UNBOUNDED", "La solución es no acotada (función objetivo infinita).", steps, start_time)
        elif phase2_status == "MAX_ITERATIONS_REACHED":
            return self._build_response("MAX_ITERATIONS_REACHED", "Se alcanzó el límite máximo de iteraciones.", steps, start_time)

        # Solution Extraction
        solution_dict: Dict[str, Fraction] = {name: Fraction(0, 1) for name in col_names}
        for i, bv in enumerate(basic_vars):
            if bv in solution_dict:
                solution_dict[bv] = rhs_rows[i]

        optimal_z = sum(self.c_orig[j] * solution_dict.get(self.orig_var_names[j], Fraction(0, 1)) for j in range(self.num_orig_vars))

        is_multiple_optimal = False
        for j, name in enumerate(col_names):
            if name not in basic_vars and z_row[j] == Fraction(0, 1):
                if any(constraint_rows[i][j] > Fraction(0, 1) for i in range(self.num_constraints)):
                    is_multiple_optimal = True
                    break

        status = "MULTIPLE_OPTIMAL" if is_multiple_optimal else "OPTIMAL"
        msg = "Solución óptima múltiple (alternativa) encontrada." if is_multiple_optimal else "Solución óptima global encontrada con éxito."

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
            method_used="STANDARD_SIMPLEX",
            message=msg,
            objective_type="MAXIMIZE" if self.is_maximize else "MINIMIZE",
            optimal_value=fraction_to_number_value(optimal_z),
            solution=sol_formatted,
            variable_names=self.orig_var_names,
            all_variable_names=col_names,
            tabular_iterations=steps,
            sensitivity_report=sensitivity_rep,
            execution_time_ms=round((time.time() - start_time) * 1000, 2)
        )

    def _simplex_loop(
        self,
        phase: int,
        col_names: List[str],
        basic_vars: List[str],
        constraint_rows: List[List[Fraction]],
        rhs_rows: List[Fraction],
        obj_row: List[Fraction],
        obj_rhs: List[Fraction],
        steps: List[TableauStep],
        iteration_start: int
    ) -> Tuple[str, int]:
        num_rows = len(constraint_rows)
        num_cols = len(col_names)
        iteration = iteration_start

        while iteration - iteration_start < self.max_iterations:
            entering_candidates = []
            for j in range(num_cols):
                if obj_row[j] < Fraction(0, 1):
                    entering_candidates.append(j)

            current_step = TableauStep(
                iteration=iteration,
                phase=phase,
                description="",
                headers=col_names + ["RHS"],
                basic_vars=basic_vars[:],
                matrix=[[fraction_to_number_value(val) for val in row] for row in constraint_rows] + [
                    [fraction_to_number_value(val) for val in obj_row]
                ],
                rhs=[fraction_to_number_value(val) for val in rhs_rows] + [fraction_to_number_value(obj_rhs[0])],
                is_optimal=len(entering_candidates) == 0
            )

            if len(entering_candidates) == 0:
                current_step.description = f"Fase {phase} completada: Se alcanzó el estado óptimo (todos los coeficientes en la fila objetivo son >= 0)."
                steps.append(current_step)
                return "OPTIMAL", iteration

            if self.use_blands:
                pivot_col = entering_candidates[0]
            else:
                pivot_col = min(entering_candidates, key=lambda j: obj_row[j])

            entering_var = col_names[pivot_col]
            current_step.entering_var = entering_var
            current_step.pivot_col = pivot_col

            ratios: List[RatioInfo] = []
            min_ratio = None
            pivot_row = None

            for i in range(num_rows):
                a_ij = constraint_rows[i][pivot_col]
                b_i = rhs_rows[i]
                
                ratio_info = RatioInfo(
                    row_index=i,
                    basic_var=basic_vars[i],
                    rhs=fraction_to_number_value(b_i),
                    pivot_col_val=fraction_to_number_value(a_ij),
                    is_valid=False,
                    is_minimum=False
                )

                if a_ij > Fraction(0, 1):
                    ratio = b_i / a_ij
                    ratio_info.ratio = fraction_to_number_value(ratio)
                    ratio_info.is_valid = True

                    if min_ratio is None or ratio < min_ratio:
                        min_ratio = ratio
                        pivot_row = i
                
                ratios.append(ratio_info)

            if pivot_row is None:
                current_step.description = f"Problema No Acotado: La columna '{entering_var}' no contiene elementos positivos para la razón mínima."
                steps.append(current_step)
                return "UNBOUNDED", iteration

            ratios[pivot_row].is_minimum = True
            current_step.ratios = ratios
            current_step.pivot_row = pivot_row
            leaving_var = basic_vars[pivot_row]
            current_step.leaving_var = leaving_var
            pivot_element = constraint_rows[pivot_row][pivot_col]
            current_step.pivot_element = fraction_to_number_value(pivot_element)

            current_step.description = (
                f"Iteración {iteration} (Fase {phase}): Entra '{entering_var}' (columna {pivot_col+1}) "
                f"y sale '{leaving_var}' (fila {pivot_row+1}) con elemento pivote {fraction_to_number_value(pivot_element).fraction}."
            )
            steps.append(current_step)

            for j in range(num_cols):
                constraint_rows[pivot_row][j] /= pivot_element
            rhs_rows[pivot_row] /= pivot_element

            for i in range(num_rows):
                if i != pivot_row:
                    factor = constraint_rows[i][pivot_col]
                    if factor != Fraction(0, 1):
                        for j in range(num_cols):
                            constraint_rows[i][j] -= factor * constraint_rows[pivot_row][j]
                        rhs_rows[i] -= factor * rhs_rows[pivot_row]

            obj_factor = obj_row[pivot_col]
            if obj_factor != Fraction(0, 1):
                for j in range(num_cols):
                    obj_row[j] -= obj_factor * constraint_rows[pivot_row][j]
                obj_rhs[0] -= obj_factor * rhs_rows[pivot_row]

            basic_vars[pivot_row] = entering_var
            iteration += 1

        return "MAX_ITERATIONS_REACHED", iteration

    def _build_response(self, status: str, message: str, steps: List[TableauStep], start_time: float) -> LinearProgramResponse:
        return LinearProgramResponse(
            status=status,
            method_used="STANDARD_SIMPLEX",
            message=message,
            objective_type="MAXIMIZE" if self.is_maximize else "MINIMIZE",
            optimal_value=None,
            solution=None,
            variable_names=self.orig_var_names,
            all_variable_names=self.orig_var_names,
            tabular_iterations=steps,
            execution_time_ms=round((time.time() - start_time) * 1000, 2)
        )

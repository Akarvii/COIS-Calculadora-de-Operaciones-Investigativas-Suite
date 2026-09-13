from fractions import Fraction
from typing import List, Dict, Any, Optional

from backend.models.schemas import (
    SensitivityReport,
    VariableSensitivity,
    ConstraintSensitivity,
    NumberValue,
    fraction_to_number_value
)
from backend.core.fractions_helper import (
    invert_matrix_exact,
    matrix_vector_mult,
    vector_matrix_mult,
    dot_product
)


def compute_sensitivity_analysis(
    c_orig: List[Fraction],
    A_orig: List[List[Fraction]],
    b_orig: List[Fraction],
    constraint_types: List[str],
    orig_var_names: List[str],
    final_basic_vars: List[str],
    final_solution: Dict[str, Fraction],
    is_maximize: bool
) -> Optional[SensitivityReport]:
    try:
        m = len(A_orig)
        n = len(c_orig)
        
        all_cols_dict: Dict[str, List[Fraction]] = {}
        all_c_dict: Dict[str, Fraction] = {}
        
        for j, name in enumerate(orig_var_names):
            all_cols_dict[name] = [A_orig[i][j] for i in range(m)]
            all_c_dict[name] = c_orig[j] if is_maximize else -c_orig[j]
        
        slack_count = 1
        surplus_count = 1
        for i, ct in enumerate(constraint_types):
            if ct in ["<=", "<", "le"]:
                s_name = f"s{slack_count}"
                slack_count += 1
                col = [Fraction(1 if r == i else 0, 1) for r in range(m)]
                all_cols_dict[s_name] = col
                all_c_dict[s_name] = Fraction(0, 1)
            elif ct in [">=", ">", "ge"]:
                e_name = f"e{surplus_count}"
                surplus_count += 1
                col = [Fraction(-1 if r == i else 0, 1) for r in range(m)]
                all_cols_dict[e_name] = col
                all_c_dict[e_name] = Fraction(0, 1)

        B_matrix: List[List[Fraction]] = [[Fraction(0, 1) for _ in range(m)] for _ in range(m)]
        c_B: List[Fraction] = []
        
        for r, bv in enumerate(final_basic_vars):
            col = all_cols_dict.get(bv, [Fraction(1 if k == r else 0, 1) for k in range(m)])
            for i in range(m):
                B_matrix[i][r] = col[i]
            c_B.append(all_c_dict.get(bv, Fraction(0, 1)))

        B_inv = invert_matrix_exact(B_matrix)
        if not B_inv:
            return None

        pi = vector_matrix_mult(c_B, B_inv)
        xB = matrix_vector_mult(B_inv, b_orig)

        # 1. Variables Sensitivity
        var_reports: List[VariableSensitivity] = []
        for j, var_name in enumerate(orig_var_names):
            final_val = final_solution.get(var_name, Fraction(0, 1))
            is_basic = var_name in final_basic_vars
            col_Aj = all_cols_dict[var_name]
            
            c_j = all_c_dict[var_name]
            pi_Aj = dot_product(pi, col_Aj)
            reduced_cost = c_j - pi_Aj
            
            allowable_min = None
            allowable_max = None
            
            if not is_basic:
                limit_val = pi_Aj if is_maximize else -pi_Aj
                allowable_max = fraction_to_number_value(limit_val)
            else:
                r = final_basic_vars.index(var_name)
                lower_bounds = []
                upper_bounds = []
                
                for k_name, k_col in all_cols_dict.items():
                    if k_name not in final_basic_vars:
                        k_red_cost = all_c_dict[k_name] - dot_product(pi, k_col)
                        gamma_k = sum(B_inv[r][i] * k_col[i] for i in range(m))
                        if gamma_k > Fraction(0, 1):
                            upper_bounds.append(k_red_cost / gamma_k)
                        elif gamma_k < Fraction(0, 1):
                            lower_bounds.append(k_red_cost / gamma_k)
                
                orig_c_val = c_orig[j]
                if lower_bounds:
                    max_lower_delta = max(lower_bounds)
                    allowable_min = fraction_to_number_value(orig_c_val + (max_lower_delta if is_maximize else -max_lower_delta))
                if upper_bounds:
                    min_upper_delta = min(upper_bounds)
                    allowable_max = fraction_to_number_value(orig_c_val + (min_upper_delta if is_maximize else -min_upper_delta))

            var_reports.append(VariableSensitivity(
                name=var_name,
                final_value=fraction_to_number_value(final_val),
                reduced_cost=fraction_to_number_value(reduced_cost),
                objective_coefficient=fraction_to_number_value(c_orig[j]),
                allowable_min=allowable_min,
                allowable_max=allowable_max,
                status="BASIC" if is_basic else "NON_BASIC"
            ))

        # 2. Constraints Sensitivity (RHS & Shadow Prices)
        constraint_reports: List[ConstraintSensitivity] = []
        for i in range(m):
            ct = constraint_types[i]
            shadow_price = pi[i] if is_maximize else -pi[i]
            
            slack_val = Fraction(0, 1)
            slack_name = f"s{i+1}"
            surplus_name = f"e{i+1}"
            if slack_name in final_solution:
                slack_val = final_solution[slack_name]
            elif surplus_name in final_solution:
                slack_val = final_solution[surplus_name]

            is_binding = (slack_val == Fraction(0, 1))

            lower_deltas = []
            upper_deltas = []
            for r in range(m):
                beta_r = B_inv[r][i]
                if beta_r > Fraction(0, 1):
                    lower_deltas.append(-xB[r] / beta_r)
                elif beta_r < Fraction(0, 1):
                    upper_deltas.append(-xB[r] / beta_r)

            b_val = b_orig[i]
            allowable_min_b = None
            allowable_max_b = None

            if lower_deltas:
                max_low_d = max(lower_deltas)
                allowable_min_b = fraction_to_number_value(b_val + max_low_d)
            if upper_deltas:
                min_up_d = min(upper_deltas)
                allowable_max_b = fraction_to_number_value(b_val + min_up_d)

            constraint_reports.append(ConstraintSensitivity(
                index=i + 1,
                name=f"Restricción {i+1}",
                constraint_type=ct,
                slack_surplus_value=fraction_to_number_value(slack_val),
                shadow_price=fraction_to_number_value(shadow_price),
                rhs_value=fraction_to_number_value(b_val),
                allowable_min=allowable_min_b,
                allowable_max=allowable_max_b,
                status="BINDING" if is_binding else "NON_BINDING"
            ))

        return SensitivityReport(
            variables=var_reports,
            constraints=constraint_reports
        )
    except Exception:
        return None

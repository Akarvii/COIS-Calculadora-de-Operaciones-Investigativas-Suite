import re
from fractions import Fraction
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class NumberValue(BaseModel):
    fraction: str
    decimal: float
    latex: str


def parse_to_fraction(val: Any) -> Fraction:
    """
    Safely parses a number (int, float, string fraction 'a/b' or decimal string) to Fraction.
    Rejects NaN, Infinity, and malformed strings.
    """
    if isinstance(val, Fraction):
        return val
    if isinstance(val, int):
        return Fraction(val, 1)
    if isinstance(val, float):
        if val != val or abs(val) == float('inf'):
            raise ValueError("No se permiten valores NaN o Infinitos.")
        return Fraction(str(val)).limit_denominator(1000000)
    if isinstance(val, str):
        val = val.strip()
        if not val:
            raise ValueError("Valor numérico vacío no permitido.")
        if '/' in val:
            parts = val.split('/')
            if len(parts) != 2:
                raise ValueError(f"Formato de fracción inválido: '{val}'")
            try:
                num = int(parts[0].strip())
                den = int(parts[1].strip())
                if den == 0:
                    raise ValueError(f"División por cero en la fracción: '{val}'")
                return Fraction(num, den)
            except ValueError as e:
                raise ValueError(f"Fracción inválida '{val}': {str(e)}")
        else:
            try:
                return Fraction(val).limit_denominator(1000000)
            except Exception:
                raise ValueError(f"Valor numérico o fracción inválida: '{val}'")
    raise ValueError(f"Tipo de dato no soportado para valor numérico: {type(val)}")


def fraction_to_number_value(frac: Fraction) -> NumberValue:
    """Formats a Fraction into a NumberValue model instance with fraction, decimal and latex."""
    if frac.denominator == 1:
        frac_str = str(frac.numerator)
        latex_str = str(frac.numerator)
    else:
        frac_str = f"{frac.numerator}/{frac.denominator}"
        if frac.numerator < 0:
            latex_str = f"-\\frac{{{abs(frac.numerator)}}}{{{frac.denominator}}}"
        else:
            latex_str = f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
    
    return NumberValue(
        fraction=frac_str,
        decimal=float(frac),
        latex=latex_str
    )


class LinearProgramRequest(BaseModel):
    objective_type: Literal["MAXIMIZE", "MINIMIZE", "MAX", "MIN"] = Field(
        default="MAXIMIZE",
        description="Tipo de optimización: MAXIMIZE o MINIMIZE"
    )
    c: List[Union[int, float, str]] = Field(
        ...,
        description="Coeficientes de la función objetivo [c1, c2, ... cn]"
    )
    A: List[List[Union[int, float, str]]] = Field(
        ...,
        description="Matriz de restricciones de m x n"
    )
    constraint_types: List[Literal["<=", ">=", "=", "le", "ge", "eq", "<", ">"]] = Field(
        ...,
        description="Operadores relacionales para cada restricción"
    )
    b: List[Union[int, float, str]] = Field(
        ...,
        description="Lado derecho (RHS) de cada restricción [b1, b2, ... bm]"
    )
    variable_names: Optional[List[str]] = Field(
        default=None,
        description="Nombres personalizados para las variables (ej: ['x1', 'x2'])"
    )
    max_iterations: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Límite máximo de iteraciones para prevenir bucles"
    )
    use_blands_rule: bool = Field(
        default=True,
        description="Usar la regla de Bland para evitar ciclos por degeneración"
    )

    @field_validator("c")
    @classmethod
    def validate_c(cls, v):
        if not v or len(v) == 0:
            raise ValueError("El vector de la función objetivo (c) no puede estar vacío.")
        if len(v) > 50:
            raise ValueError("Máximo 50 variables permitidas por seguridad.")
        for i, val in enumerate(v):
            try:
                parse_to_fraction(val)
            except Exception as e:
                raise ValueError(f"Error en coeficiente c[{i+1}]: {str(e)}")
        return v

    @field_validator("A")
    @classmethod
    def validate_A(cls, v):
        if not v or len(v) == 0:
            raise ValueError("La matriz de restricciones (A) no puede estar vacía.")
        if len(v) > 50:
            raise ValueError("Máximo 50 restricciones permitidas por seguridad.")
        num_cols = len(v[0])
        if num_cols == 0:
            raise ValueError("Las filas de restricciones no pueden estar vacías.")
        for row_idx, row in enumerate(v):
            if len(row) != num_cols:
                raise ValueError(f"La fila {row_idx+1} de la matriz A tiene {len(row)} columnas, pero se esperaban {num_cols}.")
            for col_idx, val in enumerate(row):
                try:
                    parse_to_fraction(val)
                except Exception as e:
                    raise ValueError(f"Error en A[{row_idx+1}][{col_idx+1}]: {str(e)}")
        return v

    @field_validator("b")
    @classmethod
    def validate_b(cls, v):
        if not v or len(v) == 0:
            raise ValueError("El vector del lado derecho (b) no puede estar vacío.")
        for i, val in enumerate(v):
            try:
                parse_to_fraction(val)
            except Exception as e:
                raise ValueError(f"Error en lado derecho b[{i+1}]: {str(e)}")
        return v

    @field_validator("constraint_types")
    @classmethod
    def validate_constraints(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe especificar el tipo para cada restricción.")
        valid_types = {"<=", ">=", "=", "le", "ge", "eq", "<", ">"}
        for i, ct in enumerate(v):
            if ct not in valid_types:
                raise ValueError(f"Tipo de restricción inválido en posición {i+1}: '{ct}'. Use '<=', '>=' o '='.")
        return v

    @model_validator(mode="after")
    def validate_dimensions(self):
        n_vars = len(self.c)
        n_constraints = len(self.A)
        
        for i, row in enumerate(self.A):
            if len(row) != n_vars:
                raise ValueError(
                    f"Inconsistencia dimensional: La función objetivo tiene {n_vars} variables, "
                    f"pero la restricción {i+1} tiene {len(row)} coeficientes."
                )
        
        if len(self.b) != n_constraints:
            raise ValueError(
                f"Inconsistencia dimensional: Hay {n_constraints} restricciones en la matriz A, "
                f"pero se proporcionaron {len(self.b)} valores en el vector b."
            )
            
        if len(self.constraint_types) != n_constraints:
            raise ValueError(
                f"Inconsistencia dimensional: Hay {n_constraints} restricciones en la matriz A, "
                f"pero se especificaron {len(self.constraint_types)} operadores de restricción."
            )

        if self.variable_names:
            if len(self.variable_names) != n_vars:
                raise ValueError(
                    f"Se proporcionaron {len(self.variable_names)} nombres de variable, "
                    f"pero el modelo tiene {n_vars} variables."
                )
        return self


class RatioInfo(BaseModel):
    row_index: int
    basic_var: str
    rhs: NumberValue
    pivot_col_val: NumberValue
    ratio: Optional[NumberValue] = None
    is_minimum: bool = False
    is_valid: bool = False


class TableauStep(BaseModel):
    iteration: int
    phase: int = 1
    description: str
    headers: List[str]
    basic_vars: List[str]
    matrix: List[List[NumberValue]]
    rhs: List[NumberValue]
    pivot_row: Optional[int] = None
    pivot_col: Optional[int] = None
    pivot_element: Optional[NumberValue] = None
    entering_var: Optional[str] = None
    leaving_var: Optional[str] = None
    ratios: Optional[List[RatioInfo]] = None
    is_optimal: bool = False


class RevisedStep(BaseModel):
    iteration: int
    phase: int = 1
    description: str
    basic_vars: List[str]
    non_basic_vars: List[str]
    cB: List[NumberValue]
    B_inv: List[List[NumberValue]]
    xB: List[NumberValue]
    current_Z: NumberValue
    pi_multipliers: List[NumberValue]
    reduced_costs: Dict[str, NumberValue]
    entering_var: Optional[str] = None
    entering_col_original: Optional[List[NumberValue]] = None
    transformed_col_d: Optional[List[NumberValue]] = None
    leaving_var: Optional[str] = None
    pivot_row: Optional[int] = None
    ratios: Optional[List[RatioInfo]] = None
    is_optimal: bool = False


class VariableSensitivity(BaseModel):
    name: str
    final_value: NumberValue
    reduced_cost: NumberValue
    objective_coefficient: NumberValue
    allowable_min: Optional[NumberValue] = None
    allowable_max: Optional[NumberValue] = None
    status: Literal["BASIC", "NON_BASIC"]


class ConstraintSensitivity(BaseModel):
    index: int
    name: str
    constraint_type: str
    slack_surplus_value: NumberValue
    shadow_price: NumberValue
    rhs_value: NumberValue
    allowable_min: Optional[NumberValue] = None
    allowable_max: Optional[NumberValue] = None
    status: Literal["BINDING", "NON_BINDING"]


class SensitivityReport(BaseModel):
    variables: List[VariableSensitivity]
    constraints: List[ConstraintSensitivity]


class LinearProgramResponse(BaseModel):
    status: Literal["OPTIMAL", "UNBOUNDED", "INFEASIBLE", "MULTIPLE_OPTIMAL", "MAX_ITERATIONS_REACHED", "ERROR"]
    method_used: Literal["STANDARD_SIMPLEX", "REVISED_SIMPLEX"]
    message: str
    objective_type: str
    optimal_value: Optional[NumberValue] = None
    solution: Optional[Dict[str, NumberValue]] = None
    variable_names: List[str]
    all_variable_names: List[str]
    tabular_iterations: Optional[List[TableauStep]] = None
    revised_iterations: Optional[List[RevisedStep]] = None
    sensitivity_report: Optional[SensitivityReport] = None
    execution_time_ms: float

import time
from fastapi import APIRouter

from backend.models.schemas import (
    LinearProgramRequest,
    LinearProgramResponse
)
from backend.models.examples import PRESET_EXAMPLES
from backend.core.standard_simplex import StandardSimplexSolver
from backend.core.revised_simplex import RevisedSimplexSolver

router = APIRouter(prefix="/api", tags=["COIS-IMS (Simplex)"])


@router.post("/solve/standard", response_model=LinearProgramResponse)
def solve_standard_simplex(request: LinearProgramRequest):
    """
    Resuelve el problema de programación lineal usando el Método Simplex Tabular tradicional.
    Incluye Método de Dos Fases si hay restricciones >= o =.
    """
    solver = StandardSimplexSolver(request)
    return solver.solve()


@router.post("/solve/revised", response_model=LinearProgramResponse)
def solve_revised_simplex(request: LinearProgramRequest):
    """
    Resuelve el problema usando el Método Simplex Revisado (Formulación matricial B⁻¹ y costos reducidos bajo demanda).
    """
    solver = RevisedSimplexSolver(request)
    return solver.solve()


@router.post("/solve/compare")
def compare_solvers(request: LinearProgramRequest):
    """
    Ejecuta ambos métodos (Tabular y Revisado) y entrega una comparativa completa de resultados y pasos.
    """
    start = time.time()
    standard_solver = StandardSimplexSolver(request)
    revised_solver = RevisedSimplexSolver(request)
    
    res_std = standard_solver.solve()
    res_rev = revised_solver.solve()
    
    match_status = (res_std.status == res_rev.status)
    match_value = False
    if res_std.optimal_value and res_rev.optimal_value:
        match_value = (res_std.optimal_value.fraction == res_rev.optimal_value.fraction)
    
    return {
        "is_consistent": match_status and (match_value or res_std.status != "OPTIMAL"),
        "standard_result": res_std,
        "revised_result": res_rev,
        "total_comparison_time_ms": round((time.time() - start) * 1000, 2)
    }


@router.get("/examples")
def get_example_problems():
    """
    Retorna problemas predefinidos para pruebas rápidas y educación.
    """
    return PRESET_EXAMPLES

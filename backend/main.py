import time
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.models.schemas import (
    LinearProgramRequest,
    LinearProgramResponse
)
from backend.core.standard_simplex import StandardSimplexSolver
from backend.core.revised_simplex import RevisedSimplexSolver


app = FastAPI(
    title="Simplex & Revised Simplex Optimization API",
    description="API para resolución exacta y paso a paso de Programación Lineal con Método Simplex y Simplex Revisado.",
    version="1.0.0"
)

# CORS middleware for Vue frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for Pydantic / Validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Error de validación")
        errors.append(f"{loc}: {msg}")
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "VALIDATION_ERROR",
            "message": "Los datos ingresados no cumplen con el formato o las reglas matemáticas requeridas.",
            "details": errors
        }
    )


# Exception handler for Mathematical / Value errors
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "status": "MATHEMATICAL_ERROR",
            "message": str(exc),
            "details": [str(exc)]
        }
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Simplex Optimization Engine"}


@app.post("/api/solve/standard", response_model=LinearProgramResponse)
def solve_standard_simplex(request: LinearProgramRequest):
    """
    Resuelve el problema de programación lineal usando el Método Simplex Tabular tradicional.
    Incluye Método de Dos Fases si hay restricciones >= o =.
    """
    solver = StandardSimplexSolver(request)
    return solver.solve()


@app.post("/api/solve/revised", response_model=LinearProgramResponse)
def solve_revised_simplex(request: LinearProgramRequest):
    """
    Resuelve el problema usando el Método Simplex Revisado (Formulación matricial B⁻¹ y costos reducidos bajo demanda).
    """
    solver = RevisedSimplexSolver(request)
    return solver.solve()


@app.post("/api/solve/compare")
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


@app.get("/api/examples")
def get_example_problems():
    """
    Retorna problemas predefinidos para pruebas rápidas y educación.
    """
    return [
        {
            "id": "classic_production",
            "title": "Producción Clásica (Maximización estándar)",
            "description": "Maximizar beneficios sujeto a horas de carpintería y acabado (2 variables, 3 restricciones <=).",
            "request": {
                "objective_type": "MAXIMIZE",
                "c": [3, 5],
                "A": [
                    [1, 0],
                    [0, 2],
                    [3, 2]
                ],
                "constraint_types": ["<=", "<=", "<="],
                "b": [4, 12, 18],
                "variable_names": ["x1", "x2"]
            }
        },
        {
            "id": "mixed_two_phase",
            "title": "Problema Mixto (Dos Fases con >= y =)",
            "description": "Minimización de costos con requerimientos mínimos y exactos.",
            "request": {
                "objective_type": "MINIMIZE",
                "c": [4, 1],
                "A": [
                    [3, 1],
                    [4, 3],
                    [1, 2]
                ],
                "constraint_types": ["=", ">=", "<="],
                "b": [3, 6, 4],
                "variable_names": ["x1", "x2"]
            }
        },
        {
            "id": "unbounded_example",
            "title": "Problema No Acotado",
            "description": "Región factible abierta hacia el infinito que no limita el crecimiento de Z.",
            "request": {
                "objective_type": "MAXIMIZE",
                "c": [2, 1],
                "A": [
                    [1, -1],
                    [2, 0]
                ],
                "constraint_types": ["<=", "<="],
                "b": [10, 40],
                "variable_names": ["x1", "x2"]
            }
        },
        {
            "id": "infeasible_example",
            "title": "Problema Infactible (Sin solución)",
            "description": "Restricciones contradictorias que impiden la existencia de una región factible.",
            "request": {
                "objective_type": "MAXIMIZE",
                "c": [3, 2],
                "A": [
                    [1, 1],
                    [1, 1]
                ],
                "constraint_types": ["<=", ">="],
                "b": [2, 4],
                "variable_names": ["x1", "x2"]
            }
        }
    ]

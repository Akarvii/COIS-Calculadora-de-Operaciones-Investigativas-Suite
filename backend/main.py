import sys
import os

# Asegurar que la raíz del proyecto esté en sys.path para importaciones de 'backend.*'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes_health import router as health_router
from backend.api.routes_simplex import router as simplex_router
from backend.api.routes_networks import router as networks_router


app = FastAPI(
    title="COIS - Calculadora de Operaciones Investigativas Suite API",
    description="API centralizada para resolución exacta paso a paso de Programación Lineal (COIS-IMS) y Optimización en Redes (COIS-Networks).",
    version="2.0.0"
)

# CORS middleware for Vue frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for Pydantic / Validation errors (Fail-Fast & Mensajes claros)
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


# Registrar routers modulares (Principio Open/Closed y Separación de Incumbencias)
app.include_router(health_router)
app.include_router(simplex_router)
app.include_router(networks_router)

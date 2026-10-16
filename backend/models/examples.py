"""
Catálogo de problemas de ejemplo predefinidos para COIS-IMS (Simplex).
Principio SRP: Separa la definición estática de datos de prueba del enrutador HTTP.
"""

from typing import List, Dict, Any

PRESET_EXAMPLES: List[Dict[str, Any]] = [
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

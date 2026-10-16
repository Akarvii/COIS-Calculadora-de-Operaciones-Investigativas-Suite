"""
Router para COIS-Networks (Modelos de Redes y Algoritmos Combinatorios).
Módulo II: Asignación (Kuhn-Munkres), Flujo Máximo (Edmonds-Karp) y Flujo a Costo Mínimo.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/networks", tags=["COIS-Networks"])


@router.get("/status")
def networks_status():
    """
    Retorna los métodos disponibles en el motor de optimización de redes.
    """
    return {
        "status": "ready",
        "module": "COIS-Networks",
        "algorithms": [
            "kuhn_munkres_hungarian",
            "edmonds_karp_max_flow",
            "successive_shortest_path_min_cost_flow"
        ]
    }

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """
    Endpoint de sondeo de estado y conectividad del motor backend.
    """
    return {"status": "ok", "service": "COIS Operations Research Engine"}

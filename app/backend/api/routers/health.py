from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"data": {"status": "ok"}, "meta": {}, "error": None}

from fastapi import APIRouter

router = APIRouter()


@router.get("/screener")
def screener() -> dict:
    return {"data": [], "meta": {}, "error": None}

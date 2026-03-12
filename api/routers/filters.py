from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/filters")
def get_filters(request: Request):
    from api.db import get_filters
    return get_filters(request.app.state.db)

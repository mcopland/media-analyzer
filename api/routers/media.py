from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter()


@router.get("/media")
def list_media(
    request: Request,
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="filename"),
    sort_dir: str = Query(default="asc"),
    resolution: Optional[str] = Query(default=None),
    codec: Optional[str] = Query(default=None),
    hdr: Optional[str] = Query(default=None),
    container: Optional[str] = Query(default=None),
    audio_lang: Optional[str] = Query(default=None),
    sub_lang: Optional[str] = Query(default=None),
):
    from api.db import get_media
    total, items = get_media(
        request.app.state.db,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir,
        resolution=resolution,
        codec=codec,
        hdr=hdr,
        container=container,
        audio_lang=audio_lang,
        sub_lang=sub_lang,
    )
    return {"total": total, "items": items}


@router.get("/media/{media_id}")
def get_media_detail(media_id: int, request: Request):
    from api.db import get_media_by_id
    item = get_media_by_id(request.app.state.db, media_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    return item

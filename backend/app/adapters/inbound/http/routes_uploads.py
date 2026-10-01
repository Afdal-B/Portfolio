"""Serves project images, wherever the image store keeps them (disk locally
and for the images shipped with the code, Upstash for those uploaded
online). Image names embed a random uuid and never change, so the response
is cached for a year, by browsers and by Vercel's CDN alike."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.adapters.inbound.http.dependencies import get_project_service
from app.domain.services.project_service import ProjectService

router = APIRouter(prefix="/uploads", tags=["uploads"])

CACHE_FOREVER = "public, max-age=31536000, s-maxage=31536000, immutable"


@router.get("/{name}")
def get_upload(name: str, service: ProjectService = Depends(get_project_service)) -> Response:
    content = service.load_image(name)
    if content is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not Found")
    return Response(content=content, media_type="image/webp", headers={"Cache-Control": CACHE_FOREVER})

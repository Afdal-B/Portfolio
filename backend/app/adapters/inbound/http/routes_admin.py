"""Admin API: lets the site owner edit the project catalog in production
without a redeploy. Guarded by a single shared secret
(`PORTFOLIO_ADMIN_PASSWORD`); if that isn't configured, every admin endpoint
refuses, so the feature is opt-in per deployment."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.adapters.inbound.http import mappers
from app.adapters.inbound.http.dependencies import get_project_service, require_admin
from app.adapters.inbound.http.schemas import ProjectIn, UploadResult
from app.adapters.outbound.persistence.filesystem_image_store import MAX_BYTES
from app.domain.errors import ImageRejected
from app.domain.services.project_service import ProjectService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.post("/uploads", response_model=UploadResult)
async def post_upload(
    file: UploadFile = File(...), service: ProjectService = Depends(get_project_service)
) -> UploadResult:
    # Read with one byte of headroom so an oversized file is rejected without
    # buffering the whole thing.
    content = await file.read(MAX_BYTES + 1)
    try:
        return UploadResult(url=service.store_image(content))
    except ImageRejected as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.get("/projects", response_model=list[ProjectIn])
def get_admin_projects(service: ProjectService = Depends(get_project_service)) -> list[ProjectIn]:
    return [mappers.project_to_admin_dto(project) for project in service.list_all()]


@router.put("/projects", response_model=list[ProjectIn])
def put_admin_projects(
    projects: list[ProjectIn], service: ProjectService = Depends(get_project_service)
) -> list[ProjectIn]:
    """Replaces the whole catalog: the admin UI edits a local copy of the list
    (add / edit / delete / reorder) and saves it in one call."""
    stored = service.replace_all([mappers.project_from_admin_dto(dto) for dto in projects])
    return [mappers.project_to_admin_dto(project) for project in stored]

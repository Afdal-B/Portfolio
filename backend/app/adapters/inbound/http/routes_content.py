from fastapi import APIRouter, Depends

from app.adapters.inbound.http import mappers
from app.adapters.inbound.http.dependencies import get_content_service, get_project_service
from app.adapters.inbound.http.schemas import (
    ContactOut,
    ExperienceOut,
    Lang,
    ProjectOut,
    SkillGroupOut,
    SuggestionOut,
)
from app.domain.services.content_service import ContentService
from app.domain.services.project_service import ProjectService

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/projects", response_model=list[ProjectOut])
def get_projects(
    lang: Lang = "fr",
    service: ProjectService = Depends(get_project_service),
    content: ContentService = Depends(get_content_service),
) -> list[ProjectOut]:
    return [
        mappers.project_to_dto(project, lang, content.project_stack(project)) for project in service.list_all()
    ]


@router.get("/experience", response_model=list[ExperienceOut])
def get_experience(
    lang: Lang = "fr", service: ContentService = Depends(get_content_service)
) -> list[ExperienceOut]:
    return [mappers.experience_to_dto(experience, lang) for experience in service.experiences()]


@router.get("/skills", response_model=list[SkillGroupOut])
def get_skills(
    lang: Lang = "fr", service: ContentService = Depends(get_content_service)
) -> list[SkillGroupOut]:
    return [mappers.skill_group_to_dto(group, lang) for group in service.skill_groups()]


@router.get("/contacts", response_model=list[ContactOut])
def get_contacts(service: ContentService = Depends(get_content_service)) -> list[ContactOut]:
    return [mappers.contact_to_dto(contact) for contact in service.contacts()]


@router.get("/suggestions", response_model=list[SuggestionOut])
def get_suggestions(
    lang: Lang = "fr", service: ContentService = Depends(get_content_service)
) -> list[SuggestionOut]:
    return [mappers.suggestion_to_dto(suggestion) for suggestion in service.suggestions(lang)]

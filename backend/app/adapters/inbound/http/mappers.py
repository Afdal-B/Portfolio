"""Domain <-> HTTP DTO mapping, including picking one language out of the
domain's bilingual fields."""

from app.adapters.inbound.http import schemas
from app.domain.models import (
    AnalyticsReport,
    Answer,
    Contact,
    Experience,
    Lang,
    Project,
    Skill,
    SkillGroup,
    Suggestion,
)


def answer_to_dto(answer: Answer) -> schemas.ChatResponse:
    return schemas.ChatResponse(
        answer=answer.text,
        sources=answer.sources,
        confidence=answer.confidence,
        intent=answer.intent,
        engine=answer.engine,
    )


def project_to_dto(project: Project, lang: Lang, stack: list[Skill]) -> schemas.ProjectOut:
    return schemas.ProjectOut(
        meta=project.meta[lang],
        title=project.title[lang],
        result=project.result[lang],
        problem=project.problem[lang],
        method=project.method[lang],
        stack=project.stack,
        metrics=project.metrics[lang],
        image_seed=project.image_seed,
        image_url=project.image_url,
        screenshots=project.screenshots,
        url=project.url,
        summary=project.summary.get(lang) or project.result[lang],
        code_url=project.code_url,
        stack_items=[skill_to_dto(skill) for skill in stack],
    )


def project_to_admin_dto(project: Project) -> schemas.ProjectIn:
    return schemas.ProjectIn(
        id=project.id,
        meta=project.meta,
        title=project.title,
        result=project.result,
        problem=project.problem,
        method=project.method,
        stack=project.stack,
        metrics=project.metrics,
        url=project.url,
        image_url=project.image_url,
        screenshots=project.screenshots,
        image_seed=project.image_seed,
        summary=project.summary,
        code_url=project.code_url,
    )


def project_from_admin_dto(dto: schemas.ProjectIn) -> Project:
    return Project(
        id=dto.id,
        meta=dto.meta,
        title=dto.title,
        result=dto.result,
        problem=dto.problem,
        method=dto.method,
        stack=dto.stack,
        metrics=dto.metrics,
        url=dto.url,
        image_url=dto.image_url,
        screenshots=dto.screenshots,
        image_seed=dto.image_seed,
        summary=dto.summary,
        code_url=dto.code_url,
    )


def experience_to_dto(experience: Experience, lang: Lang) -> schemas.ExperienceOut:
    return schemas.ExperienceOut(
        company=experience.company,
        role=experience.role[lang],
        contract_type=experience.contract_type[lang],
        period=experience.period[lang],
        location=experience.location[lang],
        context=experience.context[lang],
        bullets=experience.bullets[lang],
        stack=[skill_to_dto(skill) for skill in experience.stack],
    )


def skill_to_dto(skill: Skill) -> schemas.SkillOut:
    return schemas.SkillOut(name=skill.name, icon=skill.icon, glyph=skill.glyph)


def skill_group_to_dto(group: SkillGroup, lang: Lang) -> schemas.SkillGroupOut:
    return schemas.SkillGroupOut(
        id=group.id,
        title=group.title[lang],
        skills=[skill_to_dto(skill) for skill in group.skills],
    )


def contact_to_dto(contact: Contact) -> schemas.ContactOut:
    return schemas.ContactOut(key=contact.key, value=contact.value, href=contact.href)


def suggestion_to_dto(suggestion: Suggestion) -> schemas.SuggestionOut:
    return schemas.SuggestionOut(id=suggestion.id, label=suggestion.label)


def report_to_dto(report: AnalyticsReport) -> schemas.StatsOut:
    return schemas.StatsOut(
        days=[
            schemas.DailyStatsOut(day=d.day, page_views=d.page_views, visitors=d.visitors, questions=d.questions)
            for d in report.days
        ],
        countries=report.countries,
        cities=report.cities,
        referrers=report.referrers,
        recent_questions=[
            schemas.QuestionOut(at=q.at, outcome=q.outcome, text=q.text, lang=q.lang, confidence=q.confidence)
            for q in report.recent_questions
        ],
        persistent=report.persistent,
    )


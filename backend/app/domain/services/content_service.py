"""Read-only content use cases backing the public site."""

from app.domain.models import Contact, Experience, Lang, Project, Skill, SkillGroup, Suggestion
from app.domain.ports import ContactRepository, ExperienceRepository, QARepository, SkillRepository


class ContentService:
    def __init__(
        self,
        experiences: ExperienceRepository,
        skills: SkillRepository,
        contacts: ContactRepository,
        qa: QARepository,
    ) -> None:
        self._experiences = experiences
        self._skills = skills
        self._contacts = contacts
        self._qa = qa

    def experiences(self) -> list[Experience]:
        return self._experiences.list_all()

    def skill_groups(self) -> list[SkillGroup]:
        return self._skills.list_all()

    def project_stack(self, project: Project) -> list[Skill]:
        """A project's stack as catalog entries, so each one can carry its logo.
        The stack is free text edited in the admin, items separated by "·"."""
        items = [item.strip() for item in project.stack.split("·")]
        return [self._skills.resolve(item) for item in items if item]

    def contacts(self) -> list[Contact]:
        return self._contacts.list_all()

    def suggestions(self, lang: Lang) -> list[Suggestion]:
        """The questions offered as chips — hidden entries stay out."""
        return [
            Suggestion(id=entry.id, label=entry.question[lang])
            for entry in self._qa.list_all()
            if not entry.hidden
        ]

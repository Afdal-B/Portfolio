"""Contact links."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContactEntry:
    key: str
    value: str
    href: str


CONTACTS: list[ContactEntry] = [
    ContactEntry(key="Email", value="afdalbouraima2@gmail.com", href="mailto:afdalbouraima2@gmail.com"),
    ContactEntry(
        key="LinkedIn",
        value="/in/afdal-bouraima-276183253",
        href="https://www.linkedin.com/in/afdal-bouraima-276183253",
    ),
    ContactEntry(key="GitHub", value="/Afdal-B", href="https://github.com/Afdal-B"),
    ContactEntry(key="Hugging Face", value="/Dalfaxy", href="https://huggingface.co/Dalfaxy"),
]

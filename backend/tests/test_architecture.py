"""Architecture guardrails.

The value of hexagonal comes from the dependency rule, and a rule nobody
enforces quietly rots. These tests fail the build if the core starts
depending on the outside world.
"""

import ast
from pathlib import Path

APP = Path(__file__).resolve().parent.parent / "app"

# Standard library only — plus the domain itself.
# Standard-library modules only: the domain stays free of frameworks and I/O
# clients (hashing and date handling are pure computations).
DOMAIN_ALLOWED_ROOTS = {"typing", "dataclasses", "logging", "re", "abc", "hashlib", "datetime", "urllib", "app"}

FRAMEWORKS = {"fastapi", "pydantic", "pydantic_settings", "chromadb", "google", "PIL", "httpx"}


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def python_files(*parts: str) -> list[Path]:
    return [p for p in (APP.joinpath(*parts)).rglob("*.py") if "__pycache__" not in p.parts]


def test_domain_imports_only_stdlib_and_itself() -> None:
    offenders: dict[str, set[str]] = {}
    for path in python_files("domain"):
        forbidden = imported_roots(path) - DOMAIN_ALLOWED_ROOTS
        if forbidden:
            offenders[str(path.relative_to(APP))] = forbidden
    assert not offenders, f"Domain must stay framework-free, found: {offenders}"


def test_domain_never_imports_an_adapter() -> None:
    offenders: dict[str, list[str]] = {}
    for path in python_files("domain"):
        modules = [m for m in _app_modules(path) if m.startswith("app.adapters") or m.startswith("app.container")]
        if modules:
            offenders[str(path.relative_to(APP))] = modules
    assert not offenders, f"Dependencies point inward only, found: {offenders}"


def test_no_framework_leaks_into_the_domain_via_app_modules() -> None:
    """The domain may import `app.*`, but only other domain modules."""
    offenders: dict[str, list[str]] = {}
    for path in python_files("domain"):
        modules = [m for m in _app_modules(path) if not m.startswith("app.domain")]
        if modules:
            offenders[str(path.relative_to(APP))] = modules
    assert not offenders, f"Domain may only import app.domain.*, found: {offenders}"


def test_inbound_adapters_do_not_import_outbound_ones_except_wiring() -> None:
    """HTTP talks to the domain and to the container; the one exception is
    reading upload limits/paths, which are genuinely adapter constants."""
    allowed = {"app.adapters.outbound.persistence.filesystem_image_store"}
    offenders: dict[str, list[str]] = {}
    for path in python_files("adapters", "inbound"):
        modules = [
            m for m in _app_modules(path) if m.startswith("app.adapters.outbound") and m not in allowed
        ]
        if modules:
            offenders[str(path.relative_to(APP))] = modules
    assert not offenders, f"Inbound adapters should go through ports, found: {offenders}"


def test_frameworks_are_confined_to_adapters_and_wiring() -> None:
    wiring = {"config.py", "container.py", "main.py"}
    offenders: dict[str, set[str]] = {}
    for path in python_files():
        relative = path.relative_to(APP)
        if relative.parts[0] == "adapters" or relative.name in wiring:
            continue
        leaked = imported_roots(path) & FRAMEWORKS
        if leaked:
            offenders[str(relative)] = leaked
    assert not offenders, f"Frameworks belong in adapters, found: {offenders}"


def _app_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module and node.module.startswith("app."):
            modules.append(node.module)
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names if alias.name.startswith("app."))
    return modules

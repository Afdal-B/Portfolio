"""Copies the project catalog as it is online into storage/projects.json, and
downloads the images uploaded online that are missing locally.

Run before editing projects locally, so a push starts from the online
version and doesn't hide edits made in the admin:  make pull-projects

Reads the catalog through the admin API, with the production admin password:
PORTFOLIO_PROD_ADMIN_PASSWORD in backend/.env, or PORTFOLIO_ADMIN_PASSWORD
when both environments share it. PORTFOLIO_SITE_URL overrides the site."""

import os
import sys
from pathlib import Path

import httpx

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.adapters.outbound.persistence.filesystem_image_store import (  # noqa: E402
    DEFAULT_UPLOAD_DIR,
    IMAGE_NAME,
    URL_PREFIX,
)
from app.adapters.outbound.persistence.json_project_repository import (  # noqa: E402
    JsonProjectRepository,
    project_from_dict,
)

DEFAULT_SITE = "https://www.afdal-bouraima.fr"


def read_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip("'\"")
    return values


def pull(http: httpx.Client, site: str, password: str, repository: JsonProjectRepository, uploads: Path) -> dict:
    response = http.get(f"{site}/api/admin/projects", headers={"Authorization": f"Bearer {password}"})
    if response.status_code in (401, 404):
        raise SystemExit(
            "Accès refusé par l'admin en ligne : vérifiez PORTFOLIO_PROD_ADMIN_PASSWORD dans backend/.env."
        )
    response.raise_for_status()
    projects = [project_from_dict(item) for item in response.json()]

    downloaded = []
    for url in {u for p in projects for u in (p.image_url, *p.screenshots) if u.startswith(URL_PREFIX + "/")}:
        name = url.rsplit("/", 1)[1]
        target = uploads / name
        if not IMAGE_NAME.match(name) or target.exists():
            continue
        image = http.get(f"{site}{url}")
        image.raise_for_status()
        uploads.mkdir(parents=True, exist_ok=True)
        target.write_bytes(image.content)
        downloaded.append(name)

    before = {p.id for p in repository.list_all()}
    repository.replace_all(projects)
    return {
        "projects": [p.id for p in projects],
        "added": [p.id for p in projects if p.id not in before],
        "removed": sorted(before - {p.id for p in projects}),
        "images": downloaded,
    }


def main() -> None:
    env = {**read_env(BACKEND / ".env"), **os.environ}
    password = env.get("PORTFOLIO_PROD_ADMIN_PASSWORD") or env.get("PORTFOLIO_ADMIN_PASSWORD")
    if not password:
        sys.exit("PORTFOLIO_PROD_ADMIN_PASSWORD n'est pas défini dans backend/.env.")
    site = env.get("PORTFOLIO_SITE_URL", DEFAULT_SITE).rstrip("/")

    with httpx.Client(timeout=60, follow_redirects=True) as http:
        result = pull(http, site, password, JsonProjectRepository(), DEFAULT_UPLOAD_DIR)

    print(f"{len(result['projects'])} projets écrits dans storage/projects.json")
    if result["added"]:
        print("  ajoutés depuis le site :", ", ".join(result["added"]))
    if result["removed"]:
        print("  absents en ligne, retirés :", ", ".join(result["removed"]))
    print(f"  {len(result['images'])} image(s) téléchargée(s) dans storage/uploads")
    print("Ensuite : make embeddings, vérifiez le diff, puis committez.")


if __name__ == "__main__":
    main()

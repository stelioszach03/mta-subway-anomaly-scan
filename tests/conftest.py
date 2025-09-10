import os
from pathlib import Path
from typing import Iterator, TYPE_CHECKING

import pytest


def _load_env_from_infra() -> None:
    env_path = Path("infra/.env")
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            # Do not overwrite already-set envs
            os.environ.setdefault(k, v)
    except Exception:
        # Best-effort only
        pass


@pytest.fixture(autouse=True)
def _unit_env(request: pytest.FixtureRequest) -> Iterator[None]:
    """Ensure unit tests run with an in-memory DB unless marked integration.

    Also load env vars from infra/.env on best-effort basis.
    """
    _load_env_from_infra()
    is_integration = request.node.get_closest_marker("integration") is not None
    prev = os.environ.get("DB_URL")
    try:
        if not is_integration:
            os.environ["DB_URL"] = "sqlite:///:memory:"
        yield
    finally:
        if prev is None:
            os.environ.pop("DB_URL", None)
        else:
            os.environ["DB_URL"] = prev


@pytest.fixture()
def gtfs_dir() -> Path:
    from api.app.core.config import get_settings

    s = get_settings()
    return Path(s.GTFS_STATIC_DIR)


@pytest.fixture()
def has_gtfs(gtfs_dir: Path) -> bool:
    zip_path = gtfs_dir / "mta_gtfs_static.zip"
    has_txt = (gtfs_dir / "stops.txt").exists()
    has_zip = zip_path.exists()
    # Also consider explicit path from settings if it exists
    try:
        from api.app.core.config import get_settings

        s = get_settings()
        if s.MTA_GTFS_STATIC_PATH:
            has_zip = has_zip or Path(s.MTA_GTFS_STATIC_PATH).exists()
    except Exception:
        pass
    return bool(has_txt or has_zip)


if TYPE_CHECKING:  # pragma: no cover - type hints only
    from fastapi.testclient import TestClient as _TestClient


@pytest.fixture()
def test_client() -> "_TestClient":
    from fastapi.testclient import TestClient
    # Import app here so env overrides apply before startup
    from api.app.main import app

    with TestClient(app) as client:  # type: ignore[return-value]
        yield client


@pytest.fixture()
def mapbox_token() -> str:
    token = os.environ.get("MAPBOX_TOKEN") or os.environ.get("NEXT_PUBLIC_MAPBOX_TOKEN")
    if not token:
        pytest.skip("MAPBOX token missing in env")
    return token

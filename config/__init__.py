"""Config loading utilities.

Usage:
    from config import load_settings, load_apps

    settings = load_settings()
    apps = load_apps()
"""

import os
from pathlib import Path

import yaml
from loguru import logger
from pydantic import ValidationError

from config.schema import AppEntry, Settings

# Root of the project (parent of this file's directory)
_PROJECT_ROOT = Path(__file__).parent.parent
_SETTINGS_PATH = _PROJECT_ROOT / "config" / "settings.yaml"
_APPS_PATH = _PROJECT_ROOT / "config" / "apps.yaml"


def load_settings() -> Settings:
    """Load and validate application settings.

    Reads settings.yaml, then overlays environment variables / .env values.
    Raises SystemExit with a clear message on validation failure.
    """
    raw: dict = {}
    if _SETTINGS_PATH.exists():
        with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        logger.debug(f"Loaded settings from {_SETTINGS_PATH}")
    else:
        logger.warning(f"settings.yaml not found at {_SETTINGS_PATH}, using defaults")

    # Change cwd to project root so pydantic-settings finds .env
    original_cwd = os.getcwd()
    os.chdir(_PROJECT_ROOT)
    try:
        settings = Settings(**raw)
    except ValidationError as exc:
        logger.error(f"Configuration error:\n{exc}")
        raise SystemExit(1) from exc
    finally:
        os.chdir(original_cwd)

    return settings


def load_apps() -> dict[str, list[AppEntry]]:
    """Load app, website, and folder shortcuts from apps.yaml.

    Returns:
        Dict with keys 'apps', 'websites', 'folders', each a list of AppEntry.
    """
    result: dict[str, list[AppEntry]] = {"apps": [], "websites": [], "folders": []}

    if not _APPS_PATH.exists():
        logger.warning(f"apps.yaml not found at {_APPS_PATH}")
        return result

    with open(_APPS_PATH, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    for section in ("apps", "websites", "folders"):
        entries = raw.get(section, [])
        for entry in entries:
            try:
                # Convert path/url entries uniformly
                if section == "websites":
                    result[section].append(
                        AppEntry(name=entry["name"], url=entry["url"],
                                 aliases=entry.get("aliases", []))
                    )
                else:
                    result[section].append(
                        AppEntry(name=entry["name"], path=entry.get("path", ""),
                                 aliases=entry.get("aliases", []))
                    )
            except (KeyError, ValidationError) as exc:
                logger.warning(f"Skipping invalid apps.yaml entry {entry}: {exc}")

    total = sum(len(v) for v in result.values())
    logger.debug(f"Loaded {total} app/web/folder shortcuts")
    return result

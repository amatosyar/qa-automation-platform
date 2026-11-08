from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, Playwright


def _as_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default

    normalized = value.strip().lower()

    if normalized in {"1", "true", "yes", "on"}:
        return True

    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        f"Invalid boolean value: {value!r}. Expected true/false."
    )


@pytest.fixture
def browser(playwright: Playwright) -> Iterator[Browser]:
    executable = os.getenv("BROWSER_EXECUTABLE", "").strip()
    channel = os.getenv("BROWSER_CHANNEL", "").strip()
    headless = _as_bool(os.getenv("HEADLESS"), default=True)

    launch_options: dict[str, object] = {
        "headless": headless,
    }

    if executable:
        launch_options["executable_path"] = executable
    elif channel:
        launch_options["channel"] = channel

    browser_instance = playwright.chromium.launch(**launch_options)

    try:
        yield browser_instance
    finally:
        browser_instance.close()

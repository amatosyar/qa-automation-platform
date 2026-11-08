import os

import pytest
from playwright.sync_api import Browser


def test_replace_with_matrix_backed_case(browser: Browser) -> None:
    base_url = os.getenv("BASE_URL", "").strip()

    if not base_url:
        pytest.skip("BASE_URL is not configured")

    page = browser.new_page()

    try:
        response = page.goto(
            base_url,
            wait_until="domcontentloaded",
        )

        assert response is not None
        assert response.ok
        assert page.url
    finally:
        page.close()

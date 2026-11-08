from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "templates" / "playwright"


def test_python_template_required_files_exist() -> None:
    expected = [
        "pyproject.toml",
        "pytest.ini",
        "conftest.py",
        ".env.example",
        ".gitignore",
        "fixtures/__init__.py",
        "fixtures/browser.py",
        "tests/__init__.py",
        "tests/test_example.py",
        "pages/__init__.py",
        "components/__init__.py",
        "data/.gitkeep",
        "evidence/.gitkeep",
        "results/.gitkeep",
        "knowledge/.gitkeep",
    ]

    missing = [
        relative
        for relative in expected
        if not (TEMPLATE / relative).is_file()
    ]

    assert not missing, f"Missing template files: {missing}"


def test_typescript_runtime_is_absent() -> None:
    forbidden = [
        "package.json",
        "playwright.config.ts",
        "tests/example.spec.ts",
    ]

    present = [
        relative
        for relative in forbidden
        if (TEMPLATE / relative).exists()
    ]

    assert not present, f"TypeScript artifacts found: {present}"


def test_python_runtime_is_pinned() -> None:
    content = (TEMPLATE / "pyproject.toml").read_text(
        encoding="utf-8"
    )

    assert 'requires-python = ">=3.12,<3.13"' in content
    assert '"playwright==1.64.1"' in content
    assert '"pytest==9.2.0"' in content
    assert '"pytest-playwright==0.10.0"' in content


def test_browser_is_environment_configurable() -> None:
    content = (TEMPLATE / "fixtures" / "browser.py").read_text(
        encoding="utf-8"
    )

    assert 'os.getenv("BROWSER_EXECUTABLE"' in content
    assert 'os.getenv("BROWSER_CHANNEL"' in content
    assert 'os.getenv("HEADLESS"' in content

    forbidden = [
        "empdela2",
        "amatosya",
        "vw10022",
        "C:\\Users\\",
        "/Users/",
    ]

    for value in forbidden:
        assert value not in content


def test_browser_executable_has_priority_over_channel() -> None:
    content = (TEMPLATE / "fixtures" / "browser.py").read_text(
        encoding="utf-8"
    )

    executable_position = content.index("if executable:")
    channel_position = content.index("elif channel:")

    assert executable_position < channel_position


def test_template_does_not_version_real_secrets() -> None:
    env_content = (TEMPLATE / ".env.example").read_text(
        encoding="utf-8"
    )

    assert "APP_USERNAME=" in env_content
    assert "APP_PASSWORD=" in env_content

    for line in env_content.splitlines():
        stripped = line.strip()

        if stripped.startswith("APP_USERNAME="):
            assert stripped == "APP_USERNAME="

        if stripped.startswith("APP_PASSWORD="):
            assert stripped == "APP_PASSWORD="


def test_example_requires_external_base_url() -> None:
    content = (TEMPLATE / "tests" / "test_example.py").read_text(
        encoding="utf-8"
    )

    assert 'os.getenv("BASE_URL"' in content
    assert "https://" not in content
    assert "http://" not in content


def test_template_gitignore_protects_runtime_secrets() -> None:
    content = (TEMPLATE / ".gitignore").read_text(
        encoding="utf-8"
    )

    assert ".env" in content
    assert ".venv/" in content
    assert "__pycache__/" in content

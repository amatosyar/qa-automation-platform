from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

ENGINEER = ROOT / "agents" / "playwright-engineer.md"
SKILL = ROOT / "skills" / "application-discovery" / "SKILL.md"


def test_application_discovery_skill_exists() -> None:
    assert SKILL.is_file()


def test_engineer_requires_application_discovery_for_new_locators() -> None:
    content = ENGINEER.read_text(encoding="utf-8")

    assert "application-discovery" in content
    assert "locator nuevo" in content
    assert "DOM_INSPECTION" in content


def test_engineer_only_accepts_verified_new_locators() -> None:
    content = ENGINEER.read_text(encoding="utf-8")

    assert "Solo un locator `VERIFIED`" in content
    assert "`NOT_FOUND`" in content
    assert "`AMBIGUOUS`" in content


def test_engineer_does_not_hide_locator_ambiguity_by_position() -> None:
    content = ENGINEER.read_text(encoding="utf-8")

    assert "`.first`" in content
    assert "`.last`" in content
    assert "`.nth(...)`" in content
    assert "XPath posicional" in content


def test_screenshot_is_not_accepted_as_dom_proof() -> None:
    content = ENGINEER.read_text(encoding="utf-8")

    assert "captura de pantalla" in content
    assert "no demuestra por sí sola" in content
    assert "`data-testid`" in content
    assert "accessible name" in content


def test_engineer_role_boundaries_remain_present() -> None:
    content = ENGINEER.read_text(encoding="utf-8")

    assert "No define requisitos." in content
    assert "No aprueba su propio trabajo." in content
    assert "No inventar locators." in content
    assert "fabricar DOM" in content
    assert "inventar selectores" in content
    assert "no declara el estado final LISTO" in content


def test_discovery_skill_requires_real_evidence() -> None:
    content = SKILL.read_text(encoding="utf-8")

    required = [
        "aplicacion real inspeccionada",
        "DOM real",
        "match_count",
        "DOM_INSPECTION",
        "`VERIFIED`",
        "`NOT_FOUND`",
        "`AMBIGUOUS`",
    ]

    for value in required:
        assert value in content


def test_discovery_skill_protects_secrets() -> None:
    content = SKILL.read_text(encoding="utf-8")

    assert "tokens" in content
    assert "passwords" in content
    assert "cookies" in content
    assert "datos sensibles" in content

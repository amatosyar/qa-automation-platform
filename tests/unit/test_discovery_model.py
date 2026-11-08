import pytest

from core.discovery import (
    DiscoveryElement,
    DiscoveryStatus,
    LocatorEvidence,
)


def test_unique_locator_is_verified() -> None:
    locator = LocatorEvidence(
        strategy="get_by_label",
        value="Solicitud TK",
        match_count=1,
    )

    assert locator.status is DiscoveryStatus.VERIFIED


def test_missing_locator_is_not_found() -> None:
    locator = LocatorEvidence(
        strategy="get_by_label",
        value="Solicitud TK",
        match_count=0,
    )

    assert locator.status is DiscoveryStatus.NOT_FOUND


def test_multiple_matches_are_ambiguous() -> None:
    locator = LocatorEvidence(
        strategy="get_by_text",
        value="Aceptar",
        match_count=3,
    )

    assert locator.status is DiscoveryStatus.AMBIGUOUS


def test_locator_requires_dom_evidence() -> None:
    with pytest.raises(ValueError):
        LocatorEvidence(
            strategy="css",
            value="#solicitud",
            match_count=1,
            source="ASSUMPTION",
        )


def test_negative_match_count_is_rejected() -> None:
    with pytest.raises(ValueError):
        LocatorEvidence(
            strategy="get_by_role",
            value="button:Aceptar",
            match_count=-1,
        )


def test_verified_element_requires_unique_locator() -> None:
    element = DiscoveryElement(
        name="Solicitud TK",
        page_url="https://qa.example/atencion",
        locator=LocatorEvidence(
            strategy="get_by_label",
            value="Solicitud TK",
            match_count=1,
        ),
        label="Solicitud TK",
    )

    assert element.verified is True


def test_ambiguous_element_is_not_verified() -> None:
    element = DiscoveryElement(
        name="Aceptar",
        page_url="https://qa.example/atencion",
        locator=LocatorEvidence(
            strategy="get_by_text",
            value="Aceptar",
            match_count=2,
        ),
    )

    assert element.verified is False


def test_discovery_does_not_require_specific_application() -> None:
    element = DiscoveryElement(
        name="Generic field",
        page_url="https://example.invalid",
        locator=LocatorEvidence(
            strategy="data_test",
            value="generic-field",
            match_count=1,
        ),
    )

    serialized = repr(element)

    assert "vw10022" not in serialized
    assert "empdela2" not in serialized
    assert "LDS" not in serialized

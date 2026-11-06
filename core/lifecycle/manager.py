"""Lifecycle determinístico por caso de prueba."""

from core.common.enums import CaseState
from core.common.exceptions import InvalidStateTransition


_ALLOWED_TRANSITIONS = {
    CaseState.DISCOVERED: {
        CaseState.ANALYZED,
        CaseState.BLOCKED,
    },
    CaseState.ANALYZED: {
        CaseState.READY,
        CaseState.BLOCKED,
    },
    CaseState.READY: {
        CaseState.IMPLEMENTING,
        CaseState.BLOCKED,
    },
    CaseState.IMPLEMENTING: {
        CaseState.EXECUTED,
        CaseState.BLOCKED,
    },
    CaseState.EXECUTED: {
        CaseState.IN_REVIEW,
        CaseState.FAIL,
        CaseState.BLOCKED,
    },
    CaseState.IN_REVIEW: {
        CaseState.PASS,
        CaseState.FAIL,
        CaseState.BLOCKED,
    },
    CaseState.FAIL: {
        CaseState.IMPLEMENTING,
        CaseState.BLOCKED,
    },
    CaseState.BLOCKED: {
        CaseState.ANALYZED,
        CaseState.READY,
        CaseState.IMPLEMENTING,
    },
    CaseState.PASS: set(),
}


def can_transition(current: CaseState, target: CaseState) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


def transition(current: CaseState, target: CaseState) -> CaseState:
    if not can_transition(current, target):
        raise InvalidStateTransition(
            f"Transición no permitida: {current.value} -> {target.value}"
        )

    return target


def allowed_transitions(current: CaseState) -> tuple[CaseState, ...]:
    return tuple(sorted(_ALLOWED_TRANSITIONS[current], key=lambda state: state.value))

import unittest

from core.common.enums import CaseState
from core.common.exceptions import InvalidStateTransition
from core.lifecycle.manager import can_transition, transition


class LifecycleTests(unittest.TestCase):

    def test_happy_path(self):
        state = CaseState.DISCOVERED

        for target in (
            CaseState.ANALYZED,
            CaseState.READY,
            CaseState.IMPLEMENTING,
            CaseState.EXECUTED,
            CaseState.IN_REVIEW,
            CaseState.PASS,
        ):
            state = transition(state, target)

        self.assertEqual(state, CaseState.PASS)

    def test_pass_is_terminal(self):
        self.assertFalse(
            can_transition(
                CaseState.PASS,
                CaseState.IMPLEMENTING,
            )
        )

    def test_invalid_transition_fails(self):
        with self.assertRaises(InvalidStateTransition):
            transition(
                CaseState.DISCOVERED,
                CaseState.PASS,
            )


if __name__ == "__main__":
    unittest.main()

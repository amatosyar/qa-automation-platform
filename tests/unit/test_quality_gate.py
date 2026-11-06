import unittest

from core.common.enums import ExecutionStatus, ReviewStatus
from core.quality.gate import (
    QualityGateInput,
    evaluate,
)


class QualityGateTests(unittest.TestCase):

    def test_pass_when_all_conditions_are_met(self):
        result = evaluate(
            QualityGateInput(
                execution_status=ExecutionStatus.PASS,
                review_status=ReviewStatus.PASS,
                traceability_complete=True,
                evidence_complete=True,
            )
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.reasons, ())

    def test_reviewer_pass_is_not_enough(self):
        result = evaluate(
            QualityGateInput(
                execution_status=ExecutionStatus.FAIL,
                review_status=ReviewStatus.PASS,
                traceability_complete=True,
                evidence_complete=True,
            )
        )

        self.assertFalse(result.passed)
        self.assertIn(
            "execution_status=FAIL",
            result.reasons,
        )

    def test_missing_evidence_blocks_pass(self):
        result = evaluate(
            QualityGateInput(
                execution_status=ExecutionStatus.PASS,
                review_status=ReviewStatus.PASS,
                traceability_complete=True,
                evidence_complete=False,
            )
        )

        self.assertFalse(result.passed)
        self.assertIn(
            "evidence_incomplete",
            result.reasons,
        )


if __name__ == "__main__":
    unittest.main()

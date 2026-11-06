from pathlib import Path
import tempfile
import unittest

from core.common.enums import (
    ExecutionStatus,
    ReviewStatus,
)
from core.quality.gate import evaluate_case
from core.traceability import (
    add_ef_ref,
    add_et_ref,
    add_evidence_ref,
    add_execution_ref,
    add_implementation_ref,
    add_review_ref,
    create_case,
)


class QualityTraceabilityIntegrationTests(
    unittest.TestCase
):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = (
            Path(self.temp.name)
            / "traceability"
        )

    def tearDown(self):
        self.temp.cleanup()

    def _create_complete_traceability(self):
        create_case(
            self.root,
            case_id="TC-001",
            matrix_ref="matriz.xlsx#Casos!R2",
        )

        add_ef_ref(
            self.root,
            "TC-001",
            "EF.docx#paragraph-4",
        )

        add_et_ref(
            self.root,
            "TC-001",
            "ET.docx#table-1-row-2",
        )

        add_implementation_ref(
            self.root,
            "TC-001",
            "tests/login.spec.ts#TC-001",
        )

        add_execution_ref(
            self.root,
            "TC-001",
            "results/RUN-001/TC-001/1/result.json",
        )

        add_evidence_ref(
            self.root,
            "TC-001",
            "evidence/RUN-001/TC-001/trace.zip",
        )

        add_review_ref(
            self.root,
            "TC-001",
            "reviews/TC-001.json",
        )

    def test_complete_traceability_can_pass_gate(self):
        self._create_complete_traceability()

        result = evaluate_case(
            traceability_root=self.root,
            case_id="TC-001",
            execution_status=ExecutionStatus.PASS,
            review_status=ReviewStatus.PASS,
            evidence_complete=True,
        )

        self.assertTrue(result.passed)
        self.assertEqual(
            result.reasons,
            (),
        )

    def test_missing_traceability_blocks_gate(self):
        create_case(
            self.root,
            case_id="TC-001",
            matrix_ref="matriz.xlsx#Casos!R2",
        )

        result = evaluate_case(
            traceability_root=self.root,
            case_id="TC-001",
            execution_status=ExecutionStatus.PASS,
            review_status=ReviewStatus.PASS,
            evidence_complete=True,
        )

        self.assertFalse(result.passed)

        self.assertIn(
            "traceability_incomplete",
            result.reasons,
        )

        self.assertIn(
            "traceability_missing=ef",
            result.reasons,
        )

        self.assertIn(
            "traceability_missing=implementation",
            result.reasons,
        )

    def test_reviewer_pass_cannot_override_traceability(self):
        create_case(
            self.root,
            case_id="TC-001",
            matrix_ref="matriz.xlsx#Casos!R2",
        )

        result = evaluate_case(
            traceability_root=self.root,
            case_id="TC-001",
            execution_status=ExecutionStatus.PASS,
            review_status=ReviewStatus.PASS,
            evidence_complete=True,
        )

        self.assertFalse(result.passed)

    def test_execution_failure_blocks_complete_case(self):
        self._create_complete_traceability()

        result = evaluate_case(
            traceability_root=self.root,
            case_id="TC-001",
            execution_status=ExecutionStatus.FAIL,
            review_status=ReviewStatus.PASS,
            evidence_complete=True,
        )

        self.assertFalse(result.passed)

        self.assertIn(
            "execution_status=FAIL",
            result.reasons,
        )


if __name__ == "__main__":
    unittest.main()

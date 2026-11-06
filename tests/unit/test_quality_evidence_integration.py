from pathlib import Path
import tempfile
import unittest

from core.common.enums import (
    ExecutionStatus,
    ReviewStatus,
)
from core.evidence import (
    create_manifest,
    register_file,
)
from core.quality.gate import (
    evaluate_case_with_evidence,
)
from core.traceability import (
    add_ef_ref,
    add_et_ref,
    add_evidence_ref,
    add_execution_ref,
    add_implementation_ref,
    add_review_ref,
    create_case,
)


class QualityEvidenceIntegrationTests(
    unittest.TestCase
):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)

        self.traceability = (
            base / "traceability"
        )
        self.evidence = (
            base / "evidence"
        )

        create_case(
            self.traceability,
            case_id="TC-001",
            matrix_ref=(
                "matriz.xlsx#Casos!R2"
            ),
        )

        add_ef_ref(
            self.traceability,
            "TC-001",
            "EF.docx#paragraph-4",
        )

        add_et_ref(
            self.traceability,
            "TC-001",
            "ET.docx#paragraph-3",
        )

        add_implementation_ref(
            self.traceability,
            "TC-001",
            "tests/login.spec.ts#TC-001",
        )

        add_execution_ref(
            self.traceability,
            "TC-001",
            (
                "results/RUN-001/"
                "TC-001/1/result.json"
            ),
        )

        add_evidence_ref(
            self.traceability,
            "TC-001",
            (
                "evidence/RUN-001/"
                "TC-001/1/manifest.json"
            ),
        )

        add_review_ref(
            self.traceability,
            "TC-001",
            "reviews/TC-001.json",
        )

        create_manifest(
            self.evidence,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

    def tearDown(self):
        self.temp.cleanup()

    def _add_trace(self):
        directory = (
            self.evidence
            / "RUN-001"
            / "TC-001"
            / "1"
        )

        trace = directory / "trace.zip"

        trace.write_bytes(
            b"valid-playwright-trace"
        )

        register_file(
            self.evidence,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            evidence_type="TRACE",
            file_path=trace,
        )

        return trace

    def test_real_evidence_allows_pass(self):
        self._add_trace()

        result = evaluate_case_with_evidence(
            traceability_root=(
                self.traceability
            ),
            evidence_root=self.evidence,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            execution_status=(
                ExecutionStatus.PASS
            ),
            review_status=(
                ReviewStatus.PASS
            ),
        )

        self.assertTrue(
            result.passed
        )

    def test_missing_trace_blocks_pass(self):
        result = evaluate_case_with_evidence(
            traceability_root=(
                self.traceability
            ),
            evidence_root=self.evidence,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            execution_status=(
                ExecutionStatus.PASS
            ),
            review_status=(
                ReviewStatus.PASS
            ),
        )

        self.assertFalse(
            result.passed
        )

        self.assertIn(
            (
                "evidence_"
                "required_type_missing=TRACE"
            ),
            result.reasons,
        )

    def test_tampered_trace_blocks_pass(self):
        trace = self._add_trace()

        trace.write_bytes(
            b"modified-after-registration"
        )

        result = evaluate_case_with_evidence(
            traceability_root=(
                self.traceability
            ),
            evidence_root=self.evidence,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            execution_status=(
                ExecutionStatus.PASS
            ),
            review_status=(
                ReviewStatus.PASS
            ),
        )

        self.assertFalse(
            result.passed
        )


if __name__ == "__main__":
    unittest.main()

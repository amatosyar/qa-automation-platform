import json
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
from core.integrity import (
    validate_execution_integrity,
)
from core.quality.gate import (
    evaluate_verified_case,
)
from core.results.model import (
    create_result,
    save_result,
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


class ExecutionIntegrityTests(
    unittest.TestCase
):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)

        self.results = base
        self.evidence = base / "evidence"
        self.traceability = (
            base / "traceability"
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

        result = create_result(
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            status=ExecutionStatus.PASS,
            duration_ms=1000,
            environment="QA",
            browser="chromium",
        )

        save_result(
            self.results,
            result,
        )

        create_manifest(
            self.evidence,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

        directory = (
            self.evidence
            / "RUN-001"
            / "TC-001"
            / "1"
        )

        trace = directory / "trace.zip"

        trace.write_bytes(
            b"valid-trace"
        )

        register_file(
            self.evidence,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            evidence_type="TRACE",
            file_path=trace,
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_integrity_passes_for_matching_execution(self):
        result = validate_execution_integrity(
            results_root=self.results,
            evidence_root=self.evidence,
            traceability_root=(
                self.traceability
            ),
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

        self.assertTrue(
            result["valid"]
        )

    def test_wrong_traceability_result_ref_is_rejected(self):
        path = (
            self.traceability
            / "cases"
            / "TC-001.json"
        )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        data["execution_refs"] = [
            (
                "results/RUN-999/"
                "TC-001/1/result.json"
            )
        ]

        path.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

        result = validate_execution_integrity(
            results_root=self.results,
            evidence_root=self.evidence,
            traceability_root=(
                self.traceability
            ),
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

        self.assertFalse(
            result["valid"]
        )

        self.assertIn(
            (
                "traceability_"
                "execution_ref_mismatch"
            ),
            result["findings"],
        )

    def test_wrong_evidence_ref_is_rejected(self):
        path = (
            self.traceability
            / "cases"
            / "TC-001.json"
        )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        data["evidence_refs"] = [
            (
                "evidence/RUN-999/"
                "TC-001/1/manifest.json"
            )
        ]

        path.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

        result = validate_execution_integrity(
            results_root=self.results,
            evidence_root=self.evidence,
            traceability_root=(
                self.traceability
            ),
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

        self.assertFalse(
            result["valid"]
        )

    def test_verified_gate_reads_real_result(self):
        result = evaluate_verified_case(
            traceability_root=(
                self.traceability
            ),
            evidence_root=self.evidence,
            results_root=self.results,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            review_status=(
                ReviewStatus.PASS
            ),
        )

        self.assertTrue(
            result.passed
        )

    def test_failed_result_cannot_be_overridden(self):
        result_path = (
            self.results
            / "results"
            / "RUN-001"
            / "TC-001"
            / "1"
            / "result.json"
        )

        data = json.loads(
            result_path.read_text(
                encoding="utf-8"
            )
        )

        data["status"] = "FAIL"

        result_path.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

        result = evaluate_verified_case(
            traceability_root=(
                self.traceability
            ),
            evidence_root=self.evidence,
            results_root=self.results,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            review_status=(
                ReviewStatus.PASS
            ),
        )

        self.assertFalse(
            result.passed
        )

        self.assertIn(
            "execution_status=FAIL",
            result.reasons,
        )

    def test_tampered_evidence_blocks_verified_gate(self):
        trace = (
            self.evidence
            / "RUN-001"
            / "TC-001"
            / "1"
            / "trace.zip"
        )

        trace.write_bytes(
            b"tampered"
        )

        result = evaluate_verified_case(
            traceability_root=(
                self.traceability
            ),
            evidence_root=self.evidence,
            results_root=self.results,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            review_status=(
                ReviewStatus.PASS
            ),
        )

        self.assertFalse(
            result.passed
        )

        self.assertIn(
            "execution_integrity_failed",
            result.reasons,
        )


if __name__ == "__main__":
    unittest.main()

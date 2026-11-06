from pathlib import Path
import unittest

from core.paths import (
    evidence_attempt_dir,
    evidence_manifest_path,
    evidence_manifest_ref,
    result_path,
    result_ref,
    traceability_case_path,
)


class CanonicalPathTests(unittest.TestCase):

    def test_result_path(self):
        self.assertEqual(
            result_path(
                Path("/project"),
                run_id="RUN-001",
                case_id="TC-001",
                attempt=2,
            ),
            Path(
                "/project/results/"
                "RUN-001/TC-001/2/result.json"
            ),
        )

    def test_result_ref(self):
        self.assertEqual(
            result_ref(
                run_id="RUN-001",
                case_id="TC-001",
                attempt=2,
            ),
            (
                "results/RUN-001/"
                "TC-001/2/result.json"
            ),
        )

    def test_evidence_attempt_dir(self):
        self.assertEqual(
            evidence_attempt_dir(
                Path("/project/evidence"),
                run_id="RUN-001",
                case_id="TC-001",
                attempt=2,
            ),
            Path(
                "/project/evidence/"
                "RUN-001/TC-001/2"
            ),
        )

    def test_evidence_manifest_path(self):
        self.assertEqual(
            evidence_manifest_path(
                Path("/project/evidence"),
                run_id="RUN-001",
                case_id="TC-001",
                attempt=2,
            ),
            Path(
                "/project/evidence/"
                "RUN-001/TC-001/2/manifest.json"
            ),
        )

    def test_evidence_manifest_ref(self):
        self.assertEqual(
            evidence_manifest_ref(
                run_id="RUN-001",
                case_id="TC-001",
                attempt=2,
            ),
            (
                "evidence/RUN-001/"
                "TC-001/2/manifest.json"
            ),
        )

    def test_traceability_case_path(self):
        self.assertEqual(
            traceability_case_path(
                Path("/project/traceability"),
                case_id="TC-001",
            ),
            Path(
                "/project/traceability/"
                "cases/TC-001.json"
            ),
        )


if __name__ == "__main__":
    unittest.main()

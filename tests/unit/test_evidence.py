from pathlib import Path
import tempfile
import unittest

from core.common.exceptions import EvidenceError
from core.evidence import (
    EvidenceRequirement,
    create_manifest,
    read_manifest,
    register_file,
    validate_manifest,
)


class EvidenceTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = (
            Path(self.temp.name)
            / "evidence"
        )

        create_manifest(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

    def tearDown(self):
        self.temp.cleanup()

    def _create_file(
        self,
        name: str,
        content: bytes = b"evidence",
    ) -> Path:
        directory = (
            self.root
            / "RUN-001"
            / "TC-001"
            / "1"
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = directory / name
        path.write_bytes(content)

        return path

    def test_manifest_identity(self):
        manifest = read_manifest(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

        self.assertEqual(
            manifest["run_id"],
            "RUN-001",
        )

        self.assertEqual(
            manifest["case_id"],
            "TC-001",
        )

        self.assertEqual(
            manifest["attempt"],
            1,
        )

    def test_register_real_file(self):
        trace = self._create_file(
            "trace.zip"
        )

        manifest = register_file(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            evidence_type="TRACE",
            file_path=trace,
        )

        self.assertEqual(
            len(manifest["items"]),
            1,
        )

        item = manifest["items"][0]

        self.assertEqual(
            item["type"],
            "TRACE",
        )

        self.assertTrue(
            item["sha256"]
        )

    def test_missing_physical_file_is_rejected(self):
        with self.assertRaises(
            EvidenceError
        ):
            register_file(
                self.root,
                run_id="RUN-001",
                case_id="TC-001",
                attempt=1,
                evidence_type="TRACE",
                file_path=(
                    self.root
                    / "missing.zip"
                ),
            )

    def test_default_profile_requires_trace(self):
        screenshot = self._create_file(
            "screen.png"
        )

        register_file(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            evidence_type="SCREENSHOT",
            file_path=screenshot,
        )

        result = validate_manifest(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

        self.assertFalse(
            result["complete"]
        )

        self.assertIn(
            "required_type_missing=TRACE",
            result["findings"],
        )

    def test_valid_trace_completes_default_profile(self):
        trace = self._create_file(
            "trace.zip"
        )

        register_file(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            evidence_type="TRACE",
            file_path=trace,
        )

        result = validate_manifest(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

        self.assertTrue(
            result["complete"]
        )

        self.assertEqual(
            result["findings"],
            [],
        )

    def test_tampered_evidence_is_detected(self):
        trace = self._create_file(
            "trace.zip"
        )

        register_file(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            evidence_type="TRACE",
            file_path=trace,
        )

        trace.write_bytes(
            b"tampered-evidence"
        )

        result = validate_manifest(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
        )

        self.assertFalse(
            result["complete"]
        )

        self.assertTrue(
            any(
                finding.startswith(
                    (
                        "size_mismatch=",
                        "sha256_mismatch=",
                    )
                )
                for finding
                in result["findings"]
            )
        )

    def test_custom_profile(self):
        screenshot = self._create_file(
            "screen.png"
        )

        register_file(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            evidence_type="SCREENSHOT",
            file_path=screenshot,
        )

        requirement = EvidenceRequirement(
            required_types=(
                "SCREENSHOT",
            ),
        )

        result = validate_manifest(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            requirement=requirement,
        )

        self.assertTrue(
            result["complete"]
        )

    def test_any_of_profile(self):
        screenshot = self._create_file(
            "screen.png"
        )

        register_file(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            evidence_type="SCREENSHOT",
            file_path=screenshot,
        )

        requirement = EvidenceRequirement(
            required_types=(),
            require_any_of=(
                "SCREENSHOT",
                "VIDEO",
            ),
        )

        result = validate_manifest(
            self.root,
            run_id="RUN-001",
            case_id="TC-001",
            attempt=1,
            requirement=requirement,
        )

        self.assertTrue(
            result["complete"]
        )


if __name__ == "__main__":
    unittest.main()

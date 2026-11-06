from pathlib import Path
import tempfile
import unittest

from core.common.exceptions import TraceabilityError
from core.traceability import (
    add_ef_ref,
    add_et_ref,
    add_evidence_ref,
    add_execution_ref,
    add_implementation_ref,
    add_knowledge_ref,
    add_review_ref,
    completeness,
    create_case,
    read_case,
    validate_reference_shapes,
)


class TraceabilityTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = (
            Path(self.temp.name)
            / "traceability"
        )

    def tearDown(self):
        self.temp.cleanup()

    def _create(self):
        return create_case(
            self.root,
            case_id="TC-001",
            matrix_ref="matriz.xlsx#Casos!R2",
        )

    def test_create_case_preserves_matrix_ref(self):
        record = self._create()

        self.assertEqual(
            record["case_id"],
            "TC-001",
        )

        self.assertEqual(
            record["matrix_ref"],
            "matriz.xlsx#Casos!R2",
        )

    def test_duplicate_case_is_rejected(self):
        self._create()

        with self.assertRaises(
            TraceabilityError
        ):
            self._create()

    def test_references_are_unique(self):
        self._create()

        add_ef_ref(
            self.root,
            "TC-001",
            "EF.docx#paragraph-4",
        )

        add_ef_ref(
            self.root,
            "TC-001",
            "EF.docx#paragraph-4",
        )

        record = read_case(
            self.root,
            "TC-001",
        )

        self.assertEqual(
            record["ef_refs"],
            ["EF.docx#paragraph-4"],
        )

    def test_incomplete_case_reports_missing(self):
        self._create()

        result = completeness(
            self.root,
            "TC-001",
        )

        self.assertFalse(
            result["complete"]
        )

        self.assertIn(
            "ef",
            result["missing"],
        )

        self.assertIn(
            "implementation",
            result["missing"],
        )

        self.assertIn(
            "evidence",
            result["missing"],
        )

    def test_complete_case(self):
        self._create()

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

        add_knowledge_ref(
            self.root,
            "TC-001",
            "KNOW-0001",
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

        result = completeness(
            self.root,
            "TC-001",
            require_knowledge=True,
        )

        self.assertTrue(
            result["complete"]
        )

        self.assertEqual(
            result["missing"],
            [],
        )

    def test_knowledge_can_be_optional(self):
        self._create()

        add_ef_ref(
            self.root,
            "TC-001",
            "EF.docx#paragraph-4",
        )

        add_et_ref(
            self.root,
            "TC-001",
            "ET.docx#paragraph-3",
        )

        add_implementation_ref(
            self.root,
            "TC-001",
            "tests/test.spec.ts#TC-001",
        )

        add_execution_ref(
            self.root,
            "TC-001",
            "results/result.json",
        )

        add_evidence_ref(
            self.root,
            "TC-001",
            "evidence/trace.zip",
        )

        add_review_ref(
            self.root,
            "TC-001",
            "reviews/TC-001.json",
        )

        result = completeness(
            self.root,
            "TC-001",
            require_knowledge=False,
        )

        self.assertTrue(
            result["complete"]
        )

    def test_bad_document_reference_is_detected(self):
        create_case(
            self.root,
            case_id="TC-001",
            matrix_ref="matriz.xlsx",
        )

        add_ef_ref(
            self.root,
            "TC-001",
            "EF.docx",
        )

        result = validate_reference_shapes(
            self.root,
            "TC-001",
        )

        self.assertFalse(
            result["valid"]
        )

        self.assertEqual(
            len(result["findings"]),
            2,
        )


if __name__ == "__main__":
    unittest.main()

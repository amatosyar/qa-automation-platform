from pathlib import Path
import json
import tempfile
import unittest

import openpyxl
from docx import Document

from core.bootstrap import (
    BootstrapError,
    bootstrap_project,
)


class BootstrapTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

        self.matrix = (
            self.root / "source-matrix.xlsx"
        )
        self.ef = (
            self.root / "source-ef.docx"
        )
        self.et = (
            self.root / "source-et.docx"
        )

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Casos"

        sheet.append(
            [
                "ID",
                "Descripcion",
                "Resultado Esperado",
            ]
        )

        sheet.append(
            [
                "TC-001",
                "Login",
                "Acceso permitido",
            ]
        )

        workbook.save(
            self.matrix
        )
        workbook.close()

        ef = Document()
        ef.add_heading(
            "EF",
            level=1,
        )
        ef.add_paragraph(
            "Regla funcional."
        )
        ef.save(self.ef)

        et = Document()
        et.add_heading(
            "ET",
            level=1,
        )
        et.add_paragraph(
            "Regla técnica."
        )
        et.save(self.et)

        self.project = (
            self.root
            / "consumer"
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_creates_project_structure(self):
        bootstrap_project(
            project_root=self.project,
            matrix=self.matrix,
            ef=self.ef,
            et=self.et,
        )

        expected = (
            "documents/original",
            "documents/normalized",
            "tests",
            "pages",
            "components",
            "fixtures",
            "data",
            "utils",
            "knowledge",
            "traceability/cases",
            "evidence",
            "results",
            "reviews",
        )

        for directory in expected:
            self.assertTrue(
                (
                    self.project
                    / directory
                ).is_dir()
            )

    def test_preserves_originals(self):
        original_matrix = (
            self.matrix.read_bytes()
        )

        original_ef = (
            self.ef.read_bytes()
        )

        original_et = (
            self.et.read_bytes()
        )

        bootstrap_project(
            project_root=self.project,
            matrix=self.matrix,
            ef=self.ef,
            et=self.et,
        )

        self.assertEqual(
            (
                self.project
                / "documents/original/matriz.xlsx"
            ).read_bytes(),
            original_matrix,
        )

        self.assertEqual(
            (
                self.project
                / "documents/original/EF.docx"
            ).read_bytes(),
            original_ef,
        )

        self.assertEqual(
            (
                self.project
                / "documents/original/ET.docx"
            ).read_bytes(),
            original_et,
        )

    def test_creates_normalized_artifacts(self):
        bootstrap_project(
            project_root=self.project,
            matrix=self.matrix,
            ef=self.ef,
            et=self.et,
        )

        normalized = (
            self.project
            / "documents"
            / "normalized"
        )

        self.assertTrue(
            (
                normalized
                / "matrix.normalized.json"
            ).is_file()
        )

        self.assertTrue(
            (
                normalized
                / "ef.normalized.json"
            ).is_file()
        )

        self.assertTrue(
            (
                normalized
                / "et.normalized.json"
            ).is_file()
        )

    def test_initializes_knowledge(self):
        bootstrap_project(
            project_root=self.project,
            matrix=self.matrix,
            ef=self.ef,
            et=self.et,
        )

        self.assertTrue(
            (
                self.project
                / "knowledge/index.json"
            ).is_file()
        )

    def test_creates_bootstrap_marker(self):
        bootstrap_project(
            project_root=self.project,
            matrix=self.matrix,
            ef=self.ef,
            et=self.et,
        )

        marker = (
            self.project
            / ".qa-platform"
            / "bootstrap.json"
        )

        self.assertTrue(
            marker.is_file()
        )

        metadata = json.loads(
            marker.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            metadata["sources"]["matrix"],
            (
                "documents/original/"
                "matriz.xlsx"
            ),
        )

    def test_rebootstrap_requires_force(self):
        bootstrap_project(
            project_root=self.project,
            matrix=self.matrix,
            ef=self.ef,
            et=self.et,
        )

        with self.assertRaises(
            BootstrapError
        ):
            bootstrap_project(
                project_root=self.project,
                matrix=self.matrix,
                ef=self.ef,
                et=self.et,
            )

    def test_missing_source_is_rejected(self):
        with self.assertRaises(
            BootstrapError
        ):
            bootstrap_project(
                project_root=self.project,
                matrix=(
                    self.root
                    / "missing.xlsx"
                ),
                ef=self.ef,
                et=self.et,
            )


if __name__ == "__main__":
    unittest.main()

import hashlib
from pathlib import Path
import tempfile
import unittest

from core.artifacts import (
    ArtifactType,
    extract_docx,
    extract_matrix,
    normalize_artifacts,
)
from core.common.exceptions import ArtifactError


try:
    import openpyxl
    from docx import Document
except ImportError:
    openpyxl = None
    Document = None


@unittest.skipIf(
    openpyxl is None or Document is None,
    "Dependencias de Artifact Engine no instaladas",
)
class ArtifactEngineTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def _create_matrix(self) -> Path:
        path = self.root / "matriz.xlsx"

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Casos"

        sheet.append(
            [
                "ID",
                "Descripción",
                "Resultado Esperado",
            ]
        )

        sheet.append(
            [
                "TC-001",
                "Login válido",
                "Acceso permitido",
            ]
        )

        workbook.save(path)
        workbook.close()

        return path

    def _create_docx(
        self,
        filename: str,
        heading: str,
    ) -> Path:
        path = self.root / filename

        document = Document()
        document.add_heading(
            heading,
            level=1,
        )
        document.add_paragraph(
            "Contenido verificable."
        )

        table = document.add_table(
            rows=2,
            cols=2,
        )

        table.cell(0, 0).text = "Campo"
        table.cell(0, 1).text = "Valor"
        table.cell(1, 0).text = "Estado"
        table.cell(1, 1).text = "Activo"

        document.save(path)

        return path

    def test_matrix_preserves_rows(self):
        matrix = self._create_matrix()

        artifact = extract_matrix(matrix)

        self.assertEqual(
            artifact.artifact_type,
            ArtifactType.MATRIX,
        )

        self.assertEqual(
            artifact.content["sheets"][0]["name"],
            "Casos",
        )

        rows = artifact.content[
            "sheets"
        ][0]["rows"]

        self.assertEqual(
            rows[1]["values"][0],
            "TC-001",
        )

    def test_docx_preserves_paragraphs_and_tables(self):
        ef = self._create_docx(
            "EF.docx",
            "Especificación Funcional",
        )

        artifact = extract_docx(
            ef,
            ArtifactType.EF,
        )

        self.assertTrue(
            artifact.content["paragraphs"]
        )

        self.assertTrue(
            artifact.content["tables"]
        )

    def test_normalize_creates_three_outputs(self):
        matrix = self._create_matrix()
        ef = self._create_docx(
            "EF.docx",
            "EF",
        )
        et = self._create_docx(
            "ET.docx",
            "ET",
        )

        output = self.root / "normalized"

        result = normalize_artifacts(
            matrix=matrix,
            ef=ef,
            et=et,
            output_dir=output,
        )

        self.assertEqual(
            set(result),
            {"MATRIX", "EF", "ET"},
        )

        for path in result.values():
            self.assertTrue(
                path.is_file()
            )

    def test_source_hash_is_real(self):
        matrix = self._create_matrix()

        artifact = extract_matrix(matrix)

        expected = hashlib.sha256(
            matrix.read_bytes()
        ).hexdigest()

        self.assertEqual(
            artifact.source_sha256,
            expected,
        )

    def test_matrix_row_has_source_reference(self):
        matrix = self._create_matrix()

        artifact = extract_matrix(matrix)

        row = artifact.content["sheets"][0]["rows"][1]
        source = row["source_ref"]

        self.assertEqual(source["file"], "matriz.xlsx")
        self.assertEqual(source["sheet"], "Casos")
        self.assertEqual(source["row"], 2)
        self.assertEqual(
            source["locator"],
            "matriz.xlsx#Casos!R2",
        )

    def test_docx_paragraph_has_source_reference(self):
        ef = self._create_docx(
            "EF.docx",
            "Especificación Funcional",
        )

        artifact = extract_docx(
            ef,
            ArtifactType.EF,
        )

        paragraph = artifact.content["paragraphs"][0]
        source = paragraph["source_ref"]

        self.assertEqual(source["file"], "EF.docx")
        self.assertEqual(
            source["locator"],
            "EF.docx#paragraph-1",
        )

    def test_docx_table_row_has_source_reference(self):
        et = self._create_docx(
            "ET.docx",
            "Especificación Técnica",
        )

        artifact = extract_docx(
            et,
            ArtifactType.ET,
        )

        row = artifact.content["tables"][0]["rows"][0]
        source = row["source_ref"]

        self.assertEqual(source["file"], "ET.docx")
        self.assertEqual(source["table"], 1)
        self.assertEqual(source["row"], 1)
        self.assertEqual(
            source["locator"],
            "ET.docx#table-1-row-1",
        )


    def test_missing_artifact_blocks_normalization(self):
        with self.assertRaises(ArtifactError):
            normalize_artifacts(
                matrix=self.root / "missing.xlsx",
                ef=self.root / "missing-ef.docx",
                et=self.root / "missing-et.docx",
                output_dir=self.root / "out",
            )


if __name__ == "__main__":
    unittest.main()

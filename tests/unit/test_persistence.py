import json
from pathlib import Path
import tempfile
import unittest

from core.common.enums import ExecutionStatus, InterventionAction
from core.intervention.model import create_record, save_record
from core.results.model import create_result, save_result


class PersistenceTests(unittest.TestCase):

    def test_execution_result_is_persisted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            result = create_result(
                run_id="RUN-001",
                case_id="TC-001",
                attempt=1,
                status=ExecutionStatus.PASS,
                duration_ms=1500,
                environment="QA",
                browser="chromium",
                evidence_refs=["evidence/trace.zip"],
            )

            path = save_result(root, result)

            self.assertTrue(path.is_file())

            saved = json.loads(
                path.read_text(encoding="utf-8")
            )

            self.assertEqual(saved["case_id"], "TC-001")
            self.assertEqual(saved["status"], "PASS")

    def test_intervention_is_persisted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            record = create_record(
                case_id="TC-002",
                attempted="Ingresar al módulo",
                found="Acceso denegado",
                needed="Permiso funcional",
                action=InterventionAction.PENDING,
            )

            path = save_record(root, record)

            self.assertTrue(path.is_file())

            saved = json.loads(
                path.read_text(encoding="utf-8")
            )

            self.assertEqual(saved["case_id"], "TC-002")
            self.assertEqual(saved["action"], "PENDING")


if __name__ == "__main__":
    unittest.main()

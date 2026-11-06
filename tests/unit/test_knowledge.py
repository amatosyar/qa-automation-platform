import json
from pathlib import Path
import tempfile
import unittest

from core.common.enums import (
    KnowledgeState,
    KnowledgeType,
)
from core.common.exceptions import KnowledgeError
from core.knowledge.memory import (
    add,
    has_query,
    invalidate,
    read,
    read_query,
    register_query,
    search,
    verify,
)


class KnowledgeTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "knowledge"

    def tearDown(self):
        self.temp.cleanup()

    def _add_rule(self, **overrides):
        data = {
            "type_": KnowledgeType.REGLA_DOCUMENTADA,
            "description": "El botón Continuar requiere datos válidos.",
            "source": "EF sección 4.2",
            "requirement_origin": "TC-001",
            "module": "pagos",
            "environment": "QA",
            "version": "1.0",
            "evidence_refs": [
                "documents/EF.docx#4.2"
            ],
        }

        data.update(overrides)

        return add(
            self.root,
            **data,
        )

    def test_new_entry_is_provisional(self):
        entry = self._add_rule()

        self.assertEqual(
            entry["state"],
            "PROVISIONAL",
        )

        self.assertIsNone(
            entry["last_verified_at"]
        )

    def test_verify_is_explicit(self):
        entry = self._add_rule()

        verified = verify(
            self.root,
            entry["id"],
        )

        self.assertEqual(
            verified["state"],
            "VERIFICADO",
        )

        self.assertIsNotNone(
            verified["last_verified_at"]
        )

    def test_search_filters_module_and_environment(self):
        self._add_rule()

        self._add_rule(
            description="Regla de otro módulo",
            module="clientes",
        )

        result = search(
            self.root,
            module="pagos",
            environment="QA",
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["module"],
            "pagos",
        )

    def test_invalidated_entry_is_not_current(self):
        entry = self._add_rule()

        invalidate(
            self.root,
            entry["id"],
            "La EF fue reemplazada.",
        )

        current = search(self.root)

        self.assertEqual(current, [])

        historical = search(
            self.root,
            current_only=False,
        )

        self.assertEqual(len(historical), 1)
        self.assertEqual(
            historical[0]["state"],
            "INVALIDADO",
        )

    def test_replacement_keeps_history(self):
        old = self._add_rule()

        new = self._add_rule(
            description="Nueva regla documentada.",
            source="EF v2 sección 4.2",
            version="2.0",
            replaces=old["id"],
        )

        previous = read(
            self.root,
            old["id"],
        )

        self.assertEqual(
            previous["state"],
            "REEMPLAZADO",
        )

        self.assertEqual(
            previous["replaced_by"],
            new["id"],
        )

        self.assertEqual(
            new["replaces"],
            old["id"],
        )

        current = search(self.root)

        self.assertEqual(len(current), 1)
        self.assertEqual(
            current[0]["id"],
            new["id"],
        )

    def test_register_query_tracks_decisions(self):
        first = self._add_rule()

        second = self._add_rule(
            description="Dato pendiente de validar.",
            type_=KnowledgeType.DUDA_PENDIENTE,
        )

        path = register_query(
            self.root,
            requirement="TC-001",
            consulted=[
                first["id"],
                second["id"],
            ],
            applied=[
                first["id"],
            ],
            discarded={
                second["id"]:
                    "No está confirmado para QA."
            },
        )

        self.assertTrue(path.is_file())
        self.assertTrue(
            has_query(
                self.root,
                "TC-001",
            )
        )

        record = read_query(
            self.root,
            "TC-001",
        )

        self.assertEqual(
            record["applied"],
            [first["id"]],
        )

        self.assertIn(
            second["id"],
            record["discarded"],
        )

    def test_cannot_apply_unconsulted_entry(self):
        first = self._add_rule()

        with self.assertRaises(KnowledgeError):
            register_query(
                self.root,
                requirement="TC-001",
                consulted=[],
                applied=[first["id"]],
                discarded={},
            )

    def test_index_is_generated(self):
        entry = self._add_rule()

        index_path = (
            self.root / "index.json"
        )

        self.assertTrue(index_path.is_file())

        index = json.loads(
            index_path.read_text(
                encoding="utf-8"
            )
        )

        self.assertIn(
            entry["id"],
            index["entries"],
        )


if __name__ == "__main__":
    unittest.main()

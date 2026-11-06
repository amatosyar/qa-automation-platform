"""Excepciones compartidas de QA Automation Platform."""


class QAPlatformError(Exception):
    """Error base del framework."""


class ArtifactError(QAPlatformError):
    """Error procesando Matriz, EF, ET u otro artefacto."""


class EvidenceError(QAPlatformError):
    """Error relacionado con evidencia de ejecución."""


class KnowledgeError(QAPlatformError):
    """Error relacionado con conocimiento persistente."""


class TraceabilityError(QAPlatformError):
    """Error relacionado con trazabilidad."""


class QualityGateError(QAPlatformError):
    """Error evaluando un Quality Gate."""


class InvalidStateTransition(QAPlatformError):
    """Transición de lifecycle no permitida."""


class InterventionRequired(QAPlatformError):
    """El flujo necesita intervención humana para continuar."""

    def __init__(
        self,
        *,
        case_id: str,
        attempted: str,
        found: str,
        needed: str,
    ) -> None:
        self.case_id = case_id
        self.attempted = attempted
        self.found = found
        self.needed = needed

        super().__init__(
            f"{case_id}: intervención requerida. "
            f"Intentaba: {attempted}. "
            f"Encontró: {found}. "
            f"Necesita: {needed}."
        )

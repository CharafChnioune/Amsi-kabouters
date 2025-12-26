"""Organization event types voor enterprise hierarchie en governance.

Dit module bevat alle event types voor organisatie-gerelateerde communicatie:
- Opdrachten (ontvangen, voltooid, geweigerd)
- Rapporten (ontvangen, gelezen)
- Escalaties (getriggerd, opgelost)
- Goedkeuringen (vereist, gegeven, afgewezen)
- Raad van Commissarissen (berichten, beslissingen)
"""

from typing import TYPE_CHECKING, Any
from uuid import UUID

from crewai.events.base_events import BaseEvent


if TYPE_CHECKING:
    from crewai.crew import Crew
    from crewai.communication.directives import Opdracht
    from crewai.communication.reports import Rapport
    from crewai.governance.escalation import Escalatie
else:
    Crew = Any
    Opdracht = Any
    Rapport = Any
    Escalatie = Any


class OrganisatieBaseEvent(BaseEvent):
    """Basis klasse voor organisatie events."""

    crew_id: UUID | None = None
    crew_naam: str | None = None
    afdeling_id: UUID | None = None
    type: str = "organization_base"

    def __init__(self, **data):
        super().__init__(**data)
        if hasattr(self, "crew") and self.crew:
            self.crew_id = getattr(self.crew, "id", None)
            self.crew_naam = getattr(self.crew, "name", None)


# === OPDRACHT EVENTS ===


class OpdrachtOntvangenEvent(OrganisatieBaseEvent):
    """Event wanneer een crew een opdracht ontvangt van management."""

    opdracht: Opdracht | None = None
    opdracht_id: UUID | None = None
    opdracht_titel: str | None = None
    van_id: UUID | None = None
    prioriteit: str | None = None
    type: str = "opdracht_ontvangen"

    def __init__(self, **data):
        super().__init__(**data)
        if self.opdracht:
            self.opdracht_id = getattr(self.opdracht, "id", None)
            self.opdracht_titel = getattr(self.opdracht, "titel", None)
            self.van_id = getattr(self.opdracht, "van_id", None)
            self.prioriteit = str(getattr(self.opdracht, "prioriteit", "normaal"))

    def to_json(self, exclude: set[str] | None = None):
        if exclude is None:
            exclude = set()
        exclude.add("opdracht")
        return super().to_json(exclude=exclude)


class OpdrachtVoltooidEvent(OrganisatieBaseEvent):
    """Event wanneer een opdracht is voltooid."""

    opdracht_id: UUID | None = None
    opdracht_titel: str | None = None
    resultaat: str | None = None
    succes: bool = True
    type: str = "opdracht_voltooid"


class OpdrachtGeweigerdEvent(OrganisatieBaseEvent):
    """Event wanneer een opdracht wordt geweigerd."""

    opdracht_id: UUID | None = None
    opdracht_titel: str | None = None
    reden: str | None = None
    type: str = "opdracht_geweigerd"


class OpdrachtGeescaleerdEvent(OrganisatieBaseEvent):
    """Event wanneer een opdracht wordt geescaleerd."""

    opdracht_id: UUID | None = None
    escalatie_reden: str | None = None
    naar_id: UUID | None = None
    type: str = "opdracht_geescaleerd"


# === RAPPORT EVENTS ===


class RapportOntvangenEvent(OrganisatieBaseEvent):
    """Event wanneer een rapport wordt ontvangen."""

    rapport: Rapport | None = None
    rapport_id: UUID | None = None
    rapport_titel: str | None = None
    van_id: UUID | None = None
    rapport_type: str | None = None
    prioriteit: str | None = None
    type: str = "rapport_ontvangen"

    def __init__(self, **data):
        super().__init__(**data)
        if self.rapport:
            self.rapport_id = getattr(self.rapport, "id", None)
            self.rapport_titel = getattr(self.rapport, "titel", None)
            self.van_id = getattr(self.rapport, "van_id", None)
            self.rapport_type = str(getattr(self.rapport, "type", "status"))
            self.prioriteit = str(getattr(self.rapport, "prioriteit", "normaal"))

    def to_json(self, exclude: set[str] | None = None):
        if exclude is None:
            exclude = set()
        exclude.add("rapport")
        return super().to_json(exclude=exclude)


class RapportVerstuurdEvent(OrganisatieBaseEvent):
    """Event wanneer een rapport wordt verstuurd."""

    rapport_id: UUID | None = None
    rapport_titel: str | None = None
    naar_ids: list[UUID] = []
    rapport_type: str | None = None
    type: str = "rapport_verstuurd"


# === ESCALATIE EVENTS ===


class EscalatieGetriggerdEvent(OrganisatieBaseEvent):
    """Event wanneer een escalatie wordt getriggerd."""

    escalatie: Escalatie | None = None
    escalatie_id: UUID | None = None
    trigger_type: str | None = None
    reden: str | None = None
    naar_id: UUID | None = None
    type: str = "escalatie_getriggerd"

    def __init__(self, **data):
        super().__init__(**data)
        if self.escalatie:
            self.escalatie_id = getattr(self.escalatie, "id", None)
            self.trigger_type = str(getattr(self.escalatie, "trigger_type", "handmatig"))
            self.reden = getattr(self.escalatie, "reden", None)
            self.naar_id = getattr(self.escalatie, "doel_id", None)

    def to_json(self, exclude: set[str] | None = None):
        if exclude is None:
            exclude = set()
        exclude.add("escalatie")
        return super().to_json(exclude=exclude)


class EscalatieOpgelostEvent(OrganisatieBaseEvent):
    """Event wanneer een escalatie wordt opgelost."""

    escalatie_id: UUID | None = None
    opgelost_door: UUID | None = None
    reactie: str | None = None
    type: str = "escalatie_opgelost"


# === GOEDKEURING EVENTS ===


class GoedkeuringVereistEvent(OrganisatieBaseEvent):
    """Event wanneer goedkeuring van RvC/management nodig is."""

    verzoek_id: UUID | None = None
    verzoek_type: str | None = None  # "opdracht", "budget", "escalatie", "strategie"
    beschrijving: str | None = None
    aanvrager_id: UUID | None = None
    aanvrager_naam: str | None = None
    type: str = "goedkeuring_vereist"


class GoedkeuringGegevenEvent(OrganisatieBaseEvent):
    """Event wanneer goedkeuring wordt gegeven."""

    verzoek_id: UUID | None = None
    goedgekeurd_door: UUID | None = None
    toelichting: str | None = None
    type: str = "goedkeuring_gegeven"


class GoedkeuringAfgewezenEvent(OrganisatieBaseEvent):
    """Event wanneer goedkeuring wordt afgewezen."""

    verzoek_id: UUID | None = None
    afgewezen_door: UUID | None = None
    reden: str | None = None
    type: str = "goedkeuring_afgewezen"


# === RAAD VAN COMMISSARISSEN EVENTS ===


class RvCBerichtOntvangenEvent(OrganisatieBaseEvent):
    """Event wanneer RvC een bericht ontvangt."""

    bericht_id: UUID | None = None
    van_crew_id: UUID | None = None
    van_crew_naam: str | None = None
    inhoud: str | None = None
    bericht_type: str | None = None  # "rapport", "vraag", "escalatie"
    type: str = "rvc_bericht_ontvangen"


class RvCOpdrachtGegevenEvent(OrganisatieBaseEvent):
    """Event wanneer RvC een opdracht geeft."""

    opdracht_id: UUID | None = None
    naar_id: UUID | None = None
    naar_naam: str | None = None
    opdracht_titel: str | None = None
    prioriteit: str | None = None
    type: str = "rvc_opdracht_gegeven"


class RvCBeslissingEvent(OrganisatieBaseEvent):
    """Event wanneer RvC een beslissing neemt."""

    verzoek_id: UUID | None = None
    beslissing: str | None = None  # "goedgekeurd", "afgewezen", "aangepast"
    toelichting: str | None = None
    type: str = "rvc_beslissing"


# === PERMISSIE EVENTS ===


class PermissieGeweigerdEvent(OrganisatieBaseEvent):
    """Event wanneer een actie wordt geweigerd door permissie check."""

    agent_id: UUID | None = None
    agent_naam: str | None = None
    resource_type: str | None = None  # "tool", "crew", "agent"
    resource_id: UUID | str | None = None
    actie: str | None = None  # "uitvoeren", "lezen", "schrijven"
    reden: str | None = None
    type: str = "permissie_geweigerd"


class PermissieToegestaanEvent(OrganisatieBaseEvent):
    """Event wanneer een actie wordt toegestaan (voor audit)."""

    agent_id: UUID | None = None
    resource_type: str | None = None
    resource_id: UUID | str | None = None
    actie: str | None = None
    type: str = "permissie_toegestaan"

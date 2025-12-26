"""Raad van Commissarissen - Menselijke toezicht interface.

Deze module implementeert de hoogste autoriteit in de organisatie:
de menselijke gebruiker die als Raad van Commissarissen functioneert.

De RvC kan:
- Berichten sturen naar de organisatie
- Opdrachten geven aan crews/agents
- Rapporten ontvangen
- Goedkeuren of afwijzen van kritieke beslissingen
- De organisatie bijsturen

Voorbeeld:
    ```python
    from crewai.governance import RaadVanCommissarissen

    # Setup
    rvc = RaadVanCommissarissen(organisatie=org)

    # Via chat bijsturen
    rvc.verwerk_gebruiker_bericht("@trading: stop alle BTC posities")
    rvc.verwerk_gebruiker_bericht("@risk: wat is de huidige exposure?")

    # Rapporten bekijken
    for rapport in rvc.krijg_rapporten(alleen_ongelezen=True):
        print(f"{rapport.titel}: {rapport.samenvatting}")

    # Goedkeuringen afhandelen
    for verzoek in rvc.krijg_wachtende_goedkeuringen():
        rvc.keur_goed(verzoek.id, "Akkoord")
    ```
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Literal, TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.organization_events import (
    RvCOpdrachtGegevenEvent,
    RvCBeslissingEvent,
    RvCBerichtOntvangenEvent,
    GoedkeuringVereistEvent,
)


if TYPE_CHECKING:
    from crewai.organization.hierarchy import OrganisatieHierarchie
    from crewai.organization.role import Rol, PermissieNiveau
    from crewai.communication.directives import OpdrachtManager, OpdrachtPrioriteit
    from crewai.communication.reports import RapportManager, Rapport


class GoedkeuringsStatus(str, Enum):
    """Status van een goedkeuringsverzoek."""

    WACHTEND = "wachtend"
    """Wacht op beslissing van de RvC."""

    GOEDGEKEURD = "goedgekeurd"
    """Goedgekeurd door de RvC."""

    AFGEWEZEN = "afgewezen"
    """Afgewezen door de RvC."""

    AANGEPAST = "aangepast"
    """Goedgekeurd met aanpassingen."""


class GoedkeuringsVerzoek(BaseModel):
    """Verzoek dat goedkeuring vereist van de RvC.

    Attributes:
        id: Unieke identifier voor het verzoek.
        type: Type verzoek (opdracht, escalatie, budget, strategie).
        beschrijving: Beschrijving van wat goedgekeurd moet worden.
        aanvrager_id: ID van de crew/agent die om goedkeuring vraagt.
        aanvrager_naam: Naam van de aanvrager.
        details: Extra details over het verzoek.
        status: Huidige status van het verzoek.
        aangevraagd_op: Tijdstip van aanvraag.
        besloten_op: Tijdstip van beslissing (indien genomen).
        beslissing_toelichting: Toelichting bij de beslissing.
    """

    id: UUID = Field(default_factory=uuid4)
    type: Literal["opdracht", "escalatie", "budget", "strategie"] = Field(...)
    beschrijving: str = Field(...)
    aanvrager_id: UUID = Field(...)
    aanvrager_naam: str = Field(default="Onbekend")
    details: dict[str, Any] = Field(default_factory=dict)

    status: GoedkeuringsStatus = Field(default=GoedkeuringsStatus.WACHTEND)
    aangevraagd_op: datetime = Field(default_factory=datetime.utcnow)
    besloten_op: datetime | None = Field(default=None)
    beslissing_toelichting: str | None = Field(default=None)


class RvCBericht(BaseModel):
    """Bericht van/naar de Raad van Commissarissen.

    Attributes:
        id: Unieke identifier.
        richting: Of het bericht naar of van de RvC gaat.
        type: Type bericht (opdracht, rapport, vraag, antwoord, notificatie).
        inhoud: Inhoud van het bericht.
        gerelateerd_aan: Optionele ID van gerelateerde crew/agent.
        context: Extra context informatie.
        tijdstip: Tijdstip van het bericht.
        gelezen: Of het bericht is gelezen.
    """

    id: UUID = Field(default_factory=uuid4)
    richting: Literal["naar_rvc", "van_rvc"] = Field(...)
    type: Literal["opdracht", "rapport", "vraag", "antwoord", "notificatie"] = Field(...)
    inhoud: str = Field(...)
    gerelateerd_aan: UUID | None = Field(default=None)
    context: dict[str, Any] = Field(default_factory=dict)
    tijdstip: datetime = Field(default_factory=datetime.utcnow)
    gelezen: bool = Field(default=False)


class RaadVanCommissarissen(BaseModel):
    """Centrale interface voor menselijk toezicht.

    De RvC functioneert als hoogste autoriteit met BESTUUR niveau
    en kan:
    - Opdrachten geven aan alle crews
    - Rapporten ontvangen van alle crews
    - Goedkeuring geven voor kritieke acties
    - De organisatie bijsturen

    Attributes:
        id: Unieke identifier voor de RvC.
        naam: Naam van de RvC (standaard "Raad van Commissarissen").
        organisatie: Referentie naar de organisatie hierarchie.
        opdracht_manager: Manager voor opdrachten.
        rapport_manager: Manager voor rapporten.
        berichten: Lijst met alle berichten.
        goedkeurings_verzoeken: Alle goedkeuringsverzoeken.
        crews: Geregistreerde crews (naam -> id mapping).
        on_nieuw_rapport: Callback voor nieuwe rapporten.
        on_goedkeuring_vereist: Callback voor goedkeuringsverzoeken.
        on_escalatie: Callback voor escalaties.

    Example:
        ```python
        from crewai.governance import RaadVanCommissarissen

        rvc = RaadVanCommissarissen(organisatie=org)

        # Geef opdracht
        rvc.verwerk_gebruiker_bericht("@trading: analyseer EUR/USD trend")

        # Bekijk status
        print(rvc.krijg_samenvatting())
        ```
    """

    model_config = {"arbitrary_types_allowed": True}

    id: UUID = Field(default_factory=uuid4)
    naam: str = Field(default="Raad van Commissarissen")

    # Organisatie koppeling
    organisatie: Any | None = Field(default=None)

    # Managers
    opdracht_manager: Any | None = Field(default=None)
    rapport_manager: Any | None = Field(default=None)

    # Berichten queue
    berichten: list[RvCBericht] = Field(default_factory=list)

    # Goedkeuringen
    goedkeurings_verzoeken: dict[UUID, GoedkeuringsVerzoek] = Field(default_factory=dict)

    # Geregistreerde crews (naam -> crew/id)
    crews: dict[str, Any] = Field(default_factory=dict)

    # Callbacks voor UI integratie
    on_nieuw_rapport: Callable[[Any], None] | None = Field(default=None, exclude=True)
    on_goedkeuring_vereist: Callable[[GoedkeuringsVerzoek], None] | None = Field(
        default=None, exclude=True
    )
    on_escalatie: Callable[[Any], None] | None = Field(default=None, exclude=True)
    on_bericht: Callable[[RvCBericht], None] | None = Field(default=None, exclude=True)

    def model_post_init(self, __context: Any) -> None:
        """Initialiseer de RvC na model creatie."""
        # Registreer bij organisatie met BESTUUR niveau
        if self.organisatie is not None:
            try:
                from crewai.organization.role import Rol, PermissieNiveau

                rol = Rol(
                    naam="Raad van Commissarissen",
                    beschrijving="Hoogste toezichthoudend orgaan - menselijke gebruiker",
                    niveau=PermissieNiveau.BESTUUR,
                    kan_delegeren=True,
                    kan_goedkeuren=True,
                    kan_opdrachten_geven=True,
                    kan_rapporten_ontvangen=True,
                    ontvangt_opdrachten_van=[],  # Niemand geeft RvC opdrachten
                )

                # Registreer rol bij organisatie
                if hasattr(self.organisatie, "wijs_rol_toe"):
                    self.organisatie.wijs_rol_toe(self.id, rol)

            except ImportError:
                pass

    # ============================================================
    # BERICHT VERWERKING
    # ============================================================

    def verwerk_gebruiker_bericht(self, bericht: str) -> str:
        """Verwerk een bericht/opdracht van de gebruiker.

        Parseert het bericht en vertaalt het naar:
        - Opdracht aan specifieke crew (bijv. "@trading: stop posities")
        - Vraag om status (bijv. "status?" of "hoe gaat het?")
        - Goedkeuring/afwijzing (bijv. "akkoord" of "afwijzen #123")
        - Algemeen bericht

        Args:
            bericht: Tekst bericht van de gebruiker.

        Returns:
            Bevestiging of resultaat van de actie.

        Example:
            ```python
            # Geef opdracht aan trading crew
            result = rvc.verwerk_gebruiker_bericht("@trading: stop alle BTC posities")

            # Vraag om status
            result = rvc.verwerk_gebruiker_bericht("status?")

            # Keur goed
            result = rvc.verwerk_gebruiker_bericht("akkoord")
            ```
        """
        # Log het bericht
        self._log_bericht(
            richting="van_rvc",
            type="opdracht",
            inhoud=bericht,
        )

        # Parse het bericht
        actie = self._parse_bericht(bericht)

        if actie["type"] == "opdracht":
            return self._geef_opdracht_vanuit_bericht(actie)
        elif actie["type"] == "vraag":
            return self._beantwoord_vraag(actie)
        elif actie["type"] == "goedkeuring":
            return self._verwerk_goedkeuring(actie)
        else:
            return self._verwerk_algemeen(actie)

    def _parse_bericht(self, bericht: str) -> dict[str, Any]:
        """Parse gebruikersbericht naar gestructureerde actie.

        Detecteert patronen zoals:
        - "@trading: <opdracht>" -> opdracht aan trading crew
        - "status?" -> vraag om status
        - "akkoord/goedkeuren #123" -> goedkeuring

        Args:
            bericht: Het te parsen bericht.

        Returns:
            Dictionary met type en details van de actie.
        """
        # Check voor crew adressering: @crew: opdracht
        crew_match = re.match(r"@(\w+)[:\s]+(.+)", bericht, re.IGNORECASE | re.DOTALL)
        if crew_match:
            return {
                "type": "opdracht",
                "doel": crew_match.group(1).strip(),
                "inhoud": crew_match.group(2).strip(),
            }

        # Check voor goedkeuring
        goedkeuring_match = re.match(
            r"(akkoord|goedkeuren|approve|ja|yes)\s*(?:#?(\d+|[\w-]+))?",
            bericht.strip(),
            re.IGNORECASE,
        )
        if goedkeuring_match:
            return {
                "type": "goedkeuring",
                "beslissing": "goedkeuren",
                "verzoek_ref": goedkeuring_match.group(2),
                "inhoud": bericht,
            }

        # Check voor afwijzing
        afwijzing_match = re.match(
            r"(afwijzen|weigeren|reject|nee|no)\s*(?:#?(\d+|[\w-]+))?",
            bericht.strip(),
            re.IGNORECASE,
        )
        if afwijzing_match:
            return {
                "type": "goedkeuring",
                "beslissing": "afwijzen",
                "verzoek_ref": afwijzing_match.group(2),
                "inhoud": bericht,
            }

        # Check voor status vraag
        status_keywords = ["status", "hoe gaat", "voortgang", "update", "rapport"]
        if any(kw in bericht.lower() for kw in status_keywords) or bericht.strip().endswith("?"):
            return {
                "type": "vraag",
                "inhoud": bericht,
            }

        return {
            "type": "algemeen",
            "inhoud": bericht,
        }

    def _geef_opdracht_vanuit_bericht(self, actie: dict[str, Any]) -> str:
        """Vertaal een bericht naar een formele opdracht.

        Args:
            actie: Geparseerde actie met doel en inhoud.

        Returns:
            Bevestiging of foutmelding.
        """
        doel_naam = actie["doel"]
        opdracht_tekst = actie["inhoud"]

        # Zoek doel crew
        doel_id = self._zoek_doel(doel_naam)
        if doel_id is None:
            return f"Kon '{doel_naam}' niet vinden. Beschikbare crews: {', '.join(self.crews.keys()) or 'geen'}"

        # Geef opdracht
        return self.geef_opdracht(
            naar_id=doel_id,
            titel=opdracht_tekst[:100],
            beschrijving=opdracht_tekst,
        )

    def _beantwoord_vraag(self, actie: dict[str, Any]) -> str:
        """Beantwoord een vraag van de gebruiker.

        Args:
            actie: Geparseerde actie met vraag.

        Returns:
            Antwoord op de vraag.
        """
        samenvatting = self.krijg_samenvatting()

        antwoord_lines = [
            "=== Organisatie Status ===",
            f"Ongelezen rapporten: {samenvatting.get('ongelezen_rapporten', 0)}",
            f"Urgente rapporten: {samenvatting.get('urgente_rapporten', 0)}",
            f"Wachtende goedkeuringen: {samenvatting.get('wachtende_goedkeuringen', 0)}",
            f"Geregistreerde crews: {samenvatting.get('aantal_crews', 0)}",
        ]

        # Voeg wachtende goedkeuringen toe
        wachtend = self.krijg_wachtende_goedkeuringen()
        if wachtend:
            antwoord_lines.append("\n=== Wachtende Goedkeuringen ===")
            for v in wachtend[:5]:  # Max 5 tonen
                antwoord_lines.append(f"- [{v.id}] {v.type}: {v.beschrijving[:50]}...")

        return "\n".join(antwoord_lines)

    def _verwerk_goedkeuring(self, actie: dict[str, Any]) -> str:
        """Verwerk een goedkeuring of afwijzing.

        Args:
            actie: Geparseerde actie met beslissing.

        Returns:
            Bevestiging van de beslissing.
        """
        beslissing = actie["beslissing"]
        verzoek_ref = actie.get("verzoek_ref")

        # Zoek het verzoek
        verzoek = None
        if verzoek_ref:
            # Zoek op (deel van) ID
            for v_id, v in self.goedkeurings_verzoeken.items():
                if str(v_id).startswith(verzoek_ref) or verzoek_ref in str(v_id):
                    verzoek = v
                    break
        else:
            # Pak het oudste wachtende verzoek
            wachtend = self.krijg_wachtende_goedkeuringen()
            if wachtend:
                verzoek = wachtend[0]

        if verzoek is None:
            return "Geen wachtend goedkeuringsverzoek gevonden."

        if beslissing == "goedkeuren":
            self.keur_goed(verzoek.id, "Goedgekeurd via chat")
            return f"Goedgekeurd: {verzoek.beschrijving[:50]}..."
        else:
            self.wijs_af(verzoek.id, "Afgewezen via chat")
            return f"Afgewezen: {verzoek.beschrijving[:50]}..."

    def _verwerk_algemeen(self, actie: dict[str, Any]) -> str:
        """Verwerk een algemeen bericht.

        Args:
            actie: Geparseerde actie.

        Returns:
            Standaard antwoord.
        """
        return (
            "Bericht ontvangen. Gebruik:\n"
            "- @crew_naam: opdracht - om opdracht te geven\n"
            "- status? - voor status overzicht\n"
            "- akkoord/afwijzen - voor goedkeuringen"
        )

    # ============================================================
    # OPDRACHTEN
    # ============================================================

    def geef_opdracht(
        self,
        naar_id: UUID,
        titel: str,
        beschrijving: str,
        prioriteit: str = "hoog",
        context: dict[str, Any] | None = None,
    ) -> str:
        """Geef een opdracht aan een crew of agent.

        Als RvC met BESTUUR niveau mag dit aan iedereen.

        Args:
            naar_id: ID van de ontvanger (crew of agent).
            titel: Korte titel van de opdracht.
            beschrijving: Volledige beschrijving.
            prioriteit: Prioriteit (laag, normaal, hoog, kritiek).
            context: Extra context informatie.

        Returns:
            Bevestiging of foutmelding.

        Example:
            ```python
            result = rvc.geef_opdracht(
                naar_id=trading_crew.id,
                titel="Analyseer markt",
                beschrijving="Maak een volledige analyse van EUR/USD",
                prioriteit="hoog"
            )
            ```
        """
        if self.opdracht_manager is None:
            # Probeer direct aan crew te geven
            crew = self._krijg_crew_by_id(naar_id)
            if crew is not None and hasattr(crew, "ontvang_opdracht"):
                try:
                    from crewai.communication.directives import Opdracht, OpdrachtPrioriteit

                    opdracht = Opdracht(
                        van_id=self.id,
                        naar_id=naar_id,
                        titel=titel,
                        beschrijving=beschrijving,
                        prioriteit=OpdrachtPrioriteit(prioriteit),
                        context=context or {},
                    )

                    crew.ontvang_opdracht(opdracht, voer_direct_uit=True)

                    # Emit event
                    crewai_event_bus.emit(
                        self,
                        RvCOpdrachtGegevenEvent(
                            opdracht_id=opdracht.id,
                            naar_id=naar_id,
                            naar_naam=getattr(crew, "name", str(naar_id)),
                            opdracht_titel=titel,
                            prioriteit=prioriteit,
                        ),
                    )

                    return f"Opdracht verstuurd naar {getattr(crew, 'name', naar_id)}: {titel}"

                except Exception as e:
                    return f"Fout bij versturen opdracht: {str(e)}"

            return "Geen opdracht_manager geconfigureerd en crew niet gevonden"

        try:
            from crewai.communication.directives import OpdrachtPrioriteit

            opdracht = self.opdracht_manager.geef_opdracht(
                van_id=self.id,
                naar_id=naar_id,
                titel=titel,
                beschrijving=beschrijving,
                prioriteit=OpdrachtPrioriteit(prioriteit),
                context=context or {},
            )

            # Emit event
            crewai_event_bus.emit(
                self,
                RvCOpdrachtGegevenEvent(
                    opdracht_id=opdracht.id,
                    naar_id=naar_id,
                    opdracht_titel=titel,
                    prioriteit=prioriteit,
                ),
            )

            return f"Opdracht verstuurd: {opdracht.id}\nTitel: {titel}\nStatus: {opdracht.status.value}"

        except Exception as e:
            return f"Fout bij versturen opdracht: {str(e)}"

    # ============================================================
    # RAPPORTEN
    # ============================================================

    def krijg_rapporten(
        self,
        alleen_ongelezen: bool = False,
        type_filter: str | None = None,
        limiet: int = 50,
    ) -> list[Any]:
        """Krijg rapporten gericht aan de RvC.

        Args:
            alleen_ongelezen: Alleen ongelezen rapporten tonen.
            type_filter: Filter op rapport type.
            limiet: Maximum aantal rapporten.

        Returns:
            Lijst met Rapport objecten.

        Example:
            ```python
            # Alle ongelezen rapporten
            rapporten = rvc.krijg_rapporten(alleen_ongelezen=True)

            # Alleen urgente problemen
            problemen = rvc.krijg_rapporten(type_filter="probleem")
            ```
        """
        if self.rapport_manager is None:
            return []

        try:
            rapporten = self.rapport_manager.krijg_rapporten_voor(
                ontvanger_id=self.id,
                alleen_ongelezen=alleen_ongelezen,
            )

            if type_filter:
                rapporten = [r for r in rapporten if getattr(r, "type", "").value == type_filter]

            return rapporten[:limiet]

        except Exception:
            return []

    def markeer_gelezen(self, rapport_id: UUID) -> bool:
        """Markeer een rapport als gelezen.

        Args:
            rapport_id: ID van het rapport.

        Returns:
            True als succesvol.
        """
        if self.rapport_manager is None:
            return False

        try:
            self.rapport_manager.markeer_gelezen(rapport_id, self.id)
            return True
        except Exception:
            return False

    def krijg_samenvatting(self) -> dict[str, Any]:
        """Krijg een samenvatting van de huidige status.

        Returns:
            Dictionary met status overzicht.

        Example:
            ```python
            status = rvc.krijg_samenvatting()
            print(f"Ongelezen: {status['ongelezen_rapporten']}")
            ```
        """
        rapporten = self.krijg_rapporten()
        ongelezen = [r for r in rapporten if self.id not in getattr(r, "gelezen_door", [])]
        urgente = [r for r in rapporten if getattr(r, "prioriteit", None) and r.prioriteit.value == "urgent"]

        wachtende_goedkeuringen = [
            v for v in self.goedkeurings_verzoeken.values()
            if v.status == GoedkeuringsStatus.WACHTEND
        ]

        return {
            "ongelezen_rapporten": len(ongelezen),
            "urgente_rapporten": len(urgente),
            "wachtende_goedkeuringen": len(wachtende_goedkeuringen),
            "totaal_berichten": len(self.berichten),
            "aantal_crews": len(self.crews),
        }

    # ============================================================
    # GOEDKEURING WORKFLOW
    # ============================================================

    def vraag_goedkeuring(
        self,
        type: Literal["opdracht", "escalatie", "budget", "strategie"],
        beschrijving: str,
        aanvrager_id: UUID,
        aanvrager_naam: str = "Onbekend",
        details: dict[str, Any] | None = None,
    ) -> GoedkeuringsVerzoek:
        """Registreer een goedkeuringsverzoek.

        Deze methode wordt aangeroepen door crews/agents wanneer ze
        goedkeuring nodig hebben voor een actie.

        Args:
            type: Type verzoek.
            beschrijving: Wat goedgekeurd moet worden.
            aanvrager_id: ID van de aanvrager.
            aanvrager_naam: Naam van de aanvrager.
            details: Extra details.

        Returns:
            Het aangemaakte GoedkeuringsVerzoek.

        Example:
            ```python
            verzoek = rvc.vraag_goedkeuring(
                type="budget",
                beschrijving="Verhoging trading limiet naar 100k",
                aanvrager_id=trading_crew.id,
                aanvrager_naam="Trading Crew",
                details={"huidig_limiet": 50000, "nieuw_limiet": 100000}
            )
            ```
        """
        verzoek = GoedkeuringsVerzoek(
            type=type,
            beschrijving=beschrijving,
            aanvrager_id=aanvrager_id,
            aanvrager_naam=aanvrager_naam,
            details=details or {},
        )

        self.goedkeurings_verzoeken[verzoek.id] = verzoek

        # Notificeer via callback
        if self.on_goedkeuring_vereist:
            self.on_goedkeuring_vereist(verzoek)

        # Log als bericht
        self._log_bericht(
            richting="naar_rvc",
            type="notificatie",
            inhoud=f"Goedkeuring vereist ({type}): {beschrijving}",
            gerelateerd_aan=aanvrager_id,
            context={"verzoek_id": str(verzoek.id)},
        )

        # Emit event
        crewai_event_bus.emit(
            self,
            GoedkeuringVereistEvent(
                verzoek_id=verzoek.id,
                verzoek_type=type,
                beschrijving=beschrijving,
                aanvrager_id=aanvrager_id,
                aanvrager_naam=aanvrager_naam,
            ),
        )

        return verzoek

    def keur_goed(
        self,
        verzoek_id: UUID,
        toelichting: str = "",
    ) -> bool:
        """Keur een verzoek goed.

        Args:
            verzoek_id: ID van het verzoek.
            toelichting: Optionele toelichting.

        Returns:
            True als succesvol.

        Example:
            ```python
            rvc.keur_goed(verzoek.id, "Akkoord, maar monitor resultaten")
            ```
        """
        verzoek = self.goedkeurings_verzoeken.get(verzoek_id)
        if verzoek is None:
            return False

        verzoek.status = GoedkeuringsStatus.GOEDGEKEURD
        verzoek.besloten_op = datetime.utcnow()
        verzoek.beslissing_toelichting = toelichting

        # Emit event
        crewai_event_bus.emit(
            self,
            RvCBeslissingEvent(
                verzoek_id=verzoek_id,
                beslissing="goedgekeurd",
                toelichting=toelichting,
            ),
        )

        return True

    def wijs_af(
        self,
        verzoek_id: UUID,
        toelichting: str = "",
    ) -> bool:
        """Wijs een verzoek af.

        Args:
            verzoek_id: ID van het verzoek.
            toelichting: Reden voor afwijzing.

        Returns:
            True als succesvol.

        Example:
            ```python
            rvc.wijs_af(verzoek.id, "Te risicovol in huidige marktomstandigheden")
            ```
        """
        verzoek = self.goedkeurings_verzoeken.get(verzoek_id)
        if verzoek is None:
            return False

        verzoek.status = GoedkeuringsStatus.AFGEWEZEN
        verzoek.besloten_op = datetime.utcnow()
        verzoek.beslissing_toelichting = toelichting

        # Emit event
        crewai_event_bus.emit(
            self,
            RvCBeslissingEvent(
                verzoek_id=verzoek_id,
                beslissing="afgewezen",
                toelichting=toelichting,
            ),
        )

        return True

    def krijg_wachtende_goedkeuringen(self) -> list[GoedkeuringsVerzoek]:
        """Krijg alle wachtende goedkeuringsverzoeken.

        Returns:
            Lijst met wachtende verzoeken, oudste eerst.

        Example:
            ```python
            for verzoek in rvc.krijg_wachtende_goedkeuringen():
                print(f"{verzoek.type}: {verzoek.beschrijving}")
            ```
        """
        wachtend = [
            v for v in self.goedkeurings_verzoeken.values()
            if v.status == GoedkeuringsStatus.WACHTEND
        ]
        # Sorteer op aanvraag datum (oudste eerst)
        return sorted(wachtend, key=lambda v: v.aangevraagd_op)

    # ============================================================
    # CREW REGISTRATIE
    # ============================================================

    def registreer_crew(self, naam: str, crew: Any) -> None:
        """Registreer een crew bij de RvC.

        Args:
            naam: Naam waarmee de crew aangesproken kan worden.
            crew: De Crew instance.

        Example:
            ```python
            rvc.registreer_crew("trading", trading_crew)
            rvc.registreer_crew("risk", risk_crew)

            # Nu kan je gebruiken:
            rvc.verwerk_gebruiker_bericht("@trading: analyseer markt")
            ```
        """
        self.crews[naam.lower()] = crew

        # Voeg RvC toe aan rapporteert_aan van crew
        if hasattr(crew, "rapporteert_aan"):
            if self.id not in crew.rapporteert_aan:
                crew.rapporteert_aan.append(self.id)

        # Geef crew referentie naar RvC
        if hasattr(crew, "raad_van_commissarissen"):
            crew.raad_van_commissarissen = self

    def verwijder_crew(self, naam: str) -> bool:
        """Verwijder een crew registratie.

        Args:
            naam: Naam van de crew.

        Returns:
            True als verwijderd.
        """
        if naam.lower() in self.crews:
            del self.crews[naam.lower()]
            return True
        return False

    # ============================================================
    # HELPER METHODES
    # ============================================================

    def _zoek_doel(self, naam: str) -> UUID | None:
        """Zoek een crew of agent op naam.

        Args:
            naam: Naam om te zoeken.

        Returns:
            UUID van de gevonden crew/agent, of None.
        """
        naam_lower = naam.lower()

        # Zoek in geregistreerde crews
        if naam_lower in self.crews:
            crew = self.crews[naam_lower]
            return getattr(crew, "id", None)

        # Fuzzy match
        for crew_naam, crew in self.crews.items():
            if naam_lower in crew_naam or crew_naam in naam_lower:
                return getattr(crew, "id", None)

        # Zoek in organisatie afdelingen
        if self.organisatie is not None:
            try:
                if hasattr(self.organisatie, "krijg_afdeling_op_naam"):
                    afdeling = self.organisatie.krijg_afdeling_op_naam(naam)
                    if afdeling:
                        return getattr(afdeling, "id", None)
            except Exception:
                pass

        return None

    def _krijg_crew_by_id(self, crew_id: UUID) -> Any | None:
        """Krijg crew instance op basis van ID.

        Args:
            crew_id: ID van de crew.

        Returns:
            Crew instance of None.
        """
        for crew in self.crews.values():
            if getattr(crew, "id", None) == crew_id:
                return crew
        return None

    def _log_bericht(
        self,
        richting: Literal["naar_rvc", "van_rvc"],
        type: str,
        inhoud: str,
        gerelateerd_aan: UUID | None = None,
        context: dict[str, Any] | None = None,
    ) -> RvCBericht:
        """Log een bericht.

        Args:
            richting: Richting van het bericht.
            type: Type bericht.
            inhoud: Inhoud.
            gerelateerd_aan: Optionele gerelateerde ID.
            context: Extra context.

        Returns:
            Het aangemaakte bericht.
        """
        bericht = RvCBericht(
            richting=richting,
            type=type,
            inhoud=inhoud,
            gerelateerd_aan=gerelateerd_aan,
            context=context or {},
        )
        self.berichten.append(bericht)

        # Notificeer via callback
        if self.on_bericht:
            self.on_bericht(bericht)

        return bericht

    def ontvang_rapport(self, rapport: Any) -> None:
        """Ontvang een rapport van een crew.

        Deze methode wordt aangeroepen wanneer een crew een rapport stuurt.

        Args:
            rapport: Het ontvangen Rapport object.
        """
        self._log_bericht(
            richting="naar_rvc",
            type="rapport",
            inhoud=getattr(rapport, "samenvatting", str(rapport)),
            gerelateerd_aan=getattr(rapport, "van_id", None),
            context={"rapport_id": str(getattr(rapport, "id", ""))},
        )

        # Notificeer via callback
        if self.on_nieuw_rapport:
            self.on_nieuw_rapport(rapport)

        # Emit event
        crewai_event_bus.emit(
            self,
            RvCBerichtOntvangenEvent(
                bericht_id=uuid4(),
                van_crew_id=getattr(rapport, "van_id", None),
                inhoud=getattr(rapport, "samenvatting", ""),
                bericht_type="rapport",
            ),
        )

    def ontvang_escalatie(self, escalatie: Any) -> None:
        """Ontvang een escalatie van een crew.

        Deze methode wordt aangeroepen wanneer een escalatie naar RvC niveau komt.

        Args:
            escalatie: De Escalatie object.
        """
        self._log_bericht(
            richting="naar_rvc",
            type="notificatie",
            inhoud=f"Escalatie: {getattr(escalatie, 'reden', str(escalatie))}",
            gerelateerd_aan=getattr(escalatie, "bron_id", None),
            context={"escalatie_id": str(getattr(escalatie, "id", ""))},
        )

        # Notificeer via callback
        if self.on_escalatie:
            self.on_escalatie(escalatie)

        # Maak automatisch goedkeuringsverzoek aan
        self.vraag_goedkeuring(
            type="escalatie",
            beschrijving=getattr(escalatie, "reden", str(escalatie)),
            aanvrager_id=getattr(escalatie, "bron_id", uuid4()),
            aanvrager_naam=getattr(escalatie, "bron_type", "Onbekend"),
            details={"escalatie": str(escalatie)},
        )

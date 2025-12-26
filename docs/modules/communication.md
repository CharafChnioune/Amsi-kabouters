# Communication Module

De `communication/` module bevat opdrachten, rapporten en directe berichten.

## Locatie

```
crewai/communication/
├── __init__.py
├── directives.py    # OpdrachtManager, Opdracht
├── reports.py       # RapportManager, Rapport
└── crew_channel.py  # CrewCommunicatieKanaal, CrewBericht
```

## Import

```python
from crewai.communication import (
    # Opdrachten
    OpdrachtManager,
    Opdracht,
    OpdrachtStatus,
    OpdrachtPrioriteit,
    OpdrachtVoortgang,

    # Rapporten
    RapportManager,
    Rapport,
    RapportType,
    RapportPrioriteit,
    RapportBijlage,
    RapportReactie,
    maak_status_rapport,
    maak_probleem_rapport,
    maak_resultaat_rapport,

    # Crew berichten
    CrewCommunicatieKanaal,
    CrewBericht,
    BerichtType,
    BerichtPrioriteit,
)
```

## OpdrachtManager

Beheert opdrachten tussen crews/agents.

### Constructor

```python
opdracht_mgr = OpdrachtManager(organisatie: OrganisatieHierarchie | None = None)
```

### Methodes

```python
# Opdrachten geven
opdracht_mgr.geef_opdracht(
    van_id: UUID,
    naar_id: UUID,
    titel: str,
    beschrijving: str,
    prioriteit: OpdrachtPrioriteit = OpdrachtPrioriteit.NORMAAL,
    deadline: datetime | None = None,
    context: dict = {},
    vereist_goedkeuring: bool = False
) -> Opdracht

# Status beheer
opdracht_mgr.accepteer_opdracht(opdracht_id: UUID) -> bool
opdracht_mgr.weiger_opdracht(opdracht_id: UUID, reden: str) -> bool
opdracht_mgr.annuleer_opdracht(opdracht_id: UUID) -> bool

# Voortgang
opdracht_mgr.update_voortgang(
    opdracht_id: UUID,
    percentage: int,
    bericht: str = ""
) -> bool

# Voltooien
opdracht_mgr.voltooi_opdracht(
    opdracht_id: UUID,
    resultaat: str,
    details: dict = {}
) -> bool
opdracht_mgr.markeer_mislukt(opdracht_id: UUID, reden: str) -> bool

# Queries
opdracht_mgr.krijg_opdracht(opdracht_id: UUID) -> Opdracht | None
opdracht_mgr.krijg_opdrachten_voor(entity_id: UUID) -> list[Opdracht]
opdracht_mgr.krijg_open_opdrachten() -> list[Opdracht]
opdracht_mgr.krijg_opdrachten_per_status(status: OpdrachtStatus) -> list[Opdracht]
```

## Opdracht

Een opdracht van manager naar medewerker.

```python
opdracht = Opdracht(
    van_id: UUID,
    naar_id: UUID,
    titel: str,
    beschrijving: str,
    prioriteit: OpdrachtPrioriteit = OpdrachtPrioriteit.NORMAAL,
    deadline: datetime | None = None,
    context: dict = {},
    status: OpdrachtStatus = OpdrachtStatus.NIEUW,
    vereist_goedkeuring: bool = False
)
```

## OpdrachtStatus

```python
OpdrachtStatus.NIEUW
OpdrachtStatus.GEACCEPTEERD
OpdrachtStatus.IN_UITVOERING
OpdrachtStatus.WACHT_OP_GOEDKEURING
OpdrachtStatus.VOLTOOID
OpdrachtStatus.GEWEIGERD
OpdrachtStatus.GEANNULEERD
OpdrachtStatus.GEESCALEERD
OpdrachtStatus.MISLUKT
```

## OpdrachtPrioriteit

```python
OpdrachtPrioriteit.LAAG
OpdrachtPrioriteit.NORMAAL
OpdrachtPrioriteit.HOOG
OpdrachtPrioriteit.KRITIEK
```

---

## RapportManager

Beheert rapporten.

### Constructor

```python
rapport_mgr = RapportManager(organisatie: OrganisatieHierarchie | None = None)
```

### Methodes

```python
# Rapporten versturen
rapport_mgr.stuur_rapport(
    van_id: UUID,
    naar_ids: list[UUID],
    type: RapportType,
    titel: str,
    samenvatting: str,
    inhoud: str = "",
    prioriteit: RapportPrioriteit = RapportPrioriteit.NORMAAL,
    bijlagen: list[RapportBijlage] = [],
    context: dict = {}
) -> Rapport

# Lezen
rapport_mgr.krijg_rapport(rapport_id: UUID) -> Rapport | None
rapport_mgr.krijg_rapporten_voor(
    ontvanger_id: UUID,
    alleen_ongelezen: bool = False
) -> list[Rapport]
rapport_mgr.krijg_ongelezen_rapporten(voor_id: UUID) -> list[Rapport]

# Status
rapport_mgr.markeer_gelezen(rapport_id: UUID, lezer_id: UUID) -> bool

# Reacties
rapport_mgr.voeg_reactie_toe(
    rapport_id: UUID,
    auteur_id: UUID,
    tekst: str,
    actie_vereist: bool = False
) -> RapportReactie | None

# Statistieken
rapport_mgr.krijg_rapport_statistieken() -> dict
```

## Rapport

Een formeel rapport.

```python
rapport = Rapport(
    van_id: UUID,
    naar_ids: list[UUID],
    type: RapportType,
    titel: str,
    samenvatting: str,
    inhoud: str = "",
    prioriteit: RapportPrioriteit = RapportPrioriteit.NORMAAL,
    bijlagen: list[RapportBijlage] = [],
    context: dict = {}
)
```

## RapportType

```python
RapportType.STATUS      # Voortgangsupdate
RapportType.PROBLEEM    # Issue melding
RapportType.RESULTAAT   # Behaald resultaat
RapportType.ESCALATIE   # Escalatie melding
RapportType.VOORTGANG   # Periodieke rapportage
RapportType.ANALYSE     # Analyse met bevindingen
RapportType.AANBEVELING # Actie-suggesties
```

## RapportBijlage

```python
bijlage = RapportBijlage(
    naam: str,
    type: str,  # "json", "text", "csv", etc.
    inhoud: Any,
    beschrijving: str = ""
)
```

## Helper Functies

```python
# Maak snel rapport
rapport = maak_status_rapport(
    van_id: UUID,
    naar_ids: list[UUID],
    titel: str,
    status_tekst: str
)

rapport = maak_probleem_rapport(
    van_id: UUID,
    naar_ids: list[UUID],
    titel: str,
    probleem_beschrijving: str,
    urgentie: str = "normaal"
)

rapport = maak_resultaat_rapport(
    van_id: UUID,
    naar_ids: list[UUID],
    titel: str,
    resultaat: str,
    details: dict = {}
)
```

---

## CrewCommunicatieKanaal

Directe berichten tussen crews.

### Constructor

```python
kanaal = CrewCommunicatieKanaal(naam: str = "Algemeen")
```

### Methodes

```python
# Deelnemers beheren
kanaal.voeg_deelnemer_toe(crew_id: UUID) -> None
kanaal.verwijder_deelnemer(crew_id: UUID) -> bool

# Berichten sturen
kanaal.stuur_bericht(
    van_crew_id: UUID,
    naar_crew_id: UUID,
    inhoud: str,
    type: BerichtType = BerichtType.INFORMATIE,
    prioriteit: BerichtPrioriteit = BerichtPrioriteit.NORMAAL,
    context: dict = {}
) -> CrewBericht

# Broadcast
kanaal.broadcast(
    van_crew_id: UUID,
    inhoud: str,
    prioriteit: BerichtPrioriteit = BerichtPrioriteit.NORMAAL
) -> list[CrewBericht]

# Berichten ontvangen
kanaal.ontvang_berichten(
    crew_id: UUID,
    alleen_ongelezen: bool = True,
    markeer_gelezen: bool = True,
    type_filter: BerichtType | None = None
) -> list[CrewBericht]

# Beantwoorden
kanaal.beantwoord(
    vraag_id: UUID,
    van_crew_id: UUID,
    antwoord: str
) -> CrewBericht

# Callbacks
kanaal.registreer_callback(callback: Callable[[CrewBericht], None]) -> None
```

## CrewBericht

```python
bericht = CrewBericht(
    van_crew_id: UUID,
    naar_crew_id: UUID,
    inhoud: str,
    type: BerichtType = BerichtType.INFORMATIE,
    prioriteit: BerichtPrioriteit = BerichtPrioriteit.NORMAAL,
    antwoord_op: UUID | None = None,
    context: dict = {}
)
```

## BerichtType

```python
BerichtType.INFORMATIE
BerichtType.VRAAG
BerichtType.ANTWOORD
BerichtType.VERZOEK
BerichtType.BEVESTIGING
BerichtType.WAARSCHUWING
BerichtType.STATUS
```

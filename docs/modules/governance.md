# Governance Module

De `governance/` module bevat toegangscontrole, escalatie en menselijk toezicht.

## Locatie

```
crewai/governance/
├── __init__.py
├── access_control.py           # ToegangsControle, ToegangsRegel
├── escalation.py               # EscalatieManager, EscalatieRegel
└── raad_van_commissarissen.py  # RaadVanCommissarissen
```

## Import

```python
from crewai.governance import (
    # Access Control
    ToegangsControle,
    ToegangsRegel,
    ToegangsVoorwaarden,
    TijdsVoorwaarde,
    BudgetVoorwaarde,
    ActieType,
    ResourceType,
    PrincipalType,
    EffectType,

    # Escalation
    EscalatieManager,
    EscalatieRegel,
    Escalatie,
    EscalatieTriggerType,
    EscalatieDoelType,
    EscalatieActieType,
    EscalatieStatus,
    maak_standaard_escalatie_regels,

    # RvC
    RaadVanCommissarissen,
    GoedkeuringsVerzoek,
    GoedkeuringsStatus,
    RvCBericht,

    # Helpers
    maak_allow_all_regel,
    maak_werkuren_regel,
    maak_budget_regel,
)
```

## ToegangsControle

ACL-gebaseerd toegangssysteem.

### Constructor

```python
toegang = ToegangsControle(log_toegang: bool = False)
```

### Methodes

```python
# Regels beheren
toegang.voeg_regel_toe(regel: ToegangsRegel) -> None
toegang.verwijder_regel(regel_naam: str) -> bool
toegang.krijg_regels() -> list[ToegangsRegel]

# Toegang controleren
toegang.controleer_toegang(
    principal_id: UUID,
    principal_type: str,  # "agent", "crew", "rol", "afdeling"
    resource_type: str,   # "tool", "crew", "agent", etc.
    resource_id: UUID | None,
    actie: str,           # "lezen", "schrijven", "uitvoeren", etc.
    context: dict = {}
) -> tuple[bool, str]  # (toegestaan, reden)

# Query resources
toegang.krijg_toegankelijke_resources(
    principal_id: UUID,
    principal_type: str,
    resource_type: str
) -> list[UUID]
```

## ToegangsRegel

Enkele toegangsregel.

```python
regel = ToegangsRegel(
    naam: str,
    resource_type: str,
    principal_type: str,
    principal_id: UUID | None = None,
    resource_id: UUID | None = None,
    actie: str = "*",
    effect: str = "toestaan",  # of "weigeren"
    prioriteit: int = 0,
    voorwaarden: ToegangsVoorwaarden | None = None
)
```

## ToegangsVoorwaarden

Voorwaarden voor een regel.

```python
voorwaarden = ToegangsVoorwaarden(
    tijd: TijdsVoorwaarde | None = None,
    budget: BudgetVoorwaarde | None = None,
    vereist_goedkeuring: bool = False,
    max_per_dag: int | None = None
)
```

## EscalatieManager

Beheert escalaties.

### Constructor

```python
escalatie_mgr = EscalatieManager(organisatie: OrganisatieHierarchie | None = None)
```

### Methodes

```python
# Regels beheren
escalatie_mgr.voeg_regel_toe(regel: EscalatieRegel) -> None
escalatie_mgr.verwijder_regel(regel_naam: str) -> bool

# Triggers controleren
escalatie_mgr.controleer_triggers(context: dict) -> list[EscalatieRegel]

# Escaleren
escalatie_mgr.escaleer(
    bron_id: UUID,
    bron_type: str,
    regel: EscalatieRegel | None,
    reden: str,
    context: dict = {}
) -> Escalatie

# Lifecycle
escalatie_mgr.behandel_escalatie(escalatie_id: UUID, behandeld_door: UUID) -> bool
escalatie_mgr.los_escalatie_op(escalatie_id: UUID, reactie: str) -> bool
escalatie_mgr.stuur_door(escalatie_id: UUID, naar_id: UUID) -> bool

# Queries
escalatie_mgr.krijg_openstaande_escalaties() -> list[Escalatie]
escalatie_mgr.krijg_escalatie_statistieken() -> dict
```

## EscalatieRegel

Escalatieregel configuratie.

```python
regel = EscalatieRegel(
    naam: str,
    trigger_type: EscalatieTriggerType,
    trigger_waarde: Any,
    escaleer_naar: EscalatieDoelType,
    specifiek_doel_id: UUID | None = None,
    actie: EscalatieActieType = EscalatieActieType.MELDEN,
    scope: str = "alle",  # "alle", "afdeling", "crew", "agent"
    prioriteit: int = 0,
    actief: bool = True
)
```

## RaadVanCommissarissen

Menselijk toezicht interface.

### Constructor

```python
rvc = RaadVanCommissarissen(
    organisatie: OrganisatieHierarchie | None = None,
    opdracht_manager: OpdrachtManager | None = None,
    rapport_manager: RapportManager | None = None,

    # Callbacks
    on_nieuw_rapport: Callable | None = None,
    on_goedkeuring_vereist: Callable | None = None,
    on_escalatie: Callable | None = None,
    on_bericht: Callable | None = None
)
```

### Methodes

```python
# Bericht verwerking
rvc.verwerk_gebruiker_bericht(bericht: str) -> str

# Opdrachten
rvc.geef_opdracht(
    naar_id: UUID,
    titel: str,
    beschrijving: str,
    prioriteit: str = "hoog",
    context: dict = {}
) -> str

# Crews registreren
rvc.registreer_crew(naam: str, crew: Crew) -> None
rvc.verwijder_crew(naam: str) -> bool

# Rapporten
rvc.krijg_rapporten(
    alleen_ongelezen: bool = False,
    type_filter: str | None = None,
    limiet: int = 50
) -> list[Rapport]
rvc.markeer_gelezen(rapport_id: UUID) -> bool
rvc.krijg_samenvatting() -> dict

# Goedkeuringen
rvc.vraag_goedkeuring(
    type: str,  # "opdracht", "escalatie", "budget", "strategie"
    beschrijving: str,
    aanvrager_id: UUID,
    aanvrager_naam: str = "Onbekend",
    details: dict = {}
) -> GoedkeuringsVerzoek

rvc.keur_goed(verzoek_id: UUID, toelichting: str = "") -> bool
rvc.wijs_af(verzoek_id: UUID, toelichting: str = "") -> bool
rvc.krijg_wachtende_goedkeuringen() -> list[GoedkeuringsVerzoek]

# Ontvangen
rvc.ontvang_rapport(rapport: Rapport) -> None
rvc.ontvang_escalatie(escalatie: Escalatie) -> None
```

## GoedkeuringsVerzoek

Goedkeuringsaanvraag.

```python
verzoek = GoedkeuringsVerzoek(
    type: str,  # "opdracht", "escalatie", "budget", "strategie"
    beschrijving: str,
    aanvrager_id: UUID,
    aanvrager_naam: str = "Onbekend",
    details: dict = {},
    status: GoedkeuringsStatus = GoedkeuringsStatus.WACHTEND
)
```

## Enums

```python
# Trigger types
EscalatieTriggerType.TIMEOUT
EscalatieTriggerType.FOUT
EscalatieTriggerType.BUDGET_OVERSCHREDEN
EscalatieTriggerType.HANDMATIG
EscalatieTriggerType.HERHAALDE_POGINGEN
EscalatieTriggerType.GEEN_VOORTGANG

# Doel types
EscalatieDoelType.DIRECTE_MANAGER
EscalatieDoelType.AFDELING_HOOFD
EscalatieDoelType.DIRECTIE
EscalatieDoelType.SPECIFIEK
EscalatieDoelType.VOLGENDE_IN_KETEN

# Actie types
EscalatieActieType.MELDEN
EscalatieActieType.HERTOEWIJZEN
EscalatieActieType.STOPPEN
EscalatieActieType.GOEDKEURING_VRAGEN
EscalatieActieType.PARALLEL_UITVOEREN

# Goedkeuring status
GoedkeuringsStatus.WACHTEND
GoedkeuringsStatus.GOEDGEKEURD
GoedkeuringsStatus.AFGEWEZEN
GoedkeuringsStatus.AANGEPAST
```

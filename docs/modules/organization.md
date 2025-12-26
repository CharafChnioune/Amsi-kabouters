# Organization Module

De `organization/` module bevat alle klassen voor hiërarchische organisatiestructuur.

## Locatie

```
crewai/organization/
├── __init__.py
├── hierarchy.py    # OrganisatieHierarchie, Rapportagelijn
├── role.py         # Rol, PermissieNiveau
└── department.py   # Afdeling, AfdelingsResource, AfdelingsManager
```

## Import

```python
from crewai.organization import (
    # Hierarchy
    OrganisatieHierarchie,
    Rapportagelijn,

    # Roles
    Rol,
    PermissieNiveau,
    maak_standaard_rollen,

    # Departments
    Afdeling,
    AfdelingsResource,
    AfdelingsManager,
)
```

## OrganisatieHierarchie

Centrale klasse voor organisatiebeheer.

### Constructor

```python
org = OrganisatieHierarchie()
```

### Methodes

#### Afdeling Beheer

```python
# Toevoegen
org.voeg_afdeling_toe(afdeling: Afdeling) -> None

# Opvragen
org.krijg_afdeling(afdeling_id: UUID) -> Afdeling | None
org.krijg_afdeling_op_naam(naam: str) -> Afdeling | None
org.krijg_alle_afdelingen() -> list[Afdeling]
```

#### Rol Beheer

```python
# Toewijzen
org.wijs_rol_toe(entity_id: UUID, rol: Rol) -> None
org.wijs_rol_toe_aan_crew(crew_id: UUID, rol: Rol) -> None

# Opvragen
org.krijg_rol(entity_id: UUID) -> Rol | None
org.krijg_crew_rol(crew_id: UUID) -> Rol | None
org.krijg_alle_crews_met_rol(niveau: PermissieNiveau) -> list[UUID]

# Verwijderen
org.verwijder_rol(entity_id: UUID) -> bool
org.verwijder_crew_rol(crew_id: UUID) -> bool
```

#### Rapportagelijn Beheer

```python
# Toevoegen
org.voeg_rapportagelijn_toe(lijn: Rapportagelijn) -> None

# Opvragen
org.krijg_rapportagelijnen(entity_id: UUID) -> list[Rapportagelijn]
```

#### Hiërarchie Queries

```python
# Keten queries
org.krijg_management_keten(entity_id: UUID) -> list[UUID]
org.krijg_ondergeschikten(manager_id: UUID) -> list[UUID]
org.krijg_directe_manager(entity_id: UUID) -> UUID | None
org.krijg_managers(entity_id: UUID) -> list[UUID]

# Crew queries
org.crew_mag_opdracht_geven(van_crew_id: UUID, naar_id: UUID) -> bool
org.is_manager_van(manager_id: UUID, medewerker_id: UUID) -> bool
```

#### Permissie Checks

```python
org.mag_opdracht_geven(van_id: UUID, naar_id: UUID) -> bool
org.mag_rapporteren_aan(van_id: UUID, naar_id: UUID) -> bool
org.mag_escaleren_naar(van_id: UUID, naar_id: UUID) -> bool
org.mag_communiceren(van_id: UUID, naar_id: UUID) -> bool
```

#### Validatie & Visualisatie

```python
org.valideer_structuur() -> list[str]  # Lijst met fouten
org.krijg_organigram() -> dict  # Visualisatie structuur
```

## Rol

Definieert permissies voor een entity.

### Constructor

```python
rol = Rol(
    naam: str,
    beschrijving: str = "",
    niveau: PermissieNiveau = PermissieNiveau.UITVOEREND,

    # Permissies
    kan_delegeren: bool = False,
    kan_escaleren: bool = True,
    kan_goedkeuren: bool = False,
    kan_opdrachten_geven: bool = False,
    kan_rapporten_ontvangen: bool = False,

    # Tool beperkingen
    toegestane_tools: list[str] = [],
    geblokkeerde_tools: list[str] = [],

    # Relaties
    ontvangt_opdrachten_van: list[UUID] = [],
    escaleert_naar: list[UUID] = [],

    # Limieten
    max_budget: float | None = None,
    max_gelijktijdige_taken: int = 5
)
```

### Methodes

```python
rol.mag_tool_gebruiken(tool_naam: str) -> bool
rol.mag_opdracht_geven_aan(niveau: PermissieNiveau) -> bool
rol.mag_escaleren_naar(doel_niveau: PermissieNiveau) -> bool
```

## PermissieNiveau

Enum met 6 niveaus.

```python
class PermissieNiveau(str, Enum):
    UITVOEREND = "uitvoerend"
    TEAMLID = "teamlid"
    TEAMLEIDER = "teamleider"
    AFDELINGSHOOFD = "afdelingshoofd"
    DIRECTIE = "directie"
    BESTUUR = "bestuur"
```

### Class Methods

```python
PermissieNiveau.is_hoger_dan(niveau1, niveau2) -> bool
PermissieNiveau.is_gelijk_of_hoger_dan(niveau1, niveau2) -> bool
```

## Afdeling

Representeert een departement of team.

### Constructor

```python
afdeling = Afdeling(
    naam: str,
    beschrijving: str = "",
    parent_afdeling_id: UUID | None = None,
    manager_agent_id: UUID | None = None,
    resources: AfdelingsResource | None = None,
    isolatie_niveau: str = "open",  # open, afdeling, strikt
    toegestane_afdelingen: list[UUID] = []
)
```

### Methodes

```python
afdeling.voeg_agent_toe(agent_id: UUID) -> None
afdeling.voeg_crew_toe(crew_id: UUID) -> None
afdeling.verwijder_agent(agent_id: UUID) -> bool
afdeling.verwijder_crew(crew_id: UUID) -> bool
afdeling.bevat_agent(agent_id: UUID) -> bool
afdeling.bevat_crew(crew_id: UUID) -> bool
afdeling.mag_communiceren_met(andere_afdeling_id: UUID) -> bool
```

## AfdelingsResource

Resource limieten voor een afdeling.

```python
resources = AfdelingsResource(
    max_rpm: int = 100,
    max_tokens_per_dag: int = 1000000,
    budget_limiet: float = 0.0,
    budget_gebruikt: float = 0.0,
    max_gelijktijdige_crews: int = 10
)

resources.is_binnen_budget(bedrag: float) -> bool
resources.registreer_uitgave(bedrag: float) -> bool
```

## maak_standaard_rollen

Factory functie voor standaard rollen.

```python
rollen = maak_standaard_rollen()

# Returns dict met:
# - "bestuurder"
# - "directeur"
# - "afdelingshoofd"
# - "teamleider"
# - "teamlid"
# - "uitvoerend"
```

# Organization Tools Module

De `tools/organization_tools/` module bevat tools waarmee agents kunnen communiceren binnen de organisatiehiërarchie.

## Locatie

```
crewai/tools/organization_tools/
├── __init__.py
├── organization_tools.py    # OrganizationTools factory
├── give_directive_tool.py   # GeefOpdrachtTool
├── report_tool.py           # RapporteerTool
├── escalate_tool.py         # EscaleerTool
└── delegate_to_crew_tool.py # DelegeerNaarCrewTool
```

## Import

```python
from crewai.tools.organization_tools import (
    OrganizationTools,
    GeefOpdrachtTool,
    RapporteerTool,
    EscaleerTool,
    DelegeerNaarCrewTool,
)
```

---

## OrganizationTools

Factory klasse voor het aanmaken van alle organisatie tools voor een agent.

### Constructor

```python
org_tools = OrganizationTools(
    agent_id: UUID,
    rol: Rol | None = None,
    organisatie: OrganisatieHierarchie | None = None,
    opdracht_manager: OpdrachtManager | None = None,
    rapport_manager: RapportManager | None = None,
    escalatie_manager: EscalatieManager | None = None,
    ondergeschikten: dict[str, UUID] = {},
    managers: dict[str, UUID] = {}
)
```

### Methodes

```python
# Krijg alle tools gebaseerd op rol/permissies
tools = org_tools.tools() -> list[BaseTool]
```

### Factory Methodes

```python
# Voor een manager met ondergeschikten
org_tools = OrganizationTools.voor_manager(
    agent_id=manager_id,
    organisatie=org,
    ondergeschikten={"team_a": team_a_id},
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr,
    escalatie_manager=escalatie_mgr
)

# Voor een medewerker (geen ondergeschikten)
org_tools = OrganizationTools.voor_medewerker(
    agent_id=medewerker_id,
    organisatie=org,
    rapport_manager=rapport_mgr,
    escalatie_manager=escalatie_mgr
)
```

### Voorbeeld

```python
from crewai.tools.organization_tools import OrganizationTools

# Maak tools voor een manager
org_tools = OrganizationTools(
    agent_id=manager.id,
    organisatie=org,
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr,
    escalatie_manager=escalatie_mgr,
    ondergeschikten={"trading": trading_id, "research": research_id},
    managers={"directeur": directeur_id}
)

# Voeg tools toe aan agent
manager.tools.extend(org_tools.tools())

# De manager kan nu:
# - Opdrachten geven aan trading en research
# - Rapporteren aan directeur
# - Escaleren naar management
```

---

## GeefOpdrachtTool

Tool voor het geven van opdrachten aan ondergeschikten.

### Constructor

```python
tool = GeefOpdrachtTool(
    agent_id: UUID,
    organisatie: OrganisatieHierarchie | None = None,
    opdracht_manager: OpdrachtManager | None = None,
    ontvangers: dict[str, UUID] = {}
)
```

### Input Schema

```python
{
    "ontvanger": str,    # Naam of ID van de ontvanger
    "opdracht": str,     # De opdracht beschrijving
    "context": str,      # Achtergrondinformatie
    "prioriteit": str    # "laag", "normaal", "hoog", "kritiek" (optioneel)
}
```

### Voorbeeld Agent Gebruik

```
Actie: Geef Opdracht
Actie Input: {
    "ontvanger": "trading",
    "opdracht": "Analyseer de BTC marktpositie",
    "context": "Focus op de laatste 24 uur aan trades",
    "prioriteit": "hoog"
}
```

---

## RapporteerTool

Tool voor het rapporteren aan management.

### Constructor

```python
tool = RapporteerTool(
    agent_id: UUID,
    organisatie: OrganisatieHierarchie | None = None,
    rapport_manager: RapportManager | None = None,
    ontvangers: dict[str, UUID] = {}
)
```

### Input Schema

```python
{
    "type": str,        # "status", "probleem", "resultaat", "voortgang", "aanbeveling"
    "titel": str,       # Korte titel
    "inhoud": str,      # Gedetailleerde inhoud
    "prioriteit": str   # "info", "normaal", "belangrijk", "urgent" (optioneel)
}
```

### Rapport Types

| Type | Beschrijving |
|------|-------------|
| `status` | Statusupdate over lopende werkzaamheden |
| `probleem` | Melding van een probleem of blokkade |
| `resultaat` | Rapportage van behaald resultaat |
| `voortgang` | Periodieke voortgangsrapportage |
| `aanbeveling` | Rapport met aanbevelingen voor actie |

### Voorbeeld Agent Gebruik

```
Actie: Rapporteer
Actie Input: {
    "type": "resultaat",
    "titel": "Trading analyse afgerond",
    "inhoud": "BTC analyse compleet. Advies: verkopen bij huidige prijs.",
    "prioriteit": "belangrijk"
}
```

---

## EscaleerTool

Tool voor escalatie naar hoger management.

### Constructor

```python
tool = EscaleerTool(
    agent_id: UUID,
    organisatie: OrganisatieHierarchie | None = None,
    escalatie_manager: EscalatieManager | None = None
)
```

### Input Schema

```python
{
    "reden": str,       # Waarom je escaleert
    "context": str,     # Relevante informatie
    "urgentie": str     # "laag", "normaal", "hoog", "kritiek" (optioneel)
}
```

### Wanneer Escaleren?

- Probleem dat je niet zelf kunt oplossen
- Extra autorisatie of goedkeuring nodig
- Geblokkeerd en hulp nodig
- Beslissing nodig van hoger niveau

### Voorbeeld Agent Gebruik

```
Actie: Escaleer
Actie Input: {
    "reden": "Budget overschrijding verwacht",
    "context": "De geplande trade van 50K EUR overschrijdt mijn budget limiet van 10K EUR",
    "urgentie": "hoog"
}
```

---

## DelegeerNaarCrewTool

Tool voor het delegeren van taken naar sub-crews (crew-to-crew communicatie).

### Constructor

```python
tool = DelegeerNaarCrewTool(
    crew_id: UUID,
    sub_crews: dict[str, Crew] = {},
    opdracht_manager: OpdrachtManager | None = None
)
```

### Input Schema

```python
{
    "crew_naam": str,           # Naam van de sub-crew
    "taak": str,                # Beschrijving van de taak
    "context": str,             # Extra context (optioneel)
    "wacht_op_resultaat": bool, # Wachten op resultaat? (standaard: true)
    "prioriteit": str           # "laag", "normaal", "hoog", "kritiek" (optioneel)
}
```

### Methodes

```python
# Krijg lijst van beschikbare sub-crews
tool.krijg_beschikbare_crews() -> list[str]
```

### Voorbeeld Agent Gebruik

```
Actie: Delegeer naar Crew
Actie Input: {
    "crew_naam": "research",
    "taak": "Analyseer de fundamentals van BTC voor de komende week",
    "context": "Inclusief on-chain data en macro-economische factoren",
    "wacht_op_resultaat": true,
    "prioriteit": "hoog"
}
```

---

## Complete Setup Voorbeeld

```python
from uuid import uuid4
from crewai import Agent, Crew
from crewai.organization import OrganisatieHierarchie, maak_standaard_rollen
from crewai.communication import OpdrachtManager, RapportManager
from crewai.governance import EscalatieManager
from crewai.tools.organization_tools import (
    OrganizationTools,
    DelegeerNaarCrewTool
)

# Setup organisatie
org = OrganisatieHierarchie()
rollen = maak_standaard_rollen()

# Managers
opdracht_mgr = OpdrachtManager(organisatie=org)
rapport_mgr = RapportManager(organisatie=org)
escalatie_mgr = EscalatieManager(organisatie=org)

# Maak agents
directeur = Agent(role="Directeur", goal="Leid de organisatie")
manager = Agent(role="Manager", goal="Beheer het team")
medewerker = Agent(role="Analist", goal="Voer analyses uit")

# Wijs rollen toe
org.wijs_rol_toe(directeur.id, rollen["directeur"])
org.wijs_rol_toe(manager.id, rollen["teamleider"])
org.wijs_rol_toe(medewerker.id, rollen["teamlid"])

# Tools voor directeur (kan aan manager delegeren)
directeur_tools = OrganizationTools.voor_manager(
    agent_id=directeur.id,
    organisatie=org,
    ondergeschikten={"manager": manager.id},
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr,
    escalatie_manager=escalatie_mgr
)
directeur.tools.extend(directeur_tools.tools())

# Tools voor manager (kan aan medewerker delegeren, rapporteert aan directeur)
manager_tools = OrganizationTools(
    agent_id=manager.id,
    organisatie=org,
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr,
    escalatie_manager=escalatie_mgr,
    ondergeschikten={"analist": medewerker.id},
    managers={"directeur": directeur.id}
)
manager.tools.extend(manager_tools.tools())

# Tools voor medewerker (alleen rapporteren en escaleren)
medewerker_tools = OrganizationTools.voor_medewerker(
    agent_id=medewerker.id,
    organisatie=org,
    rapport_manager=rapport_mgr,
    escalatie_manager=escalatie_mgr
)
medewerker.tools.extend(medewerker_tools.tools())
```

---

## Crew-to-Crew Delegatie

Voor hiërarchische crews die taken delegeren aan sub-crews:

```python
# Sub-crews
trading_crew = Crew(agents=[trader], tasks=[...])
research_crew = Crew(agents=[analyst], tasks=[...])

# Manager crew met delegatie tool
delegeer_tool = DelegeerNaarCrewTool(
    crew_id=manager_crew.id,
    sub_crews={
        "trading": trading_crew,
        "research": research_crew
    },
    opdracht_manager=opdracht_mgr
)

# Manager crew kan nu taken delegeren
ceo = Agent(
    role="CEO",
    tools=[delegeer_tool],
    ...
)

manager_crew = Crew(agents=[ceo], tasks=[...])
```

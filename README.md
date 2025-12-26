# Amsi Kabouters

**Nederlands Enterprise AI Agent Framework**

Een uitgebreid AI agent framework met hiërarchische organisatiestructuur, Raad van Commissarissen interface, opdrachten/rapportages systeem en 24/7 operatie. Volledig in het Nederlands.

---

## Kenmerken

- **Raad van Commissarissen (RvC)** - Menselijk toezicht via chat interface
- **OrganisatieHierarchie** - 6 permissie niveaus van UITVOEREND tot BESTUUR
- **Opdrachten & Rapporten** - Formele communicatie tussen crews
- **Escalatie Systeem** - Automatische en handmatige escalatie
- **Toegangscontrole** - ACL-gebaseerde permissies met voorwaarden
- **Nederlandse Teksten** - Alle agent output in het Nederlands

---

## Installatie

```bash
pip install amsi-kabouters
```

Of met extra tools:

```bash
pip install 'amsi-kabouters[tools]'
```

---

## Quick Start

```python
from crewai import Agent, Crew, Task
from crewai.organization import OrganisatieHierarchie, maak_standaard_rollen
from crewai.governance import RaadVanCommissarissen
from crewai.communication import OpdrachtManager, RapportManager

# Setup organisatie
org = OrganisatieHierarchie()
rollen = maak_standaard_rollen()

# Managers
opdracht_mgr = OpdrachtManager(organisatie=org)
rapport_mgr = RapportManager(organisatie=org)

# Raad van Commissarissen (menselijk toezicht)
rvc = RaadVanCommissarissen(
    organisatie=org,
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr
)

# Maak een crew
analyst = Agent(
    role="Markt Analist",
    goal="Analyseer markttrends en geef advies",
    backstory="Je bent een ervaren analist met expertise in financiële markten."
)

crew = Crew(
    agents=[analyst],
    tasks=[Task(description="Analyseer de huidige markttrends", agent=analyst)],
    organisatie=org
)

# Registreer bij RvC
rvc.registreer_crew("analyse", crew)

# Gebruiker kan nu via chat aansturen
rvc.verwerk_gebruiker_bericht("@analyse: analyseer de EUR/USD trend")
rvc.verwerk_gebruiker_bericht("status?")
rvc.verwerk_gebruiker_bericht("akkoord")
```

---

## Organisatie Structuur

### Permissie Niveaus

| Niveau | Beschrijving |
|--------|-------------|
| `BESTUUR` | Volledige controle (RvC) |
| `DIRECTIE` | Alle afdelingen + strategie |
| `AFDELINGSHOOFD` | Afdeling aansturen + budget |
| `TEAMLEIDER` | Team aansturen |
| `TEAMLID` | Beperkt delegeren in team |
| `UITVOEREND` | Alleen taken uitvoeren |

### Hiërarchie Voorbeeld

```
          ┌──────────────────────┐
          │        RvC           │
          │  (Mens/Gebruiker)    │
          └──────────┬───────────┘
                     │
          ┌──────────┴───────────┐
          │     Directie Crew    │
          └──────────┬───────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
 Trading          Research         Risk
   Crew            Crew           Crew
```

---

## Raad van Commissarissen

De RvC is de interface voor menselijk toezicht:

```python
# Opdrachten geven via chat
rvc.verwerk_gebruiker_bericht("@trading: stop alle posities")
rvc.verwerk_gebruiker_bericht("@risk: wat is de huidige exposure?")

# Status opvragen
rvc.verwerk_gebruiker_bericht("status?")

# Goedkeuringen afhandelen
rvc.verwerk_gebruiker_bericht("akkoord")      # Keur oudste goed
rvc.verwerk_gebruiker_bericht("afwijzen")     # Wijs oudste af
rvc.verwerk_gebruiker_bericht("akkoord #123") # Specifiek verzoek
```

### Chat Commando's

| Patroon | Actie |
|---------|-------|
| `@crew: tekst` | Opdracht aan crew |
| `status?` | Status opvragen |
| `akkoord` | Goedkeuring geven |
| `afwijzen` | Afwijzing geven |

---

## Modules

### Organization (`crewai/organization/`)

```python
from crewai.organization import (
    OrganisatieHierarchie,
    Afdeling,
    Rol,
    PermissieNiveau,
    maak_standaard_rollen
)
```

### Governance (`crewai/governance/`)

```python
from crewai.governance import (
    RaadVanCommissarissen,
    ToegangsControle,
    EscalatieManager,
    maak_standaard_escalatie_regels
)
```

### Communication (`crewai/communication/`)

```python
from crewai.communication import (
    OpdrachtManager,
    RapportManager,
    CrewCommunicatieKanaal,
    maak_status_rapport,
    maak_probleem_rapport
)
```

### Organization Tools (`crewai/tools/organization_tools/`)

```python
from crewai.tools.organization_tools import (
    GeefOpdrachtTool,
    RapporteerTool,
    EscaleerTool,
    DelegeerNaarCrewTool,
    OrganizationTools
)
```

---

## Documentatie

Volledige documentatie is beschikbaar in de `/docs/` folder:

- [README](docs/README.md) - Hoofdoverzicht
- [Getting Started](docs/getting-started.md) - Quick start guide
- **Architectuur**
  - [Overzicht](docs/architectuur/overzicht.md)
  - [Organisatie Model](docs/architectuur/organisatie-model.md)
  - [Governance Model](docs/architectuur/governance-model.md)
- **Modules**
  - [Organization](docs/modules/organization.md)
  - [Governance](docs/modules/governance.md)
  - [Communication](docs/modules/communication.md)
  - [Tools](docs/modules/tools.md)
- **Guides**
  - [Raad van Commissarissen](docs/guides/raad-van-commissarissen.md)
  - [Opdrachten & Rapporten](docs/guides/opdrachten-rapporten.md)
  - [Escalatie Workflow](docs/guides/escalatie-workflow.md)
- **API**
  - [Events](docs/api/events.md)

---

## Voorbeeld: Complete Setup

```python
from crewai import Agent, Crew, Task
from crewai.organization import (
    OrganisatieHierarchie,
    Afdeling,
    maak_standaard_rollen
)
from crewai.governance import (
    RaadVanCommissarissen,
    EscalatieManager,
    maak_standaard_escalatie_regels
)
from crewai.communication import OpdrachtManager, RapportManager

# 1. Organisatie setup
org = OrganisatieHierarchie()
rollen = maak_standaard_rollen()

# 2. Afdelingen
directie = Afdeling(naam="Directie")
trading = Afdeling(naam="Trading", parent_afdeling_id=directie.id)
research = Afdeling(naam="Research", parent_afdeling_id=directie.id)

org.voeg_afdeling_toe(directie)
org.voeg_afdeling_toe(trading)
org.voeg_afdeling_toe(research)

# 3. Managers
opdracht_mgr = OpdrachtManager(organisatie=org)
rapport_mgr = RapportManager(organisatie=org)
escalatie_mgr = EscalatieManager(organisatie=org)

# Standaard escalatie regels
for regel in maak_standaard_escalatie_regels():
    escalatie_mgr.voeg_regel_toe(regel)

# 4. RvC (menselijk toezicht)
rvc = RaadVanCommissarissen(
    organisatie=org,
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr
)

# 5. Crews aanmaken
trading_agent = Agent(role="Trader", goal="Voer trades uit")
trading_crew = Crew(
    agents=[trading_agent],
    tasks=[...],
    organisatie=org
)

research_agent = Agent(role="Onderzoeker", goal="Doe marktonderzoek")
research_crew = Crew(
    agents=[research_agent],
    tasks=[...],
    organisatie=org
)

# 6. Rollen toewijzen
org.wijs_rol_toe_aan_crew(trading_crew.id, rollen["teamleider"])
org.wijs_rol_toe_aan_crew(research_crew.id, rollen["teamleider"])

# 7. Registreer bij RvC
rvc.registreer_crew("trading", trading_crew)
rvc.registreer_crew("research", research_crew)

# 8. Klaar! Gebruiker kan nu aansturen via chat
print(rvc.verwerk_gebruiker_bericht("status?"))
```

---

## Gebaseerd op CrewAI

Amsi Kabouters is gebouwd op [CrewAI](https://github.com/crewAIInc/crewAI) en breidt dit uit met:

- Nederlandse enterprise features
- Hiërarchische organisatiestructuur
- Raad van Commissarissen interface
- Opdrachten en rapportages systeem
- Escalatie en toegangscontrole

---

## Licentie

MIT License - Zie [LICENSE](LICENSE) voor details.

---

## Bijdragen

Bijdragen zijn welkom! Fork de repository en maak een pull request.

```bash
# Clone
git clone https://github.com/CharafChnioune/Amsi-kabouters.git

# Install dependencies
cd Amsi-kabouters
pip install -e ".[dev]"

# Run tests
pytest
```

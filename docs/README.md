# Amsi Kabouters

**Nederlands Enterprise AI Agent Framework**

Amsi Kabouters is een volledig Nederlands AI agent framework gebaseerd op CrewAI, uitgebreid met enterprise-grade organisatiestructuur, governance en 24/7 operatie mogelijkheden.

## Belangrijkste Features

### Organisatiestructuur
- **Hiërarchische crews** - Crews als afdelingen met managers en teams
- **6-niveau rollen systeem** - Van uitvoerend tot bestuur
- **Afdelingen met isolatie** - Strikte scheiding tussen teams

### Governance
- **Raad van Commissarissen** - Menselijk toezicht via chat interface
- **Toegangscontrole (ACL)** - Permissies per rol/agent/tool
- **Automatische escalatie** - Bij timeout, fouten, budgetoverschrijding

### Communicatie
- **Opdrachten systeem** - Formele taakdelegatie met status tracking
- **Rapportages** - Gestructureerde rapporten naar management
- **Crew-to-crew berichten** - Directe communicatie tussen crews

### Nederlandse Taal
- Alle prompts en instructies in het Nederlands
- Nederlandse error messages en logging
- Nederlandse API voor organisatie-concepten

## Installatie

```bash
pip install amsi-kabouters
```

Of direct van GitHub:
```bash
pip install git+https://github.com/CharafChnioune/crewAI247.git#subdirectory=lib/crewai
```

## Snel Starten

```python
from crewai import Crew, Agent, Task
from crewai.governance import RaadVanCommissarissen
from crewai.organization import OrganisatieHierarchie, maak_standaard_rollen

# Maak organisatie
org = OrganisatieHierarchie()

# Maak RvC (menselijk toezicht)
rvc = RaadVanCommissarissen(organisatie=org)

# Maak crew met organisatie integratie
crew = Crew(
    agents=[...],
    tasks=[...],
    organisatie=org,
    raad_van_commissarissen=rvc,
)

# Registreer bij RvC
rvc.registreer_crew("mijn_crew", crew)

# Start crew
result = crew.kickoff()

# Geef opdracht via RvC
rvc.verwerk_gebruiker_bericht("@mijn_crew: analyseer de data")
```

## Documentatie

- [Getting Started](getting-started.md) - Eerste stappen
- [Architectuur](architectuur/overzicht.md) - Hoe het werkt
- [Modules](modules/organization.md) - API referentie
- [Guides](guides/raad-van-commissarissen.md) - Praktische handleidingen

## Modules Overzicht

| Module | Beschrijving |
|--------|--------------|
| `organization/` | Hiërarchie, rollen, afdelingen |
| `governance/` | Toegangscontrole, escalatie, RvC |
| `communication/` | Opdrachten, rapporten, berichten |
| `tools/organization_tools/` | Tools voor agents |

## Licentie

MIT License - Gebaseerd op CrewAI door Joao Moura

## Auteur

Charaf Chnioune

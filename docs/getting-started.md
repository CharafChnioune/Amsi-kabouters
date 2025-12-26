# Getting Started met Amsi Kabouters

Deze guide helpt je om snel aan de slag te gaan met Amsi Kabouters.

## Installatie

### Via pip

```bash
pip install amsi-kabouters
```

### Van source

```bash
git clone https://github.com/CharafChnioune/crewAI247.git
cd crewAI247/lib/crewai
pip install -e .
```

## Basisgebruik

### 1. Simpele Crew

```python
from crewai import Crew, Agent, Task

# Maak agents
analist = Agent(
    role="Data Analist",
    goal="Analyseer data en lever inzichten",
    backstory="Je bent een ervaren data analist."
)

# Maak taken
analyse_taak = Task(
    description="Analyseer de verkoopcijfers van Q4",
    expected_output="Een rapport met key insights",
    agent=analist
)

# Maak crew
crew = Crew(
    agents=[analist],
    tasks=[analyse_taak]
)

# Start
result = crew.kickoff()
print(result.raw)
```

### 2. Met Organisatie Structuur

```python
from crewai import Crew, Agent, Task
from crewai.organization import (
    OrganisatieHierarchie,
    Afdeling,
    maak_standaard_rollen
)

# Maak organisatie
org = OrganisatieHierarchie()

# Maak afdeling
data_afdeling = Afdeling(
    naam="Data Team",
    beschrijving="Verantwoordelijk voor data analyse"
)
org.voeg_afdeling_toe(data_afdeling)

# Maak crew met organisatie
crew = Crew(
    agents=[analist],
    tasks=[analyse_taak],
    organisatie=org,
    afdeling_id=data_afdeling.id
)

result = crew.kickoff()
```

### 3. Met Raad van Commissarissen

```python
from crewai.governance import RaadVanCommissarissen

# Maak RvC
rvc = RaadVanCommissarissen(organisatie=org)

# Maak crew met RvC
crew = Crew(
    agents=[analist],
    tasks=[analyse_taak],
    organisatie=org,
    raad_van_commissarissen=rvc
)

# Registreer crew
rvc.registreer_crew("data", crew)

# Nu kan je via chat opdrachten geven
result = rvc.verwerk_gebruiker_bericht("@data: maak een kwartaalrapport")
print(result)

# Bekijk status
print(rvc.krijg_samenvatting())
```

### 4. Met Opdrachten en Rapporten

```python
from crewai.communication import OpdrachtManager, RapportManager

# Maak managers
opdracht_mgr = OpdrachtManager()
rapport_mgr = RapportManager()

# Maak crew met managers
crew = Crew(
    agents=[analist],
    tasks=[analyse_taak],
    organisatie=org,
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr
)

# Crew kan nu rapporten sturen
crew.stuur_rapport(
    type="status",
    titel="Q4 Analyse Voltooid",
    inhoud="De analyse is afgerond met positieve resultaten."
)

# En escaleren indien nodig
crew.escaleer(
    reden="Data kwaliteit probleem ontdekt",
    urgentie="hoog"
)
```

## Hierarchie Opzetten

```python
from crewai.organization import (
    OrganisatieHierarchie,
    Afdeling,
    Rol,
    PermissieNiveau,
    maak_standaard_rollen
)

# Organisatie
org = OrganisatieHierarchie()

# Afdelingen
directie = Afdeling(naam="Directie")
verkoop = Afdeling(naam="Verkoop", parent_afdeling_id=directie.id)
marketing = Afdeling(naam="Marketing", parent_afdeling_id=directie.id)

org.voeg_afdeling_toe(directie)
org.voeg_afdeling_toe(verkoop)
org.voeg_afdeling_toe(marketing)

# Rollen
rollen = maak_standaard_rollen()

# Wijs rollen toe aan crews
org.wijs_rol_toe_aan_crew(verkoop_crew.id, rollen["afdelingshoofd"])
org.wijs_rol_toe_aan_crew(marketing_crew.id, rollen["afdelingshoofd"])

# Rapportagelijnen
from crewai.organization.hierarchy import Rapportagelijn

org.voeg_rapportagelijn_toe(Rapportagelijn(
    medewerker_id=verkoop_crew.id,
    manager_id=directie_crew.id,
    afdeling_id=verkoop.id,
    type="direct"
))
```

## Volgende Stappen

- [Architectuur Overzicht](architectuur/overzicht.md) - Begrijp hoe alles samenwerkt
- [Raad van Commissarissen Guide](guides/raad-van-commissarissen.md) - Menselijk toezicht
- [Escalatie Workflow](guides/escalatie-workflow.md) - Automatische escalatie
- [API Referentie](modules/organization.md) - Alle klassen en methodes

# Organisatie Model

Het organisatie model definieert de hiërarchische structuur van crews en agents.

## Componenten

### OrganisatieHierarchie

Centrale klasse die de gehele organisatiestructuur beheert.

```python
from crewai.organization import OrganisatieHierarchie

org = OrganisatieHierarchie()

# Afdelingen beheren
org.voeg_afdeling_toe(afdeling)
org.krijg_afdeling(afdeling_id)
org.krijg_afdeling_op_naam("Verkoop")

# Rollen beheren
org.wijs_rol_toe(agent_id, rol)
org.wijs_rol_toe_aan_crew(crew_id, rol)
org.krijg_rol(entity_id)

# Hiërarchie queries
org.krijg_management_keten(entity_id)  # [manager, manager's manager, ...]
org.krijg_ondergeschikten(manager_id)
org.krijg_directe_manager(entity_id)

# Permissie checks
org.mag_opdracht_geven(van_id, naar_id)  # True/False
org.mag_rapporteren_aan(van_id, naar_id)
org.mag_escaleren_naar(van_id, naar_id)
```

### Afdeling

Representeert een team of departement.

```python
from crewai.organization import Afdeling, AfdelingsResource

# Resource limieten
resources = AfdelingsResource(
    max_rpm=100,
    max_tokens_per_dag=1000000,
    budget_limiet=10000.0,
    max_gelijktijdige_crews=5
)

afdeling = Afdeling(
    naam="Data Science",
    beschrijving="Machine learning en analytics",
    parent_afdeling_id=None,  # Root afdeling
    manager_agent_id=manager.id,
    resources=resources,
    isolatie_niveau="afdeling"  # open, afdeling, of strikt
)
```

### Rol

Definieert permissies voor een agent of crew.

```python
from crewai.organization import Rol, PermissieNiveau

rol = Rol(
    naam="Team Lead Data",
    beschrijving="Leidt het data team",
    niveau=PermissieNiveau.TEAMLEIDER,

    # Permissies
    kan_delegeren=True,
    kan_escaleren=True,
    kan_goedkeuren=False,
    kan_opdrachten_geven=True,
    kan_rapporten_ontvangen=True,

    # Tool beperkingen
    toegestane_tools=["search", "analyze"],
    geblokkeerde_tools=["deploy"],

    # Relaties
    ontvangt_opdrachten_van=[manager_id],
    escaleert_naar=[director_id],

    # Limieten
    max_budget=5000.0,
    max_gelijktijdige_taken=3
)
```

### PermissieNiveau

De 6 standaard niveaus:

```python
from crewai.organization import PermissieNiveau

# Van laag naar hoog
PermissieNiveau.UITVOEREND      # Alleen taken uitvoeren
PermissieNiveau.TEAMLID         # Beperkt delegeren in team
PermissieNiveau.TEAMLEIDER      # Team aansturen
PermissieNiveau.AFDELINGSHOOFD  # Afdeling aansturen + budget
PermissieNiveau.DIRECTIE        # Alle afdelingen + strategie
PermissieNiveau.BESTUUR         # Volledige controle

# Vergelijken
PermissieNiveau.is_hoger_dan(DIRECTIE, TEAMLEIDER)  # True
PermissieNiveau.is_gelijk_of_hoger_dan(BESTUUR, BESTUUR)  # True
```

### Rapportagelijn

Definieert wie aan wie rapporteert.

```python
from crewai.organization.hierarchy import Rapportagelijn

lijn = Rapportagelijn(
    medewerker_id=agent.id,
    manager_id=manager.id,
    afdeling_id=afdeling.id,
    type="direct",  # direct, functioneel, of dotted_line
    actief_sinds=datetime.now(),
    actief_tot=None  # Permanent
)

org.voeg_rapportagelijn_toe(lijn)
```

## Standaard Rollen

Factory functie voor veelgebruikte rollen:

```python
from crewai.organization import maak_standaard_rollen

rollen = maak_standaard_rollen()

# Beschikbaar:
rollen["bestuurder"]       # BESTUUR niveau
rollen["directeur"]        # DIRECTIE niveau
rollen["afdelingshoofd"]   # AFDELINGSHOOFD niveau
rollen["teamleider"]       # TEAMLEIDER niveau
rollen["teamlid"]          # TEAMLID niveau
rollen["uitvoerend"]       # UITVOEREND niveau
```

## Voorbeeld: Complete Organisatie

```python
from crewai.organization import (
    OrganisatieHierarchie,
    Afdeling,
    maak_standaard_rollen
)
from crewai.organization.hierarchy import Rapportagelijn

# Setup
org = OrganisatieHierarchie()
rollen = maak_standaard_rollen()

# Afdelingen
directie = Afdeling(naam="Directie")
verkoop = Afdeling(naam="Verkoop", parent_afdeling_id=directie.id)
support = Afdeling(naam="Support", parent_afdeling_id=directie.id)

org.voeg_afdeling_toe(directie)
org.voeg_afdeling_toe(verkoop)
org.voeg_afdeling_toe(support)

# Crews met rollen
org.wijs_rol_toe_aan_crew(directie_crew.id, rollen["directeur"])
org.wijs_rol_toe_aan_crew(verkoop_crew.id, rollen["afdelingshoofd"])
org.wijs_rol_toe_aan_crew(support_crew.id, rollen["afdelingshoofd"])

# Rapportagelijnen
org.voeg_rapportagelijn_toe(Rapportagelijn(
    medewerker_id=verkoop_crew.id,
    manager_id=directie_crew.id,
    afdeling_id=verkoop.id,
    type="direct"
))

# Valideer structuur
fouten = org.valideer_structuur()
if fouten:
    print("Structuur fouten:", fouten)

# Genereer organigram
organigram = org.krijg_organigram()
```

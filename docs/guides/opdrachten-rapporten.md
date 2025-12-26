# Opdrachten & Rapporten Guide

Deze guide beschrijft hoe je het opdrachten- en rapportensysteem gebruikt voor communicatie binnen de organisatiehiërarchie.

## Overzicht

Het systeem ondersteunt twee communicatiestromen:

1. **Opdrachten** - Top-down: Manager geeft opdrachten aan medewerkers
2. **Rapporten** - Bottom-up: Medewerkers rapporteren aan management

```
          ┌──────────────────────┐
          │        RvC           │
          │  (Mens/Gebruiker)    │
          └──────────┬───────────┘
                     │
            Opdrachten ↓  ↑ Rapporten
                     │
          ┌──────────┴───────────┐
          │     Directie Crew    │
          └──────────┬───────────┘
                     │
            Opdrachten ↓  ↑ Rapporten
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
 Trading          Research         Risk
   Crew            Crew           Crew
```

## OpdrachtManager

### Setup

```python
from crewai.communication import OpdrachtManager, OpdrachtPrioriteit
from crewai.organization import OrganisatieHierarchie

org = OrganisatieHierarchie()
opdracht_mgr = OpdrachtManager(organisatie=org)
```

### Opdracht Geven

```python
# Geef opdracht
opdracht = opdracht_mgr.geef_opdracht(
    van_id=manager_crew.id,
    naar_id=trading_crew.id,
    titel="Analyseer EUR/USD",
    beschrijving="Maak een technische en fundamentele analyse van EUR/USD voor de komende week",
    prioriteit=OpdrachtPrioriteit.HOOG,
    deadline=datetime.now() + timedelta(hours=4),
    context={
        "focus": "technisch",
        "timeframe": "1W",
        "max_budget": 1000
    },
    vereist_goedkeuring=False
)

print(f"Opdracht {opdracht.id} aangemaakt")
print(f"Status: {opdracht.status.value}")
```

### Prioriteit Niveaus

```python
OpdrachtPrioriteit.LAAG      # Niet urgent
OpdrachtPrioriteit.NORMAAL   # Standaard
OpdrachtPrioriteit.HOOG      # Prioriteit
OpdrachtPrioriteit.KRITIEK   # Onmiddellijke aandacht
```

### Opdracht Lifecycle

```python
# 1. Manager geeft opdracht
opdracht = opdracht_mgr.geef_opdracht(...)
# Status: NIEUW

# 2. Ontvanger accepteert
opdracht_mgr.accepteer_opdracht(opdracht.id)
# Status: GEACCEPTEERD

# 3. Werk begint
opdracht_mgr.update_voortgang(opdracht.id, 25, "Gestart met analyse")
# Status: IN_UITVOERING

# 4. Voortgang updates
opdracht_mgr.update_voortgang(opdracht.id, 50, "Technische analyse klaar")
opdracht_mgr.update_voortgang(opdracht.id, 75, "Fundamentele analyse klaar")

# 5. Voltooien
opdracht_mgr.voltooi_opdracht(
    opdracht.id,
    resultaat="Analyse compleet. Advies: SHORT EUR/USD",
    details={"entry": 1.0850, "target": 1.0750, "stop": 1.0900}
)
# Status: VOLTOOID
```

### Opdracht Weigeren of Escaleren

```python
# Weigeren
opdracht_mgr.weiger_opdracht(
    opdracht.id,
    reden="Onvoldoende resources beschikbaar"
)
# Status: GEWEIGERD

# Escaleren (als er problemen zijn)
# Status wordt: GEESCALEERD

# Markeer als mislukt
opdracht_mgr.markeer_mislukt(
    opdracht.id,
    reden="API timeout, kon data niet ophalen"
)
# Status: MISLUKT
```

### Opdracht Status

```python
from crewai.communication import OpdrachtStatus

OpdrachtStatus.NIEUW                # Zojuist aangemaakt
OpdrachtStatus.GEACCEPTEERD         # Geaccepteerd door ontvanger
OpdrachtStatus.IN_UITVOERING        # Werk is gestart
OpdrachtStatus.WACHT_OP_GOEDKEURING # Wacht op goedkeuring (als vereist)
OpdrachtStatus.VOLTOOID             # Succesvol afgerond
OpdrachtStatus.GEWEIGERD            # Geweigerd door ontvanger
OpdrachtStatus.GEANNULEERD          # Geannuleerd door manager
OpdrachtStatus.GEESCALEERD          # Geescaleerd naar hoger niveau
OpdrachtStatus.MISLUKT              # Gefaald tijdens uitvoering
```

### Opdrachten Queries

```python
# Krijg specifieke opdracht
opdracht = opdracht_mgr.krijg_opdracht(opdracht_id)

# Alle opdrachten voor een entity
mijn_opdrachten = opdracht_mgr.krijg_opdrachten_voor(trading_crew.id)

# Alle open opdrachten
open_opdrachten = opdracht_mgr.krijg_open_opdrachten()

# Filter op status
actieve = opdracht_mgr.krijg_opdrachten_per_status(OpdrachtStatus.IN_UITVOERING)
```

---

## RapportManager

### Setup

```python
from crewai.communication import RapportManager, RapportType, RapportPrioriteit

rapport_mgr = RapportManager(organisatie=org)
```

### Rapport Versturen

```python
rapport = rapport_mgr.stuur_rapport(
    van_id=trading_crew.id,
    naar_ids=[manager_crew.id, rvc.id],
    type=RapportType.RESULTAAT,
    titel="EUR/USD Analyse Voltooid",
    samenvatting="Technische en fundamentele analyse wijzen op SHORT positie",
    inhoud="""
    ## Technische Analyse
    - RSI overbought op 72
    - Dubbele top formatie bij 1.0900
    - Support bij 1.0750

    ## Fundamentele Analyse
    - ECB dovish outlook
    - Fed hawkish rhetoric

    ## Aanbeveling
    SHORT EUR/USD bij 1.0850, target 1.0750, stop 1.0900
    """,
    prioriteit=RapportPrioriteit.BELANGRIJK,
    bijlagen=[
        RapportBijlage(
            naam="chart.png",
            type="image",
            inhoud=chart_data
        )
    ]
)
```

### Rapport Types

```python
RapportType.STATUS      # Voortgangsupdate
RapportType.PROBLEEM    # Issue/blokkade melding
RapportType.RESULTAAT   # Behaald resultaat
RapportType.ESCALATIE   # Escalatie melding
RapportType.VOORTGANG   # Periodieke rapportage
RapportType.ANALYSE     # Analyse met bevindingen
RapportType.AANBEVELING # Actie-suggesties
```

### Rapport Prioriteit

```python
RapportPrioriteit.INFO        # Ter informatie
RapportPrioriteit.NORMAAL     # Standaard
RapportPrioriteit.BELANGRIJK  # Vereist aandacht
RapportPrioriteit.URGENT      # Onmiddellijke actie
```

### Helper Functies

Snel rapporten maken zonder alle parameters:

```python
from crewai.communication import (
    maak_status_rapport,
    maak_probleem_rapport,
    maak_resultaat_rapport
)

# Status rapport
rapport = maak_status_rapport(
    van_id=trading_crew.id,
    naar_ids=[manager_crew.id],
    titel="Dagelijkse update",
    status_tekst="Alle systemen operationeel, 3 trades uitgevoerd"
)

# Probleem rapport
rapport = maak_probleem_rapport(
    van_id=trading_crew.id,
    naar_ids=[manager_crew.id, rvc.id],
    titel="API Connection Issues",
    probleem_beschrijving="Exchange API geeft timeout errors",
    urgentie="hoog"
)

# Resultaat rapport
rapport = maak_resultaat_rapport(
    van_id=trading_crew.id,
    naar_ids=[manager_crew.id],
    titel="Trade Afgerond",
    resultaat="EUR/USD SHORT positie gesloten met +50 pips winst",
    details={"entry": 1.0850, "exit": 1.0800, "pnl": 500}
)
```

### Rapporten Lezen

```python
# Alle rapporten voor een ontvanger
rapporten = rapport_mgr.krijg_rapporten_voor(manager_crew.id)

# Alleen ongelezen
ongelezen = rapport_mgr.krijg_rapporten_voor(
    manager_crew.id,
    alleen_ongelezen=True
)

# Of via shorthand
ongelezen = rapport_mgr.krijg_ongelezen_rapporten(manager_crew.id)

# Markeer als gelezen
rapport_mgr.markeer_gelezen(rapport.id, manager_crew.id)
```

### Reageren op Rapporten

```python
# Voeg reactie toe
reactie = rapport_mgr.voeg_reactie_toe(
    rapport_id=rapport.id,
    auteur_id=manager_crew.id,
    tekst="Goed werk! Ga door met monitoren.",
    actie_vereist=False
)

# Reactie met actie vereist
reactie = rapport_mgr.voeg_reactie_toe(
    rapport_id=rapport.id,
    auteur_id=manager_crew.id,
    tekst="Onderzoek de timeout issues verder",
    actie_vereist=True
)
```

### Statistieken

```python
stats = rapport_mgr.krijg_rapport_statistieken()

print(f"Totaal rapporten: {stats['totaal']}")
print(f"Per type: {stats['per_type']}")
print(f"Per prioriteit: {stats['per_prioriteit']}")
```

---

## Integratie met Crews

### Crew Ontvangt Opdracht

```python
from crewai import Crew

class ManagedCrew(Crew):
    def ontvang_opdracht(self, opdracht, voer_direct_uit=False):
        """Verwerk inkomende opdracht."""

        # Log ontvangst
        print(f"Opdracht ontvangen: {opdracht.titel}")

        # Accepteer automatisch
        self.opdracht_manager.accepteer_opdracht(opdracht.id)

        if voer_direct_uit:
            # Start direct met uitvoering
            self.kickoff(inputs={
                "opdracht": opdracht.beschrijving,
                "context": opdracht.context
            })
        else:
            # Queue voor later
            self.opdrachten_queue.append(opdracht)
```

### Crew Rapporteert

```python
class ManagedCrew(Crew):
    def rapporteer_resultaat(self, titel: str, resultaat: str, details: dict = None):
        """Stuur resultaat naar management."""

        maak_resultaat_rapport(
            van_id=self.id,
            naar_ids=self.rapporteert_aan,
            titel=titel,
            resultaat=resultaat,
            details=details or {}
        )
```

---

## Complete Workflow Voorbeeld

```python
from crewai import Agent, Crew
from crewai.communication import (
    OpdrachtManager,
    RapportManager,
    OpdrachtPrioriteit,
    maak_resultaat_rapport
)
from crewai.organization import OrganisatieHierarchie

# Setup
org = OrganisatieHierarchie()
opdracht_mgr = OpdrachtManager(organisatie=org)
rapport_mgr = RapportManager(organisatie=org)

# Crews
directeur_crew = Crew(agents=[...], tasks=[...])
trading_crew = Crew(agents=[...], tasks=[...])

# === WORKFLOW ===

# 1. Directeur geeft opdracht
opdracht = opdracht_mgr.geef_opdracht(
    van_id=directeur_crew.id,
    naar_id=trading_crew.id,
    titel="Marktanalyse Q1",
    beschrijving="Maak een volledige analyse van Q1 performance",
    prioriteit=OpdrachtPrioriteit.HOOG
)

# 2. Trading accepteert
opdracht_mgr.accepteer_opdracht(opdracht.id)

# 3. Trading werkt aan opdracht
opdracht_mgr.update_voortgang(opdracht.id, 25, "Data verzameld")
opdracht_mgr.update_voortgang(opdracht.id, 50, "Analyse gestart")
opdracht_mgr.update_voortgang(opdracht.id, 75, "Rapport schrijven")

# 4. Trading voltooit en rapporteert
opdracht_mgr.voltooi_opdracht(
    opdracht.id,
    resultaat="Q1 analyse compleet",
    details={"totaal_trades": 150, "win_rate": 0.62, "pnl": 25000}
)

maak_resultaat_rapport(
    van_id=trading_crew.id,
    naar_ids=[directeur_crew.id],
    titel="Q1 Analyse Rapport",
    resultaat="150 trades, 62% win rate, +25k EUR PnL",
    details={"file": "q1_analysis.pdf"}
)

# 5. Directeur leest rapport
for rapport in rapport_mgr.krijg_ongelezen_rapporten(directeur_crew.id):
    print(f"Rapport: {rapport.titel}")
    print(f"Samenvatting: {rapport.samenvatting}")
    rapport_mgr.markeer_gelezen(rapport.id, directeur_crew.id)
```

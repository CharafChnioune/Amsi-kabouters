# Escalatie Workflow Guide

Deze guide beschrijft hoe het escalatiesysteem werkt voor het omhoog brengen van problemen in de organisatiehiërarchie.

## Wat is Escalatie?

Escalatie is het proces waarbij problemen, beslissingen of situaties worden doorgestuurd naar een hoger managementniveau wanneer:

- Een agent/crew het probleem niet zelf kan oplossen
- Extra autorisatie of budget nodig is
- Een deadline wordt overschreden
- Herhaaldelijke fouten optreden
- Menselijke beslissing vereist is

## EscalatieManager

### Setup

```python
from crewai.governance import (
    EscalatieManager,
    EscalatieRegel,
    EscalatieTriggerType,
    EscalatieDoelType,
    EscalatieActieType
)
from crewai.organization import OrganisatieHierarchie

org = OrganisatieHierarchie()
escalatie_mgr = EscalatieManager(organisatie=org)
```

### Escalatie Regels

Definieer wanneer automatisch geescaleerd wordt:

```python
# Timeout regel - escaleer als taak te lang duurt
timeout_regel = EscalatieRegel(
    naam="Timeout escalatie",
    trigger_type=EscalatieTriggerType.TIMEOUT,
    trigger_waarde=3600,  # 1 uur in seconden
    escaleer_naar=EscalatieDoelType.DIRECTE_MANAGER,
    actie=EscalatieActieType.MELDEN,
    prioriteit=5
)

# Fout regel - escaleer bij kritieke fouten
fout_regel = EscalatieRegel(
    naam="Kritieke fout escalatie",
    trigger_type=EscalatieTriggerType.FOUT,
    trigger_waarde="kritiek",  # Ernst niveau
    escaleer_naar=EscalatieDoelType.AFDELING_HOOFD,
    actie=EscalatieActieType.STOPPEN,
    prioriteit=10
)

# Budget regel
budget_regel = EscalatieRegel(
    naam="Budget overschrijding",
    trigger_type=EscalatieTriggerType.BUDGET_OVERSCHREDEN,
    trigger_waarde=10000.0,  # EUR
    escaleer_naar=EscalatieDoelType.DIRECTIE,
    actie=EscalatieActieType.GOEDKEURING_VRAGEN,
    prioriteit=8
)

# Herhaalde pogingen
retry_regel = EscalatieRegel(
    naam="Te veel retries",
    trigger_type=EscalatieTriggerType.HERHAALDE_POGINGEN,
    trigger_waarde=3,  # Na 3 mislukte pogingen
    escaleer_naar=EscalatieDoelType.DIRECTE_MANAGER,
    actie=EscalatieActieType.HERTOEWIJZEN,
    prioriteit=6
)

# Geen voortgang
stagnatie_regel = EscalatieRegel(
    naam="Geen voortgang",
    trigger_type=EscalatieTriggerType.GEEN_VOORTGANG,
    trigger_waarde=1800,  # 30 minuten
    escaleer_naar=EscalatieDoelType.DIRECTE_MANAGER,
    actie=EscalatieActieType.MELDEN,
    prioriteit=4
)

# Voeg regels toe
escalatie_mgr.voeg_regel_toe(timeout_regel)
escalatie_mgr.voeg_regel_toe(fout_regel)
escalatie_mgr.voeg_regel_toe(budget_regel)
escalatie_mgr.voeg_regel_toe(retry_regel)
escalatie_mgr.voeg_regel_toe(stagnatie_regel)
```

### Standaard Regels

Gebruik de helper functie voor veelvoorkomende regels:

```python
from crewai.governance import maak_standaard_escalatie_regels

regels = maak_standaard_escalatie_regels()

# Bevat:
# - Timeout (1 uur)
# - Fout escalatie
# - Budget overschrijding
# - Herhaalde mislukkingen (3x)
# - Geen voortgang (30 min)

for regel in regels:
    escalatie_mgr.voeg_regel_toe(regel)
```

## Trigger Types

```python
EscalatieTriggerType.TIMEOUT
# Taak duurt langer dan trigger_waarde (seconden)

EscalatieTriggerType.FOUT
# Kritieke fout opgetreden (trigger_waarde = ernst niveau)

EscalatieTriggerType.BUDGET_OVERSCHREDEN
# Budget limiet overschreden (trigger_waarde = bedrag)

EscalatieTriggerType.HANDMATIG
# Handmatig getriggerd door agent

EscalatieTriggerType.HERHAALDE_POGINGEN
# Te veel retries (trigger_waarde = aantal)

EscalatieTriggerType.GEEN_VOORTGANG
# Geen progress gemaakt (trigger_waarde = seconden)
```

## Doel Types

```python
EscalatieDoelType.DIRECTE_MANAGER
# Escaleer naar directe leidinggevende

EscalatieDoelType.AFDELING_HOOFD
# Escaleer naar hoofd van afdeling

EscalatieDoelType.DIRECTIE
# Escaleer naar directie niveau

EscalatieDoelType.SPECIFIEK
# Escaleer naar specifiek persoon (gebruik specifiek_doel_id)

EscalatieDoelType.VOLGENDE_IN_KETEN
# Escaleer naar volgende in management keten
```

## Actie Types

```python
EscalatieActieType.MELDEN
# Alleen rapporteren, geen actie

EscalatieActieType.HERTOEWIJZEN
# Taak opnieuw toewijzen aan ander

EscalatieActieType.STOPPEN
# Taak onmiddellijk stoppen

EscalatieActieType.GOEDKEURING_VRAGEN
# Vraag goedkeuring voor voortzetting

EscalatieActieType.PARALLEL_UITVOEREN
# Start parallel uitvoering bij doel
```

## Handmatige Escalatie

Agents kunnen ook handmatig escaleren via de EscaleerTool:

```python
from crewai.tools.organization_tools import EscaleerTool

escaleer_tool = EscaleerTool(
    agent_id=trading_agent.id,
    organisatie=org,
    escalatie_manager=escalatie_mgr
)

# Agent kan nu escaleren met:
# Actie: Escaleer
# Actie Input: {
#     "reden": "Budget limiet bereikt",
#     "context": "Wil trade uitvoeren van 15k EUR maar limiet is 10k",
#     "urgentie": "hoog"
# }
```

## Automatische Trigger Check

Controleer of escalatie nodig is:

```python
# Context van huidige taak
context = {
    "start_tijd": task_start_time,
    "budget_gebruikt": 15000.0,
    "pogingen": 3,
    "laatste_voortgang": last_update_time,
    "fout_niveau": "kritiek"
}

# Check welke regels triggeren
triggered_regels = escalatie_mgr.controleer_triggers(context)

for regel in triggered_regels:
    print(f"Trigger: {regel.naam}")

    # Maak escalatie aan
    escalatie = escalatie_mgr.escaleer(
        bron_id=trading_crew.id,
        bron_type="crew",
        regel=regel,
        reden=f"Automatisch geescaleerd: {regel.naam}",
        context=context
    )
```

## Escalatie Lifecycle

```python
# 1. Escalatie wordt aangemaakt
escalatie = escalatie_mgr.escaleer(
    bron_id=agent_id,
    bron_type="agent",
    regel=timeout_regel,
    reden="Taak timeout",
    context={"elapsed": 3700}
)
# Status: NIEUW

# 2. Manager neemt in behandeling
escalatie_mgr.behandel_escalatie(
    escalatie.id,
    behandeld_door=manager_id
)
# Status: IN_BEHANDELING

# 3. Oplossing
escalatie_mgr.los_escalatie_op(
    escalatie.id,
    reactie="Extra tijd toegekend, deadline verlengd"
)
# Status: OPGELOST

# Of doorsturen naar hoger niveau
escalatie_mgr.stuur_door(
    escalatie.id,
    naar_id=directeur_id
)
```

## Escalatie naar RvC

Bij ernstige escalaties komt de RvC in beeld:

```python
from crewai.governance import RaadVanCommissarissen

rvc = RaadVanCommissarissen(
    organisatie=org,
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr
)

# Escalatie naar RvC niveau
def on_directie_escalatie(escalatie):
    """Wordt aangeroepen als escalatie naar directie/bestuur gaat."""
    rvc.ontvang_escalatie(escalatie)

# De RvC maakt automatisch een goedkeuringsverzoek aan
# De gebruiker kan dan via chat reageren:
rvc.verwerk_gebruiker_bericht("akkoord")  # Goedkeuren
rvc.verwerk_gebruiker_bericht("afwijzen")  # Afwijzen
```

## Integratie met Crew

```python
class ManagedCrew(Crew):
    def _check_escalatie(self, context: dict):
        """Check of escalatie nodig is."""

        triggered = self.escalatie_manager.controleer_triggers(context)

        for regel in triggered:
            self.escalatie_manager.escaleer(
                bron_id=self.id,
                bron_type="crew",
                regel=regel,
                reden=f"Automatisch: {regel.naam}",
                context=context
            )

    def kickoff(self, *args, **kwargs):
        """Kickoff met escalatie monitoring."""

        start_tijd = datetime.now()

        try:
            result = super().kickoff(*args, **kwargs)
            return result

        except Exception as e:
            # Check voor fout escalatie
            self._check_escalatie({
                "fout_niveau": "kritiek",
                "fout_bericht": str(e)
            })
            raise

        finally:
            # Check voor timeout
            elapsed = (datetime.now() - start_tijd).total_seconds()
            self._check_escalatie({
                "start_tijd": start_tijd,
                "elapsed": elapsed
            })
```

## Statistieken

```python
stats = escalatie_mgr.krijg_escalatie_statistieken()

print(f"Totaal escalaties: {stats['totaal']}")
print(f"Openstaand: {stats['openstaand']}")
print(f"Per trigger: {stats['per_trigger']}")
print(f"Gem. oplostijd: {stats['gem_oplostijd']}")
```

## Complete Voorbeeld

```python
from datetime import datetime, timedelta
from crewai.governance import (
    EscalatieManager,
    EscalatieRegel,
    EscalatieTriggerType,
    EscalatieDoelType,
    EscalatieActieType,
    RaadVanCommissarissen,
    maak_standaard_escalatie_regels
)
from crewai.organization import OrganisatieHierarchie

# Setup
org = OrganisatieHierarchie()
escalatie_mgr = EscalatieManager(organisatie=org)

# Standaard regels
for regel in maak_standaard_escalatie_regels():
    escalatie_mgr.voeg_regel_toe(regel)

# Custom regel voor trading
trading_budget_regel = EscalatieRegel(
    naam="Trading budget alarm",
    trigger_type=EscalatieTriggerType.BUDGET_OVERSCHREDEN,
    trigger_waarde=25000.0,
    escaleer_naar=EscalatieDoelType.DIRECTIE,
    actie=EscalatieActieType.GOEDKEURING_VRAGEN,
    prioriteit=9,
    scope="trading"  # Alleen voor trading afdeling
)
escalatie_mgr.voeg_regel_toe(trading_budget_regel)

# Simuleer scenario
task_context = {
    "start_tijd": datetime.now() - timedelta(hours=2),
    "budget_gebruikt": 30000.0,
    "pogingen": 1,
}

# Check triggers
triggered = escalatie_mgr.controleer_triggers(task_context)

if triggered:
    for regel in triggered:
        escalatie = escalatie_mgr.escaleer(
            bron_id=trading_crew.id,
            bron_type="crew",
            regel=regel,
            reden=f"Budget overschrijding: 30k > 25k limiet",
            context=task_context
        )

        print(f"Escalatie aangemaakt: {escalatie.id}")
        print(f"Naar: {regel.escaleer_naar}")
        print(f"Actie: {regel.actie}")

# RvC ontvangt escalatie
rvc.ontvang_escalatie(escalatie)

# Gebruiker handelt af via chat
rvc.verwerk_gebruiker_bericht("akkoord")  # Verhoog budget
# of
rvc.verwerk_gebruiker_bericht("afwijzen")  # Stop activiteit
```

## Best Practices

1. **Stel realistische triggers in** - Niet te agressief (constant escaleren) of te los (problemen missen)

2. **Gebruik de juiste actie** - MELDEN voor informatie, STOPPEN voor kritieke situaties

3. **Documenteer context** - Geef altijd genoeg context mee voor de behandelaar

4. **Monitor statistieken** - Veel escalaties kan wijzen op structurele problemen

5. **Handel tijdig af** - Openstaande escalaties blokkeren vaak werk

# Raad van Commissarissen Guide

Deze guide beschrijft hoe je de Raad van Commissarissen (RvC) module gebruikt voor menselijk toezicht op je AI organisatie.

## Wat is de RvC?

De RvC is de interface waarmee een menselijke gebruiker als hoogste autoriteit (BESTUUR niveau) de AI organisatie kan:

- **Aansturen** via chat-achtige berichten
- **Opdrachten geven** aan alle crews
- **Rapporten ontvangen** van crews
- **Goedkeuringen geven** voor kritieke acties
- **Escalaties behandelen**

## Quick Start

```python
from crewai import Crew
from crewai.governance import RaadVanCommissarissen
from crewai.communication import OpdrachtManager, RapportManager
from crewai.organization import OrganisatieHierarchie

# Setup organisatie
org = OrganisatieHierarchie()
opdracht_mgr = OpdrachtManager(organisatie=org)
rapport_mgr = RapportManager(organisatie=org)

# Maak RvC
rvc = RaadVanCommissarissen(
    organisatie=org,
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr
)

# Registreer crews
rvc.registreer_crew("trading", trading_crew)
rvc.registreer_crew("research", research_crew)
rvc.registreer_crew("risk", risk_crew)
```

## Chat Interface

De RvC parseert berichten automatisch naar acties:

### Opdrachten Geven

Gebruik `@crew_naam: opdracht` om een opdracht te geven:

```python
# Opdracht aan trading crew
rvc.verwerk_gebruiker_bericht("@trading: analyseer de BTC markt")

# Opdracht aan research crew
rvc.verwerk_gebruiker_bericht("@research: onderzoek nieuwe DeFi projecten")

# Urgente opdracht
rvc.verwerk_gebruiker_bericht("@risk: STOP alle open posities onmiddellijk")
```

### Status Opvragen

```python
# Vraag om status
rvc.verwerk_gebruiker_bericht("status?")
rvc.verwerk_gebruiker_bericht("hoe gaat het?")
rvc.verwerk_gebruiker_bericht("voortgang?")
```

Output:
```
=== Organisatie Status ===
Ongelezen rapporten: 5
Urgente rapporten: 1
Wachtende goedkeuringen: 2
Geregistreerde crews: 3

=== Wachtende Goedkeuringen ===
- [abc123...] budget: Verhoging trading limiet
- [def456...] escalatie: Timeout bij marktanalyse
```

### Goedkeuringen Afhandelen

```python
# Keur oudste wachtende verzoek goed
rvc.verwerk_gebruiker_bericht("akkoord")
rvc.verwerk_gebruiker_bericht("ja")

# Keur specifiek verzoek goed
rvc.verwerk_gebruiker_bericht("akkoord #abc123")

# Wijs af
rvc.verwerk_gebruiker_bericht("afwijzen")
rvc.verwerk_gebruiker_bericht("nee")

# Wijs specifiek verzoek af
rvc.verwerk_gebruiker_bericht("afwijzen #abc123")
```

## Bericht Parsing

| Patroon | Actie | Voorbeeld |
|---------|-------|-----------|
| `@crew: tekst` | Opdracht aan crew | `@trading: stop posities` |
| `status?` | Status opvragen | `status?` of `hoe gaat het?` |
| `akkoord` | Goedkeuring geven | `akkoord` of `ja` |
| `akkoord #id` | Specifieke goedkeuring | `akkoord #abc123` |
| `afwijzen` | Afwijzing geven | `afwijzen` of `nee` |
| `afwijzen #id` | Specifieke afwijzing | `afwijzen #abc123` |

## Goedkeuringsworkflow

Crews kunnen goedkeuring vragen voor kritieke acties:

### Vanuit een Crew

```python
# Crew vraagt goedkeuring
verzoek = rvc.vraag_goedkeuring(
    type="budget",
    beschrijving="Verhoging trading limiet van 50k naar 100k EUR",
    aanvrager_id=trading_crew.id,
    aanvrager_naam="Trading Crew",
    details={
        "huidig_limiet": 50000,
        "nieuw_limiet": 100000,
        "reden": "Grotere marktopportuniteiten"
    }
)
```

### Goedkeuring Afhandelen

```python
# Bekijk wachtende verzoeken
for verzoek in rvc.krijg_wachtende_goedkeuringen():
    print(f"[{verzoek.id}] {verzoek.type}: {verzoek.beschrijving}")
    print(f"  Van: {verzoek.aanvrager_naam}")
    print(f"  Details: {verzoek.details}")
    print()

# Goedkeuren via API
rvc.keur_goed(verzoek.id, "Akkoord, maar monitor de resultaten")

# Of afwijzen
rvc.wijs_af(verzoek.id, "Te risicovol in huidige marktomstandigheden")
```

### Verzoek Types

| Type | Beschrijving | Wanneer |
|------|-------------|---------|
| `opdracht` | Goedkeuring voor opdracht | Kritieke opdrachten |
| `budget` | Budget/limiet aanpassingen | Verhogingen boven threshold |
| `escalatie` | Escalatie naar RvC | Problemen die aandacht vereisen |
| `strategie` | Strategische beslissingen | Koerswijzigingen |

## Rapporten Ontvangen

### Rapporten Ophalen

```python
# Alle rapporten
rapporten = rvc.krijg_rapporten()

# Alleen ongelezen
ongelezen = rvc.krijg_rapporten(alleen_ongelezen=True)

# Filteren op type
problemen = rvc.krijg_rapporten(type_filter="probleem")
resultaten = rvc.krijg_rapporten(type_filter="resultaat")

# Limiet instellen
laatste_10 = rvc.krijg_rapporten(limiet=10)
```

### Rapport Verwerken

```python
for rapport in rvc.krijg_rapporten(alleen_ongelezen=True):
    print(f"[{rapport.type.value}] {rapport.titel}")
    print(f"  Van: {rapport.van_id}")
    print(f"  {rapport.samenvatting}")
    print()

    # Markeer als gelezen
    rvc.markeer_gelezen(rapport.id)
```

## Callbacks voor UI Integratie

De RvC ondersteunt callbacks voor real-time notificaties:

```python
def on_nieuw_rapport(rapport):
    print(f"Nieuw rapport: {rapport.titel}")
    # Push notificatie, email, etc.

def on_goedkeuring_vereist(verzoek):
    print(f"Goedkeuring nodig: {verzoek.beschrijving}")
    # Alert gebruiker

def on_escalatie(escalatie):
    print(f"ESCALATIE: {escalatie.reden}")
    # Urgente notificatie

def on_bericht(bericht):
    print(f"Bericht: {bericht.inhoud}")
    # Log naar chat interface

# RvC met callbacks
rvc = RaadVanCommissarissen(
    organisatie=org,
    on_nieuw_rapport=on_nieuw_rapport,
    on_goedkeuring_vereist=on_goedkeuring_vereist,
    on_escalatie=on_escalatie,
    on_bericht=on_bericht
)
```

## Dashboard Integratie

```python
# Status samenvatting voor dashboard
status = rvc.krijg_samenvatting()

dashboard_data = {
    "ongelezen_rapporten": status["ongelezen_rapporten"],
    "urgente_items": status["urgente_rapporten"],
    "actie_vereist": status["wachtende_goedkeuringen"],
    "crews": status["aantal_crews"],
}

# Wachtende acties voor todo list
acties = []
for verzoek in rvc.krijg_wachtende_goedkeuringen():
    acties.append({
        "id": str(verzoek.id),
        "type": verzoek.type,
        "beschrijving": verzoek.beschrijving,
        "van": verzoek.aanvrager_naam,
        "sinds": verzoek.aangevraagd_op.isoformat()
    })
```

## Complete Voorbeeld

```python
from crewai import Agent, Crew, Task
from crewai.governance import RaadVanCommissarissen
from crewai.communication import OpdrachtManager, RapportManager
from crewai.organization import OrganisatieHierarchie

# Setup
org = OrganisatieHierarchie()
opdracht_mgr = OpdrachtManager(organisatie=org)
rapport_mgr = RapportManager(organisatie=org)

# Maak crews
trading_agent = Agent(role="Trader", goal="Trade crypto")
trading_crew = Crew(agents=[trading_agent], tasks=[...])

risk_agent = Agent(role="Risk Manager", goal="Beheer risico")
risk_crew = Crew(agents=[risk_agent], tasks=[...])

# Maak RvC
rvc = RaadVanCommissarissen(
    organisatie=org,
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr
)

# Registreer crews
rvc.registreer_crew("trading", trading_crew)
rvc.registreer_crew("risk", risk_crew)

# === Gebruiker interactie ===

# Geef opdracht aan trading
result = rvc.verwerk_gebruiker_bericht("@trading: koop 0.1 BTC bij gunstige prijs")
print(result)

# Check status
result = rvc.verwerk_gebruiker_bericht("status?")
print(result)

# Handel goedkeuringen af
for verzoek in rvc.krijg_wachtende_goedkeuringen():
    if verzoek.type == "budget" and verzoek.details.get("nieuw_limiet", 0) < 100000:
        rvc.keur_goed(verzoek.id, "Akkoord tot 100k")
    else:
        rvc.wijs_af(verzoek.id, "Meer analyse nodig")

# Of via chat
rvc.verwerk_gebruiker_bericht("akkoord")
```

## Best Practices

1. **Registreer alle crews** - Alleen geregistreerde crews kunnen aangestuurd worden via `@naam:`

2. **Gebruik callbacks** - Voor real-time UI updates en notificaties

3. **Handel goedkeuringen tijdig af** - Wachtende goedkeuringen blokkeren crews

4. **Lees rapporten regelmatig** - Vooral urgente rapporten vereisen aandacht

5. **Gebruik specifieke IDs** - Bij meerdere wachtende goedkeuringen, gebruik `akkoord #id`

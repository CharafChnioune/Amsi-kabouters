# Architectuur Overzicht

Amsi Kabouters breidt CrewAI uit met een enterprise-grade organisatielaag.

## Module Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Raad van Commissarissen                       │
│                    (Menselijk Toezicht)                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GOVERNANCE LAAG                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Toegangs-    │  │ Escalatie-   │  │ Goedkeurings-        │   │
│  │ Controle     │  │ Manager      │  │ Workflow             │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORGANISATIE LAAG                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Hierarchie   │  │ Rollen &     │  │ Afdelingen           │   │
│  │              │  │ Permissies   │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMMUNICATIE LAAG                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Opdrachten   │  │ Rapporten    │  │ Crew Berichten       │   │
│  │ Manager      │  │ Manager      │  │ Kanaal               │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CREWAI CORE                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Crew         │  │ Agent        │  │ Task                 │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Dataflow

### Opdracht Flow

```
RvC/Manager                     Crew                        Agent
    │                            │                            │
    │ ─── geef_opdracht() ────>  │                            │
    │                            │                            │
    │                            │ ─── selecteer_agent() ──>  │
    │                            │                            │
    │                            │ <── ontvang_opdracht() ─── │
    │                            │                            │
    │                            │ ─── kickoff() ──────────>  │
    │                            │                            │
    │                            │ <── result ─────────────── │
    │                            │                            │
    │ <── stuur_rapport() ─────  │                            │
    │                            │                            │
```

### Escalatie Flow

```
Agent/Crew                 EscalatieManager              RvC/Manager
    │                            │                            │
    │ ─── trigger detectie ──>   │                            │
    │                            │                            │
    │                            │ ─── bepaal_doel() ────>    │
    │                            │                            │
    │                            │ ─── escaleer() ────────>   │
    │                            │                            │
    │                            │ <── behandel/los_op() ──── │
    │                            │                            │
    │ <── resultaat ───────────  │                            │
```

## Event Systeem

Alle organisatie-acties emitten events via de CrewAI event bus:

```python
# Opdracht events
OpdrachtOntvangenEvent
OpdrachtVoltooidEvent
OpdrachtGeescaleerdEvent

# Rapport events
RapportVerstuurdEvent
RapportOntvangenEvent

# Escalatie events
EscalatieGetriggerdEvent
EscalatieOpgelostEvent

# RvC events
RvCOpdrachtGegevenEvent
RvCBeslissingEvent
GoedkeuringVereistEvent

# Permissie events
PermissieGeweigerdEvent
```

## Permissie Model

### 6-Niveau Hiërarchie

```
BESTUUR          ────────────────────────────────────  Hoogste
    │
DIRECTIE         ────────────────────────────────
    │
AFDELINGSHOOFD   ──────────────────────────
    │
TEAMLEIDER       ────────────────────
    │
TEAMLID          ──────────────
    │
UITVOEREND       ────────  Laagste
```

### Permissie Types

| Permissie | Beschrijving |
|-----------|--------------|
| `kan_delegeren` | Mag taken delegeren naar anderen |
| `kan_escaleren` | Mag problemen escaleren |
| `kan_goedkeuren` | Mag beslissingen goedkeuren |
| `kan_opdrachten_geven` | Mag opdrachten geven aan lager niveau |
| `kan_rapporten_ontvangen` | Ontvangt rapporten van lager niveau |

## Isolatie Niveaus

```python
"open"       # Geen beperkingen op communicatie
"afdeling"   # Alleen binnen afdeling + goedgekeurde afdelingen
"strikt"     # Alleen binnen eigen crew
```

## Volgende

- [Organisatie Model](organisatie-model.md) - Details over hiërarchie
- [Governance Model](governance-model.md) - Details over toegang en escalatie

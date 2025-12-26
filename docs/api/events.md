# Events API Referentie

Deze pagina documenteert alle organisatie-gerelateerde event types.

## Overzicht

Amsi Kabouters gebruikt een event bus voor communicatie tussen componenten. Events worden geemit bij belangrijke acties en kunnen worden gesubscribed voor monitoring, logging, of UI updates.

## Import

```python
from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.organization_events import (
    # Opdracht events
    OpdrachtOntvangenEvent,
    OpdrachtVoltooidEvent,
    OpdrachtGeweigerdEvent,
    OpdrachtGeescaleerdEvent,

    # Rapport events
    RapportOntvangenEvent,
    RapportVerstuurdEvent,

    # Escalatie events
    EscalatieGetriggerdEvent,
    EscalatieOpgelostEvent,

    # Goedkeuring events
    GoedkeuringVereistEvent,
    GoedkeuringGegevenEvent,
    GoedkeuringAfgewezenEvent,

    # RvC events
    RvCBerichtOntvangenEvent,
    RvCOpdrachtGegevenEvent,
    RvCBeslissingEvent,

    # Permissie events
    PermissieGeweigerdEvent,
    PermissieToegestaanEvent,
)
```

## Subscriben op Events

```python
from crewai.events.event_bus import crewai_event_bus

# Subscribe op specifiek event type
@crewai_event_bus.on(OpdrachtOntvangenEvent)
def handle_opdracht(event: OpdrachtOntvangenEvent):
    print(f"Opdracht ontvangen: {event.opdracht_titel}")
    print(f"Van: {event.van_id}")
    print(f"Prioriteit: {event.prioriteit}")

# Subscribe op alle organisatie events
@crewai_event_bus.on(OrganisatieBaseEvent)
def handle_all_org_events(event):
    print(f"Org event: {event.type}")
```

---

## Opdracht Events

### OpdrachtOntvangenEvent

Geemit wanneer een crew/agent een opdracht ontvangt.

```python
class OpdrachtOntvangenEvent:
    type: str = "opdracht_ontvangen"

    # Basis velden
    crew_id: UUID | None
    crew_naam: str | None
    afdeling_id: UUID | None

    # Opdracht velden
    opdracht: Opdracht | None      # Volledige opdracht object
    opdracht_id: UUID | None
    opdracht_titel: str | None
    van_id: UUID | None
    prioriteit: str | None         # "laag", "normaal", "hoog", "kritiek"
```

**Voorbeeld:**
```python
@crewai_event_bus.on(OpdrachtOntvangenEvent)
def on_opdracht(event):
    if event.prioriteit == "kritiek":
        send_alert(f"KRITIEKE opdracht: {event.opdracht_titel}")
```

### OpdrachtVoltooidEvent

Geemit wanneer een opdracht succesvol is afgerond.

```python
class OpdrachtVoltooidEvent:
    type: str = "opdracht_voltooid"

    opdracht_id: UUID | None
    opdracht_titel: str | None
    resultaat: str | None
    succes: bool = True
```

### OpdrachtGeweigerdEvent

Geemit wanneer een opdracht wordt geweigerd.

```python
class OpdrachtGeweigerdEvent:
    type: str = "opdracht_geweigerd"

    opdracht_id: UUID | None
    opdracht_titel: str | None
    reden: str | None
```

### OpdrachtGeescaleerdEvent

Geemit wanneer een opdracht wordt geescaleerd.

```python
class OpdrachtGeescaleerdEvent:
    type: str = "opdracht_geescaleerd"

    opdracht_id: UUID | None
    escalatie_reden: str | None
    naar_id: UUID | None           # Escalatie doel
```

---

## Rapport Events

### RapportOntvangenEvent

Geemit wanneer een rapport wordt ontvangen.

```python
class RapportOntvangenEvent:
    type: str = "rapport_ontvangen"

    rapport: Rapport | None
    rapport_id: UUID | None
    rapport_titel: str | None
    van_id: UUID | None
    rapport_type: str | None       # "status", "probleem", etc.
    prioriteit: str | None
```

### RapportVerstuurdEvent

Geemit wanneer een rapport wordt verstuurd.

```python
class RapportVerstuurdEvent:
    type: str = "rapport_verstuurd"

    rapport_id: UUID | None
    rapport_titel: str | None
    naar_ids: list[UUID]
    rapport_type: str | None
```

---

## Escalatie Events

### EscalatieGetriggerdEvent

Geemit wanneer een escalatie wordt getriggerd.

```python
class EscalatieGetriggerdEvent:
    type: str = "escalatie_getriggerd"

    escalatie: Escalatie | None
    escalatie_id: UUID | None
    trigger_type: str | None       # "timeout", "fout", "budget", etc.
    reden: str | None
    naar_id: UUID | None
```

**Voorbeeld:**
```python
@crewai_event_bus.on(EscalatieGetriggerdEvent)
def on_escalatie(event):
    if event.trigger_type == "fout":
        log_error(f"Escalatie door fout: {event.reden}")
```

### EscalatieOpgelostEvent

Geemit wanneer een escalatie wordt opgelost.

```python
class EscalatieOpgelostEvent:
    type: str = "escalatie_opgelost"

    escalatie_id: UUID | None
    opgelost_door: UUID | None
    reactie: str | None
```

---

## Goedkeuring Events

### GoedkeuringVereistEvent

Geemit wanneer goedkeuring nodig is van RvC/management.

```python
class GoedkeuringVereistEvent:
    type: str = "goedkeuring_vereist"

    verzoek_id: UUID | None
    verzoek_type: str | None       # "opdracht", "budget", "escalatie", "strategie"
    beschrijving: str | None
    aanvrager_id: UUID | None
    aanvrager_naam: str | None
```

**Voorbeeld:**
```python
@crewai_event_bus.on(GoedkeuringVereistEvent)
def on_goedkeuring_nodig(event):
    notify_user(f"Goedkeuring nodig: {event.beschrijving}")
```

### GoedkeuringGegevenEvent

Geemit wanneer goedkeuring wordt gegeven.

```python
class GoedkeuringGegevenEvent:
    type: str = "goedkeuring_gegeven"

    verzoek_id: UUID | None
    goedgekeurd_door: UUID | None
    toelichting: str | None
```

### GoedkeuringAfgewezenEvent

Geemit wanneer goedkeuring wordt afgewezen.

```python
class GoedkeuringAfgewezenEvent:
    type: str = "goedkeuring_afgewezen"

    verzoek_id: UUID | None
    afgewezen_door: UUID | None
    reden: str | None
```

---

## RvC Events

### RvCBerichtOntvangenEvent

Geemit wanneer de RvC een bericht ontvangt.

```python
class RvCBerichtOntvangenEvent:
    type: str = "rvc_bericht_ontvangen"

    bericht_id: UUID | None
    van_crew_id: UUID | None
    van_crew_naam: str | None
    inhoud: str | None
    bericht_type: str | None       # "rapport", "vraag", "escalatie"
```

### RvCOpdrachtGegevenEvent

Geemit wanneer de RvC een opdracht geeft.

```python
class RvCOpdrachtGegevenEvent:
    type: str = "rvc_opdracht_gegeven"

    opdracht_id: UUID | None
    naar_id: UUID | None
    naar_naam: str | None
    opdracht_titel: str | None
    prioriteit: str | None
```

### RvCBeslissingEvent

Geemit wanneer de RvC een beslissing neemt.

```python
class RvCBeslissingEvent:
    type: str = "rvc_beslissing"

    verzoek_id: UUID | None
    beslissing: str | None         # "goedgekeurd", "afgewezen", "aangepast"
    toelichting: str | None
```

---

## Permissie Events

### PermissieGeweigerdEvent

Geemit wanneer een actie wordt geweigerd door permissie check.

```python
class PermissieGeweigerdEvent:
    type: str = "permissie_geweigerd"

    agent_id: UUID | None
    agent_naam: str | None
    resource_type: str | None      # "tool", "crew", "agent"
    resource_id: UUID | str | None
    actie: str | None              # "uitvoeren", "lezen", "schrijven"
    reden: str | None
```

**Voorbeeld:**
```python
@crewai_event_bus.on(PermissieGeweigerdEvent)
def on_permissie_geweigerd(event):
    audit_log.warning(
        f"DENIED: {event.agent_naam} tried {event.actie} on {event.resource_type}"
    )
```

### PermissieToegestaanEvent

Geemit wanneer een actie wordt toegestaan (voor audit).

```python
class PermissieToegestaanEvent:
    type: str = "permissie_toegestaan"

    agent_id: UUID | None
    resource_type: str | None
    resource_id: UUID | str | None
    actie: str | None
```

---

## Event Monitoring

### Logging Setup

```python
import logging
from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.organization_events import OrganisatieBaseEvent

logger = logging.getLogger("amsi_kabouters")

@crewai_event_bus.on(OrganisatieBaseEvent)
def log_all_events(event):
    logger.info(f"Event: {event.type}", extra={
        "event_type": event.type,
        "crew_id": str(event.crew_id) if event.crew_id else None,
        "crew_naam": event.crew_naam,
    })
```

### Metrics Collection

```python
from prometheus_client import Counter

org_events = Counter(
    "amsi_kabouters_org_events",
    "Organization events",
    ["event_type"]
)

@crewai_event_bus.on(OrganisatieBaseEvent)
def count_events(event):
    org_events.labels(event_type=event.type).inc()
```

### UI Notifications

```python
import websockets

async def notify_ui(event):
    await websocket.send(json.dumps({
        "type": event.type,
        "data": event.to_json()
    }))

@crewai_event_bus.on(GoedkeuringVereistEvent)
async def on_approval_needed(event):
    await notify_ui(event)

@crewai_event_bus.on(EscalatieGetriggerdEvent)
async def on_escalation(event):
    await notify_ui(event)
```

---

## Event Type Overzicht

| Event | Type String | Wanneer |
|-------|-------------|---------|
| `OpdrachtOntvangenEvent` | `opdracht_ontvangen` | Crew ontvangt opdracht |
| `OpdrachtVoltooidEvent` | `opdracht_voltooid` | Opdracht afgerond |
| `OpdrachtGeweigerdEvent` | `opdracht_geweigerd` | Opdracht geweigerd |
| `OpdrachtGeescaleerdEvent` | `opdracht_geescaleerd` | Opdracht geescaleerd |
| `RapportOntvangenEvent` | `rapport_ontvangen` | Rapport ontvangen |
| `RapportVerstuurdEvent` | `rapport_verstuurd` | Rapport verstuurd |
| `EscalatieGetriggerdEvent` | `escalatie_getriggerd` | Escalatie gestart |
| `EscalatieOpgelostEvent` | `escalatie_opgelost` | Escalatie opgelost |
| `GoedkeuringVereistEvent` | `goedkeuring_vereist` | Goedkeuring nodig |
| `GoedkeuringGegevenEvent` | `goedkeuring_gegeven` | Goedkeuring gegeven |
| `GoedkeuringAfgewezenEvent` | `goedkeuring_afgewezen` | Goedkeuring afgewezen |
| `RvCBerichtOntvangenEvent` | `rvc_bericht_ontvangen` | RvC ontvangt bericht |
| `RvCOpdrachtGegevenEvent` | `rvc_opdracht_gegeven` | RvC geeft opdracht |
| `RvCBeslissingEvent` | `rvc_beslissing` | RvC neemt beslissing |
| `PermissieGeweigerdEvent` | `permissie_geweigerd` | Toegang geweigerd |
| `PermissieToegestaanEvent` | `permissie_toegestaan` | Toegang toegestaan |

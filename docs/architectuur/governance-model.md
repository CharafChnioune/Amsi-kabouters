# Governance Model

Het governance model biedt toegangscontrole, escalatie en menselijk toezicht.

## Componenten

### ToegangsControle

ACL-gebaseerd toegangssysteem met regels en voorwaarden.

```python
from crewai.governance import (
    ToegangsControle,
    ToegangsRegel,
    TijdsVoorwaarde,
    BudgetVoorwaarde
)

# Maak controle
toegang = ToegangsControle(log_toegang=True)

# Voeg regels toe
regel = ToegangsRegel(
    naam="Trading werkuren",
    resource_type="tool",
    principal_type="agent",
    principal_id=trader_id,
    actie="uitvoeren",
    effect="toestaan",
    prioriteit=10,

    voorwaarden=ToegangsVoorwaarden(
        tijd=TijdsVoorwaarde(
            start_uur=9,
            eind_uur=17,
            weekdagen=[0, 1, 2, 3, 4]  # Ma-Vr
        ),
        budget=BudgetVoorwaarde(
            max_per_actie=10000.0,
            max_totaal=100000.0
        )
    )
)

toegang.voeg_regel_toe(regel)

# Controleer toegang
toegestaan, reden = toegang.controleer_toegang(
    principal_id=trader_id,
    principal_type="agent",
    resource_type="tool",
    resource_id=trade_tool_id,
    actie="uitvoeren",
    context={"bedrag": 5000}
)

if not toegestaan:
    print(f"Toegang geweigerd: {reden}")
```

### EscalatieManager

Automatische en handmatige escalatie naar management.

```python
from crewai.governance import (
    EscalatieManager,
    EscalatieRegel,
    EscalatieTriggerType,
    EscalatieDoelType,
    EscalatieActieType
)

# Maak manager
escalatie_mgr = EscalatieManager(organisatie=org)

# Voeg regel toe
regel = EscalatieRegel(
    naam="Timeout escalatie",
    trigger_type=EscalatieTriggerType.TIMEOUT,
    trigger_waarde=3600,  # 1 uur in seconden
    escaleer_naar=EscalatieDoelType.DIRECTE_MANAGER,
    actie=EscalatieActieType.MELDEN,
    prioriteit=5
)

escalatie_mgr.voeg_regel_toe(regel)

# Check triggers
context = {
    "start_tijd": task_start_time,
    "budget_gebruikt": 15000.0,
    "pogingen": 3
}

triggered = escalatie_mgr.controleer_triggers(context)

# Escaleer
if triggered:
    escalatie = escalatie_mgr.escaleer(
        bron_id=agent_id,
        bron_type="agent",
        regel=triggered[0],
        reden="Task duurde te lang"
    )

# Manager handelt af
escalatie_mgr.behandel_escalatie(escalatie.id, behandeld_door=manager_id)
escalatie_mgr.los_escalatie_op(escalatie.id, reactie="Taak opnieuw gestart")
```

### Trigger Types

```python
EscalatieTriggerType.TIMEOUT           # Taak duurt te lang
EscalatieTriggerType.FOUT              # Kritieke fout opgetreden
EscalatieTriggerType.BUDGET_OVERSCHREDEN
EscalatieTriggerType.HANDMATIG         # Handmatig getriggerd
EscalatieTriggerType.HERHAALDE_POGINGEN  # Te veel retries
EscalatieTriggerType.GEEN_VOORTGANG    # Geen progress
```

### Doel Types

```python
EscalatieDoelType.DIRECTE_MANAGER      # Directe leidinggevende
EscalatieDoelType.AFDELING_HOOFD       # Hoofd van afdeling
EscalatieDoelType.DIRECTIE             # Directie niveau
EscalatieDoelType.SPECIFIEK            # Specifiek persoon
EscalatieDoelType.VOLGENDE_IN_KETEN    # Volgende in management keten
```

### Actie Types

```python
EscalatieActieType.MELDEN              # Alleen rapporteren
EscalatieActieType.HERTOEWIJZEN        # Taak opnieuw toewijzen
EscalatieActieType.STOPPEN             # Taak stoppen
EscalatieActieType.GOEDKEURING_VRAGEN  # Vraag goedkeuring
EscalatieActieType.PARALLEL_UITVOEREN  # Start parallel bij doel
```

### Standaard Regels

```python
from crewai.governance import maak_standaard_escalatie_regels

regels = maak_standaard_escalatie_regels()

# Bevat:
# - Timeout (1 uur)
# - Fout escalatie
# - Budget overschrijding
# - Herhaalde mislukkingen (3x)
# - Geen voortgang (30 min)
```

## RaadVanCommissarissen

Menselijk toezicht via chat-achtige interface.

```python
from crewai.governance import RaadVanCommissarissen

rvc = RaadVanCommissarissen(
    organisatie=org,
    opdracht_manager=opdracht_mgr,
    rapport_manager=rapport_mgr
)

# Registreer crews
rvc.registreer_crew("trading", trading_crew)
rvc.registreer_crew("risk", risk_crew)

# Verwerk berichten
rvc.verwerk_gebruiker_bericht("@trading: stop alle posities")
rvc.verwerk_gebruiker_bericht("status?")
rvc.verwerk_gebruiker_bericht("akkoord")

# Goedkeuringsworkflow
for verzoek in rvc.krijg_wachtende_goedkeuringen():
    print(f"{verzoek.type}: {verzoek.beschrijving}")
    rvc.keur_goed(verzoek.id, "Akkoord")
    # of: rvc.wijs_af(verzoek.id, "Te risicovol")

# Status
samenvatting = rvc.krijg_samenvatting()
print(f"Ongelezen: {samenvatting['ongelezen_rapporten']}")
print(f"Wachtend: {samenvatting['wachtende_goedkeuringen']}")
```

### Bericht Parsing

De RvC parseert berichten automatisch:

| Patroon | Actie |
|---------|-------|
| `@crew: tekst` | Opdracht aan crew |
| `status?` | Vraag om status |
| `akkoord` / `ja` | Goedkeuring oudste verzoek |
| `afwijzen` / `nee` | Afwijzing oudste verzoek |
| `akkoord #123` | Goedkeuring specifiek verzoek |

### Callbacks

```python
def on_rapport(rapport):
    print(f"Nieuw rapport: {rapport.titel}")

def on_goedkeuring(verzoek):
    print(f"Goedkeuring nodig: {verzoek.beschrijving}")

rvc = RaadVanCommissarissen(
    organisatie=org,
    on_nieuw_rapport=on_rapport,
    on_goedkeuring_vereist=on_goedkeuring
)
```

## Helper Functies

```python
from crewai.governance import (
    maak_allow_all_regel,
    maak_werkuren_regel,
    maak_budget_regel
)

# Alles toestaan voor specifieke agent
regel = maak_allow_all_regel(agent_id, "agent")

# Werkuren regel (9-17, ma-vr)
regel = maak_werkuren_regel(
    principal_id=agent_id,
    principal_type="agent",
    resource_type="tool",
    actie="uitvoeren",
    start_uur=9,
    eind_uur=17
)

# Budget regel
regel = maak_budget_regel(
    principal_id=agent_id,
    principal_type="agent",
    resource_type="tool",
    actie="uitvoeren",
    max_bedrag=10000.0,
    max_totaal=100000.0
)
```

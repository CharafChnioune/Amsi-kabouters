"""Event type definitions for CrewAI.

This module contains all event types used throughout the CrewAI system
for monitoring and extending agent, crew, task, and tool execution.
"""

from crewai.events.types.continuous_events import (
    ContinuousAgentActionEvent,
    ContinuousAgentObservationEvent,
    ContinuousErrorEvent,
    ContinuousHealthCheckEvent,
    ContinuousIterationCompleteEvent,
    ContinuousKickoffStartedEvent,
    ContinuousKickoffStoppedEvent,
    ContinuousPausedEvent,
    ContinuousResumedEvent,
)
from crewai.events.types.organization_events import (
    # Base
    OrganisatieBaseEvent,
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

__all__ = [
    # Continuous events
    "ContinuousKickoffStartedEvent",
    "ContinuousKickoffStoppedEvent",
    "ContinuousAgentActionEvent",
    "ContinuousAgentObservationEvent",
    "ContinuousIterationCompleteEvent",
    "ContinuousHealthCheckEvent",
    "ContinuousPausedEvent",
    "ContinuousResumedEvent",
    "ContinuousErrorEvent",
    # Organization events - Base
    "OrganisatieBaseEvent",
    # Organization events - Opdrachten
    "OpdrachtOntvangenEvent",
    "OpdrachtVoltooidEvent",
    "OpdrachtGeweigerdEvent",
    "OpdrachtGeescaleerdEvent",
    # Organization events - Rapporten
    "RapportOntvangenEvent",
    "RapportVerstuurdEvent",
    # Organization events - Escalaties
    "EscalatieGetriggerdEvent",
    "EscalatieOpgelostEvent",
    # Organization events - Goedkeuringen
    "GoedkeuringVereistEvent",
    "GoedkeuringGegevenEvent",
    "GoedkeuringAfgewezenEvent",
    # Organization events - RvC
    "RvCBerichtOntvangenEvent",
    "RvCOpdrachtGegevenEvent",
    "RvCBeslissingEvent",
    # Organization events - Permissies
    "PermissieGeweigerdEvent",
    "PermissieToegestaanEvent",
]

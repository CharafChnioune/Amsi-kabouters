from typing import Any
import warnings

from crewai.agent.core import Agent
from crewai.crew import Crew
from crewai.crews.crew_output import CrewOutput
from crewai.flow.flow import Flow
from crewai.knowledge.knowledge import Knowledge
from crewai.llm import LLM
from crewai.llms.base_llm import BaseLLM
from crewai.process import Process
from crewai.task import Task
from crewai.tasks.llm_guardrail import LLMGuardrail
from crewai.tasks.task_output import TaskOutput


def _suppress_pydantic_deprecation_warnings() -> None:
    """Suppress Pydantic deprecation warnings using targeted monkey patch."""
    original_warn = warnings.warn

    def filtered_warn(
        message: Any,
        category: type | None = None,
        stacklevel: int = 1,
        source: Any = None,
    ) -> Any:
        if (
            category
            and hasattr(category, "__module__")
            and category.__module__ == "pydantic.warnings"
        ):
            return None
        return original_warn(message, category, stacklevel + 1, source)

    warnings.warn = filtered_warn  # type: ignore[assignment]


_suppress_pydantic_deprecation_warnings()

__version__ = "1.0.0"
__package_name__ = "amsi-kabouters"
__description__ = "Nederlands Enterprise AI Agent Framework"
__all__ = [
    # Core
    "Agent",
    "Crew",
    "Task",
    "Flow",
    "Process",
    # LLM
    "LLM",
    "BaseLLM",
    # Output
    "CrewOutput",
    "TaskOutput",
    # Knowledge & Guards
    "Knowledge",
    "LLMGuardrail",
    # Package info
    "__version__",
    "__package_name__",
    "__description__",
]

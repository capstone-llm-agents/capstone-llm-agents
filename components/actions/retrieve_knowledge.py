"""The hello action simply prints a greeting message."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.knowledge_base.knowledge_base import KnowledgeBase

EXAMPLE_KB = KnowledgeBase()
EXAMPLE_KB.add_fact("The house is purple.")


class RetrieveKnowledge(Action):
    """An action that prints a greeting message."""

    def __init__(self) -> None:
        """Initialize the RetrieveKnowledge action."""
        super().__init__(description="Retrieves knowledge from the knowledge base.")

    @override
    def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by printing a greeting."""
        facts = EXAMPLE_KB.query("")

        res = ActionResult()
        res.set_param("facts", facts)
        return res

"""Action class for the multi-agent system."""

from typing import Any, override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.schema import DictSchema
from llm_mas.fragment.fragment import Fragment
from llm_mas.fragment.kind import FragmentKind


class FragAction(Action):
    """Base class for all actions in the system."""

    in_frag_schema: DictSchema
    out_frag_schema: DictSchema

    def __init__(
        self,
        in_schema: DictSchema,
        out_schema: DictSchema,
        description: str,
        name: str | None = None,
        params_schema: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the action with a name."""
        super().__init__(description, name, params_schema)
        self.use_fragments_for_context()
        self.in_schema = in_schema
        self.out_schema = out_schema

    async def update_frag_schemas(self, available_fragments: list[type[FragmentKind]]) -> None:
        """Update the input and output fragment schemas based on available fragments."""
        self.in_frag_schema = await self.create_in_schema(self.in_schema, available_fragments)
        self.out_frag_schema = await self.create_out_schema(self.out_schema, available_fragments)

    async def arrange(
        self,
        fragments: list[Fragment],
        in_frag_schema: DictSchema,
    ) -> tuple[list[Fragment], list[Fragment]]:
        """Take all incoming fragments and chooses which to use for inputs and which for context."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    async def prep(self, fragments: list[Fragment], in_schema: DictSchema) -> ActionParams:
        """Create action parameters from fragments."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    async def out(self, result: ActionResult, out_frag_schema: DictSchema) -> list[Fragment]:
        """Create fragments from action result."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    async def create_out_schema(
        self,
        out_schema: DictSchema,
        available_fragments: list[type[FragmentKind]],
    ) -> DictSchema:
        """Create output schema based on available fragments."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    async def create_in_schema(
        self,
        in_schema: DictSchema,
        available_fragments: list[type[FragmentKind]],
    ) -> DictSchema:
        """Create input schema based on available fragments."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Wrap the _do method to perform the action. Ignores params arg."""
        fragments = context.fragments

        if self.in_frag_schema is None:
            self.in_frag_schema = await self.create_in_schema(self.in_schema, context.available_fragment_kinds)

        arranged_fragments, context_fragments = await self.arrange(fragments, self.in_frag_schema)

        prep_params = await self.prep(arranged_fragments, self.in_schema)

        # verify schema
        if not self.in_schema.dict_satisfies_schema(prep_params.to_dict()):
            msg = f"Prepared params do not satisfy input schema for action {self.name}."
            raise ValueError(msg)

        result = await self._do(prep_params, context)

        # verify output schema
        if not self.out_schema.dict_satisfies_schema(result.results):
            msg = f"Action result does not satisfy output schema for action {self.name}."
            raise ValueError(msg)

        if self.out_frag_schema is None:
            self.out_frag_schema = await self.create_out_schema(self.out_schema, context.available_fragment_kinds)

        out_fragments = await self.out(result, self.out_frag_schema)

        res = ActionResult()
        for fragment in out_fragments:
            res.add_fragment(fragment)
        return res

from core.capabiliity_manager import AgentCapabilities
from core.query import Query, QueryResponse
from core.entity import Entity
from core.model import UnderlyingModel


class Agent(Entity):
    """A class representing an agent with various capabilities."""

    def __init__(
        self,
        name: str,
        description: str,
        role: str,
        capabilities: AgentCapabilities,
        underlying_model: UnderlyingModel,
    ):
        super().__init__(name, description, role)

        # capabilities
        self.capabilties = capabilities

        # underlying model
        self.underlying_model = underlying_model

    def handle_query(self, query: Query) -> QueryResponse:
        """Handle a query by executing it and returning the result."""

        # build prompt from the query
        original_query = query.content

        # relevant memories
        relevant_memories = self.capabilties.memory.load_memories_relevant_to_query(
            query.content
        )

        # TODO inject into system prompt rather than user prompt

        memory_str = "Memories:\n" + "\n".join(
            [f" - {memory}" for memory in relevant_memories]
        )

        # relevant knowledge
        relevant_knowledge = self.capabilties.knowledge_base.retrieve_related_knowledge(
            query.content
        )

        # relevant tool outputs
        relevant_tool_outputs = (
            self.capabilties.tools_manager.get_tool_responses_for_query(query.content)
        )

        new_query = Query(
            query.sender,
            query.recipient,
            query.content,
            relevant_memories,
            relevant_knowledge,
            relevant_tool_outputs,
        )

        knowledge_str = "\n\nKnowledge:\n" + "\n".join(
            [f" - {knowledge.knowledge}" for knowledge in relevant_knowledge]
        )

        # if no knowledge or memory don't add them to the prompt

        prompt = ""
        if len(relevant_memories) > 0:
            prompt += memory_str
        if len(relevant_knowledge) > 0:
            prompt += knowledge_str

        # add the query to the prompt
        if len(relevant_memories) > 0 or len(relevant_knowledge) > 0:
            prompt += "\n\nAnswer the following query:\n\n"

        # prompt inject
        prompt += original_query

        new_query = Query(query.sender, query.recipient, prompt)

        # check if the query needs planning
        result = ""
        if self.capabilties.planning.query_needs_planning(new_query.content):
            # create a plan
            plan = self.capabilties.planning.create_plan(new_query.content)

            # build an executor for the plan
            executor = self.capabilties.planning.build_executor(new_query.content, plan)

            # execute the plan
            result = executor.answer_query(new_query)
        else:
            result = self.capabilties.query_executor.answer_query(new_query)

        return QueryResponse(self, result)

    def get_capabilities(self) -> AgentCapabilities:
        """Get the capabilities of the agent."""
        return self.capabilties

    def is_assistant_agent(self) -> bool:
        """Check if the agent is an assistant agent."""
        # TODO make this more robust, e.g. by checking the role or capabilities
        return self.name == "Assistant"

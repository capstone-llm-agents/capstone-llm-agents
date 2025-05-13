from autogen import ConversableAgent
from core.query import Query
from core.model import UnderlyingModel


class AG2Model(UnderlyingModel):
    """A class representing the AG2 model."""

    def __init__(self, ag2_agent: ConversableAgent):
        super().__init__()
        self.ag2_agent = ag2_agent

    def who_asked(self, query: Query) -> ConversableAgent:
        """Get the sender of the query."""
        entity = query.sender

        return ConversableAgent(
            name=entity.name,
            description=entity.description,
        )

    def generate(self, query: Query):
        """Generate a response from the AG2 model."""

        sender_agent = self.who_asked(query)

        relevant_memories = query.memories
        relevant_knowledge = query.knowledge

        context_sections = []

        if relevant_memories:
            memory_str = "\n".join(
                [f"- {memory.content}" for memory in relevant_memories]
            )
            context_sections.append(f"Memories:\n{memory_str}")

        if relevant_knowledge:
            knowledge_str = "\n".join(
                [f"- {knowledge.knowledge}" for knowledge in relevant_knowledge]
            )
            context_sections.append(f"Knowledge:\n{knowledge_str}")

        prompt_parts = []

        if context_sections:
            prompt_parts.append("The following background context may be helpful:\n")
            prompt_parts.append("\n\n".join(context_sections))
            prompt_parts.append("\n\nNow answer the following query:\n")

        prompt_parts.append(query.content)
        full_prompt = "\n".join(prompt_parts)

        response = sender_agent.initiate_chat(
            recipient=self.ag2_agent,
            message={"role": "user", "content": full_prompt},
            max_turns=1,
        )

        return response.summary

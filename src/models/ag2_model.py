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

        past_messages = []

        if relevant_memories:
            # roles are: "system", "user", "assistant"

            # convert memory e.g. "user: I need help with my homework"
            # and "agent: I can help you with that"
            # to { "role": "user", "content": "I need help with my homework" }
            # and { "role": "assistant", "content": "I can help you with that" }

            for memory in relevant_memories:
                content = memory.content
                output = content.split(":", 1)
                role = output[0].strip() if len(output) > 0 else "user"
                message_content = output[1].strip() if len(output) > 1 else content

                role = role.strip().lower()

                role = "user" if role == "user" else "assistant"

                past_messages.append({"role": role, "content": message_content})

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

        past_messages.append({"role": "user", "content": full_prompt})

        response = self.ag2_agent.generate_reply(
            messages=past_messages,
            sender=sender_agent,
        )

        if response is None:
            return ""

        return response["content"]

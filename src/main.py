from autogen import ConversableAgent
from app import App
from core.capability import Capability
from implementations.faiss_kb import FAISSKnowledgeBase


default_capabilities: list[Capability] = []
app = App(default_capabilities)

# Capabilities
# ============

# add kb
default_capabilities.append(FAISSKnowledgeBase(["pdf", "txt"], 1000, 3))

# Agents
# ======

# add agent
app.add_ag2_agent(
    ConversableAgent(
        name="Assistant",
        system_message="You are a helpful assistant.",
        llm_config={"api_type": "ollama", "model": "gemma3"},
    ),
    default_capabilities,
)

app.run()

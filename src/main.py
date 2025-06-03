from autogen import ConversableAgent
from app import App
from core.capability import Capability
from implementations.faiss_kb import FAISSKnowledgeBase
from user_interface.cli import CLI
from user_interface.gui import GUI


default_capabilities: list[Capability] = []


interface = CLI()
# interface = GUI()


app = App(interface, default_capabilities)

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
        llm_config=app.config.get_llm_config(),
    ),
)


app.run()

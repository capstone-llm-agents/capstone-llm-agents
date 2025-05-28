# NOTE: For now just do what you need to make it work but I will fix it later
from autogen import ConversableAgent
from app import App
from core.agent import Agent
from core.api import MASAPI
from core.capabiliity_manager import AgentCapabilities
from core.capabiliity_proxy import CapabilityProxy
from core.capability import Capability
from core.entity import HumanUser
from core.mas import MAS
from implementations.memory import Memory
from implementations.faiss_kb import FAISSKnowledgeBase
from models.ag2_model import AG2Model
from spoof.spoofed_capabilities import SpoofedCapabilities
from spoof.spoofed_comm_protocol import CommunicationProtocolSpoof
from user_interface.inteface import UserInterface
import os

from autogen import ConversableAgent
from app import App
from core.capability import Capability
from implementations.faiss_kb import FAISSKnowledgeBase
from openai import OpenAI

os.environ['OPENAI_API_KEY'] = "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"
default_capabilities: list[Capability] = []
app = App(default_capabilities)

# Capabilities
# ============

# add kb
default_capabilities.append(FAISSKnowledgeBase(["pdf", "txt"], 1000, 3))
default_capabilities.append(Memory())

# Agents
# ======

# add agent
app.add_ag2_agent(
    ConversableAgent(
        name="Assistant",
        system_message="You are a helpful assistant.",
        llm_config={
            "api_type": "openai",
            "api_key": os.getenv("OPENAI_API_KEY"), 
            "model": "gpt-4o"},
        ),
    default_capabilities,
)

app.run()
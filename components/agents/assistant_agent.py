"""The assistant agent module defines the main assistant that talks to the user and handles their requests."""

from components.agents.base_agent import create_base_agent

ASSISTANT_AGENT = create_base_agent(
    name="Assistant Agent",
    description="An intelligent assistant that helps users with a variety of tasks by leveraging tools and actions.",
)

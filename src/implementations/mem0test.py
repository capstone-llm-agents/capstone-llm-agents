import os
from openai import OpenAI
from mem0 import Memory, MemoryClient
from dotenv import load_dotenv

load_dotenv()

os.getenv("OPENAI_API_KEY")
client = OpenAI()


class PersonalAITutor:
    def __init__(self):
        """
        Initialize the PersonalAITutor with memory configuration and OpenAI client.
        """
        self.memory = MemoryClient(os.getenv("MEM0_API_KEY")) # utilise mem0 cloud service
        self.client = client
        self.app_id = "app-1"

    def ask(self, question, user_id=None):
        """
        Ask a question to the AI and store the relevant facts in memory

        :param question: The question to ask the AI.
        :param user_id: Optional user ID to associate with the memory.
        """
        # Start a streaming response request to the AI
        response = self.client.responses.create(
            model="gpt-4o",
            instructions="You are a personal AI Tutor.",
            input=question,
            stream=True
        )

        # Store the question in memory
        self.memory.add(question, user_id=user_id, metadata={"app_id": self.app_id})

        # Print the response from the AI in real-time
        for event in response:
            if event.type == "response.output_text.delta":
                print(event.delta, end="")

    def get_memories(self, user_id=None):
        """
        Retrieve all memories associated with the given user ID.

        :param user_id: Optional user ID to filter memories.
        :return: List of memories.
        """
        return self.memory.get_all(user_id=user_id)

# Instantiate the PersonalAITutor
ai_tutor = PersonalAITutor()

# Define a user ID
user_id = "john_doe"

# Ask a question
ai_tutor.ask("I am learning introduction to CS. What is queue? Briefly explain.", user_id=user_id)

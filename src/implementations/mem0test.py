import os
from openai import OpenAI
from mem0 import Memory, MemoryClient

os.environ['OPENAI_API_KEY'] = "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"
MEM0_API_KEY = "m0-xX74vpX3bEKH0BfJZjBVffA7AWXU7D7EaL00rjOf"
client = OpenAI()


class PersonalAITutor:
    def __init__(self):
        """
        Initialize the PersonalAITutor with memory configuration and OpenAI client.
        """
        self.memory = MemoryClient(MEM0_API_KEY) # utilise mem0 cloud service
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

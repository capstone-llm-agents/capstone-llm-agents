from capabilities.knowledge_base import Document

import os

from user_interface.user_interface import UserInterface


class CLI(UserInterface):
    """A simple CLI interface for interacting with MASAPI."""

    def run(self):
        """Run the CLI interface."""

        # self.clear_screen()

        print("Welcome to the MAS CLI!")
        while True:

            print("\nMenu:")
            print("1. List Agents")
            print("2. Query MAS")
            print("3. View Chat History")
            print("4. Add Document to Agent")
            print("5. List Documents")
            print("6. Exit\n")
            choice = input("Enter your choice: ").strip()

            self.clear_screen()

            if choice == "1":
                self.list_agents()
            elif choice == "2":
                self.query_mas()
            elif choice == "3":
                self.view_chat_history()
            elif choice == "4":
                self.add_document()
            elif choice == "5":
                self.list_documents()
            elif choice == "6":
                self.exit()
                break
            else:
                print("Invalid choice. Try again.")

    def list_agents(self):
        """List all agents in the MAS."""
        agents = self.api.mas_api.get_agents()
        if agents:
            print("Agents:")
            for agent in agents:
                print(f"- {agent.name}")
        else:
            print("No agents found.")

    def query_mas(self):
        """Query the MAS with a prompt."""
        query = input("Enter your query: ")
        response = self.api.mas_api.query_mas(query)
        print("Response:")
        print(response)

    def view_chat_history(self):
        """View the chat history."""
        history = self.api.mas_api.get_chat_history()

        # length check
        if len(history.messages) == 0:
            print("No chat history available.")
            return

        print("Chat History:")
        for entry in history.messages:
            print(f" - {entry.who}: {entry.content}")

    def add_document(self):
        """Add a document to an agent."""
        agent_name = input("Enter agent name: ")
        try:
            agent = self.api.mas_api.get_agent(agent_name)
        except KeyError:
            print(f"No agent found with name: {agent_name}")
            return
        path = input("Enter document path: ")

        extension = path.split(".")[-1]

        document = Document(path=path, extension=extension)

        self.api.mas_api.add_document(document, agent)
        print("Document added successfully.")

    def list_documents(self):
        """List all documents in the MAS."""
        docs = self.api.mas_api.get_documents()
        if docs:
            print("Documents:")
            for doc in docs:
                print(f"- {doc.path}")
        else:
            print("No documents available.")

    def clear_screen(self):
        """Clear the console screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def exit(self):
        """Exit the CLI interface."""
        super().exit()
        print("Exiting the MAS CLI. Goodbye!")

"""Main entry point for the capstone-llm-agents project."""

from llm_mas.client.ui.textual_app.app import TextualApp


def main() -> None:
    """Run the main application logic."""
    app = TextualApp()
    app.run()


if __name__ == "__main__":
    main()

"""Main entry point for the PyQt6 LLM MAS application."""

from llm_mas.client.ui.pyqt.app import run_app
from llm_mas.mas.checkpointer import CheckPointer


def main():
    """Main entry point - show login screen."""
    # Always show login screen
    checkpoint = CheckPointer("./db/checkpoint.sqlite3")
    run_app(None, checkpoint)


if __name__ == "__main__":
    main()

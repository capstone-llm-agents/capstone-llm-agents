"""Main entry point for the PyQt6 LLM MAS application."""

import argparse
import sys

from llm_mas.client.ui.pyqt.app import run_app
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.checkpointer import CheckPointer
from llm_mas.utils.server_manager import ServerManager
from pathlib import Path

def main() -> None:
    """Start servers and launch application."""
    parser = argparse.ArgumentParser(description="Run the LLM MAS application")
    parser.add_argument(
        "--no-servers",
        action="store_true",
        help="Skip automatic server startup (use if servers are already running)",
    )
    args = parser.parse_args()

    if not args.no_servers:
        APP_LOGGER.info("Starting servers automatically...")
        server_manager = ServerManager()
        if not server_manager.start_all():
            APP_LOGGER.error("Failed to start servers. Exiting.")
            sys.exit(1)
    else:
        APP_LOGGER.info("Skipping automatic server startup (--no-servers flag set)")
    checkpointing_path = Path(__file__).parent.joinpath("db").joinpath("checkpoint.sqlite3")
    checkpoint = CheckPointer(str(checkpointing_path))
    run_app(None, checkpoint)


if __name__ == "__main__":
    main()

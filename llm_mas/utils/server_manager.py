"""Server manager for starting and stopping MCP and network servers."""

import atexit
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from types import FrameType

from llm_mas.logging.loggers import APP_LOGGER


class ServerManager:
    """Manages lifecycle of MCP and network server subprocesses."""

    def __init__(self) -> None:
        """Initialize server manager with server configurations."""
        self.processes: list[subprocess.Popen] = []
        self.servers = [
            {"name": "Weather MCP", "cmd": ["python", "mcp_server/weather_server.py"], "port": 8080},
            {"name": "Calendar MCP", "cmd": ["python", "mcp_server/calendar_server.py"], "port": 8081},
            {"name": "PDF MCP", "cmd": ["python", "mcp_server/pdf_server.py"], "port": 8082},
            {"name": "Network Server", "cmd": ["python", "-m", "network_server.run_network"], "port": 8000},
        ]

    def _is_port_open(self, port: int, timeout: float = 0.5) -> bool:
        try:
            with socket.create_connection(("localhost", port), timeout=timeout):
                return True
        except (ConnectionRefusedError, TimeoutError, OSError):
            return False

    def _wait_for_port(self, port: int, server_name: str, max_wait: float = 10.0) -> bool:
        APP_LOGGER.info(f"Waiting for {server_name} on port {port}...")
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self._is_port_open(port):
                APP_LOGGER.info(f"{server_name} is ready on port {port}")
                return True
            time.sleep(0.3)
        return False

    def start_all(self) -> bool:
        """Start all servers and wait for health checks."""
        APP_LOGGER.info("Starting all servers...")

        project_root = Path(__file__).parent.parent.parent

        for server in self.servers:
            APP_LOGGER.info(f"Starting {server['name']}...")
            try:
                process = subprocess.Popen(  # noqa: S603
                    server["cmd"],
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                self.processes.append(process)

                if not self._wait_for_port(server["port"], server["name"]):
                    APP_LOGGER.error(f"Failed to start {server['name']} on port {server['port']}")
                    self.shutdown_all()
                    return False

            except (OSError, subprocess.SubprocessError) as e:
                APP_LOGGER.error(f"Error starting {server['name']}: {e}")
                self.shutdown_all()
                return False

        APP_LOGGER.info("All servers started successfully!")
        atexit.register(self.shutdown_all)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        return True

    def shutdown_all(self) -> None:
        """Terminate all running server subprocesses."""
        APP_LOGGER.info("Shutting down all servers...")
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        self.processes.clear()
        APP_LOGGER.info("All servers shut down.")

    def _signal_handler(self, signum: int, _frame: FrameType | None) -> None:
        APP_LOGGER.info(f"Received signal {signum}, shutting down...")
        self.shutdown_all()
        sys.exit(0)

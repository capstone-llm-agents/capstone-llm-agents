from datetime import datetime

from core.capability import Capability


class LogItem:
    """Class to represent a log item."""

    def __init__(self, content: str, timestamp: str):
        self.content = content
        self.timestamp = timestamp


class Logger:
    """Class to log the performance of the system."""

    logs: list[LogItem]

    def __init__(self):
        self.logs = []

    def log(self, content: str):
        """Log the content with a timestamp."""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_item = LogItem(content, timestamp)
        self.logs.append(log_item)


class Monitoring(Capability):
    """Class to monitor the performance of the system."""

    # TODO: supported by Sprint 3
    def __init__(self):
        super().__init__("monitoring")
        self.logger = Logger()

    def log(self, content: str):
        """Log the content with a timestamp."""
        self.logger.log(content)

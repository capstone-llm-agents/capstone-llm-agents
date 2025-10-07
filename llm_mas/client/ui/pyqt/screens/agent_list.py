# agent_list_screen.py (PyQt6 version)
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QListWidget, QListWidgetItem
from llm_mas.client.account.client import Client
from llm_mas.mas.agent import Agent

class AgentListScreen(QWidget):
    """Screen to list all agents in the MAS (PyQt6)."""

    def __init__(self, client: Client, nav: QWidget):
        super().__init__()
        self.client = client
        self.nav = nav

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Top bar with back button
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(lambda: self.nav.navigate.emit("main_menu", None))
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        header = QLabel("Agents List")
        layout.addWidget(header)

        self.agent_list = QListWidget()
        layout.addWidget(self.agent_list)

        self._populate_agents()

    def _populate_agents(self):
        mas = self.client.get_mas()
        for agent in mas.agents:
            item = QListWidgetItem(agent.name)
            self.agent_list.addItem(item)

    def _go_back(self):
        self.nav.setCentralWidget(self.nav.main_menu)

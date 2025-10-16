import math
from typing import Dict

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from llm_mas.client.account.client import Client
from llm_mas.client.ui.pyqt.screens.agent_network_graphics import Rectangle, draw_line
from llm_mas.mas.agent import Agent

# hardcoded distance between nodes idk make this auto later
AGENT_ORBIT_RADIUS = 200
ACTION_ORBIT_RADIUS = 120


class AgentNetworkScreen(QWidget):
    def __init__(self, client: Client, nav):
        super().__init__()
        self.client = client
        self.nav = nav
        self.agent_nodes: Dict[Agent, Rectangle] = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(lambda: self.nav.navigate.emit("main_menu", None))
        top_bar.addWidget(back_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)
        top_bar.addWidget(refresh_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("white")))  # white for visibility, delegate to the qss later

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints() | QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.view)

        self._populate_network()

    def _refresh(self):
        # i was hoping this could be a refresh/reset thing as you connected up more nodes
        # but just runs the main command again for the moment
        self.scene.clear()
        self.agent_nodes.clear()
        self._populate_network()

    def _populate_network(self):
        agents = self.client.mas.agents  # yoink agents
        if not agents:
            return

        # for centering the layout
        center = QPointF(400, 300)
        num_agents = len(agents)

        # draw agents
        for i, agent in enumerate(agents):
            # agents are placed in orbit/circularly (?) around
            angle = 2 * math.pi * i / num_agents
            x = center.x() + AGENT_ORBIT_RADIUS * math.cos(angle)
            y = center.y() + AGENT_ORBIT_RADIUS * math.sin(angle)
            node = Rectangle(agent.name, "#dedede")
            node.setPos(QPointF(x, y))
            self.scene.addItem(node)
            self.agent_nodes[agent] = node

        # get agent friendships
        for agent in agents:
            for friend in getattr(agent, "friends", []):
                if friend in self.agent_nodes:
                    draw_line(self.scene, self.agent_nodes[agent], self.agent_nodes[friend], width=2)

        #  get actions
        for agent in agents:
            if hasattr(agent, "narrower") and agent.narrower:
                # yoink actions
                actions = agent.action_space.actions
                if not actions:
                    continue
                agent_node = self.agent_nodes[agent]
                count = len(actions)
                for j, action in enumerate(actions):
                    if count == 1:
                        angle = -math.pi / 2
                    else:
                        angle = 2 * math.pi * j / count
                    ax = agent_node.x() + ACTION_ORBIT_RADIUS * math.cos(angle)
                    ay = agent_node.y() + ACTION_ORBIT_RADIUS * math.sin(angle)
                    action_node = Rectangle(action.__class__.__name__, "#969696")
                    action_node.setPos(QPointF(ax, ay))
                    self.scene.addItem(action_node)
                    draw_line(self.scene, agent_node, action_node, color=Qt.GlobalColor.darkGray)

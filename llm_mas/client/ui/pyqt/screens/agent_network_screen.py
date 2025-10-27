"""Agent Network visualization screen for displaying agents and their connections."""

import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QWheelEvent
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from llm_mas.client.account.client import Client
from llm_mas.client.ui.pyqt.screens.agent_network_graphics import Rectangle, draw_line
from llm_mas.mas.agent import Agent


class ZoomableGraphicsView(QGraphicsView):
    """Custom QGraphicsView with mouse wheel zoom support."""

    def __init__(self, scene: QGraphicsScene) -> None:
        """Initialize the zoomable graphics view.

        Args:
            scene: The QGraphicsScene to display

        """
        super().__init__(scene)
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel for zooming.

        Args:
            event: The wheel event

        """
        # Get the mouse position before scaling
        old_pos = self.mapToScene(event.position().toPoint())

        # Calculate zoom factor
        zoom_in = event.angleDelta().y() > 0
        factor = 1.2 if zoom_in else 0.8

        # Check zoom limits
        new_zoom = self.zoom_factor * factor
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return

        # Apply zoom
        self.scale(factor, factor)
        self.zoom_factor = new_zoom

        # Get the new mouse position after scaling
        new_pos = self.mapToScene(event.position().toPoint())

        # Move scene to keep mouse position constant
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())


class AgentNetworkScreen(QWidget):
    """Screen for visualizing agent networks and their connections."""

    def __init__(self, client: Client, nav) -> None:
        """Initialize the agent network screen.

        Args:
            client: The client instance
            nav: The navigation manager

        """
        super().__init__()
        self.client = client
        self.nav = nav
        self.agent_nodes: dict[Agent, Rectangle] = {}
        self.scene = None
        self.view = None
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(lambda: self.nav.navigate.emit("main_menu", None))
        top_bar.addWidget(back_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh)
        top_bar.addWidget(refresh_btn)

        # Zoom control buttons
        zoom_in_btn = QPushButton("🔍+ Zoom In")
        zoom_in_btn.clicked.connect(self._zoom_in)
        top_bar.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("🔍- Zoom Out")
        zoom_out_btn.clicked.connect(self._zoom_out)
        top_bar.addWidget(zoom_out_btn)

        reset_view_btn = QPushButton("⟲ Reset View")
        reset_view_btn.clicked.connect(self._reset_view)
        top_bar.addWidget(reset_view_btn)

        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#1e1e1e")))  # Dark theme background

        self.view = ZoomableGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints() | QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)  # Enable panning
        layout.addWidget(self.view)

        self._populate_network()

    def _zoom_in(self) -> None:
        """Zoom in the view."""
        self.view.scale(1.2, 1.2)
        self.view.zoom_factor *= 1.2

    def _zoom_out(self) -> None:
        """Zoom out the view."""
        self.view.scale(0.8, 0.8)
        self.view.zoom_factor *= 0.8

    def _reset_view(self) -> None:
        """Reset the view to fit all content."""
        self.view.resetTransform()
        self.view.zoom_factor = 1.0
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _refresh(self) -> None:
        """Refresh the network visualization."""
        # i was hoping this could be a refresh/reset thing as you connected up more nodes
        # but just runs the main command again for the moment
        self.scene.clear()
        self.agent_nodes.clear()
        self._populate_network()
        self._reset_view()

    def _populate_network(self) -> None:
        """Populate the network with agents and their connections."""
        agents = self.client.mas.agents  # yoink agents
        if not agents:
            return

        num_agents = len(agents)

        # Dynamic layout based on number of agents and screen size
        view_rect = self.view.viewport().rect()
        view_width = max(view_rect.width(), 800)
        view_height = max(view_rect.height(), 600)

        # Center based on viewport size
        center = QPointF(view_width / 2, view_height / 2)

        # Dynamic orbit radius based on number of agents
        agent_orbit_radius = 150 + (num_agents * 25)
        action_orbit_radius = max(100, agent_orbit_radius * 0.5)

        # draw agents
        for i, agent in enumerate(agents):
            # agents are placed in orbit/circularly (?) around
            angle = 2 * math.pi * i / num_agents
            x = center.x() + agent_orbit_radius * math.cos(angle)
            y = center.y() + agent_orbit_radius * math.sin(angle)
            node = Rectangle(agent.name, "#4a4a7a")  # Purple-ish for agents
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
                    angle = -math.pi / 2 if count == 1 else 2 * math.pi * j / count
                    ax = agent_node.x() + action_orbit_radius * math.cos(angle)
                    ay = agent_node.y() + action_orbit_radius * math.sin(angle)
                    action_node = Rectangle(action.__class__.__name__, "#5a5a5a")  # Darker gray for actions
                    action_node.setPos(QPointF(ax, ay))
                    self.scene.addItem(action_node)
                    draw_line(self.scene, agent_node, action_node, color=Qt.GlobalColor.darkGray)

        # Fit the view to show all content
        if self.agent_nodes:
            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

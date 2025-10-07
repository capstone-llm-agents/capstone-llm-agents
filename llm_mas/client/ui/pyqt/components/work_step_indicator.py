"""Work step indicator widget for PyQt6."""

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from llm_mas.agent.work_step import WorkStep

class WorkStepIndicator(QWidget):
    """Compact work step indicator."""

    def __init__(self, work_step: WorkStep):
        super().__init__()
        self.work_step = work_step
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.status_label = QLabel("⏳" if not work_step.complete else "✓")
        self.status_label.setMaximumWidth(40)
        self.name_label = QLabel(work_step.name)

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.name_label)

    def mark_complete(self):
        self.work_step.mark_complete()
        self.status_label.setText("✓")
        self.status_label.setStyleSheet("color: green;")

    def mark_grey(self):
        self.status_label.setStyleSheet("color: grey;")
        self.name_label.setStyleSheet("color: grey;")

    def mark_current_green(self):
        self.status_label.setStyleSheet("color: green;")
        self.name_label.setStyleSheet("color: black;")

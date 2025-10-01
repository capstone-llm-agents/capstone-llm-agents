"""A work step indicator component for the textual app."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from llm_mas.agent.work_step import WorkStep


class WorkStepIndicator(Static):
    """A compact work step indicator that can be embedded in messages."""

    def __init__(self, work_step: WorkStep) -> None:
        """Initialize the work step indicator with a work step."""
        super().__init__(classes="work-step-indicator")
        self.work_step = work_step

    def compose(self) -> ComposeResult:
        """Compose the compact work step indicator."""
        with Horizontal(classes="work-step-row"):
            # Status indicator (tick or hourglass)
            if self.work_step.complete:
                self.status_widget = Static("✓", classes="step-complete")
            else:
                self.status_widget = Static("⏳", classes="step-in-progress")
            yield self.status_widget

            # Work step name
            self.text_widget = Static(self.work_step.name, classes="step-text")
            yield self.text_widget

    async def mark_complete(self, time_taken: float | None = None) -> None:
        """Mark the work step as complete and update the UI."""
        self.work_step.mark_complete()

        if self.status_widget:
            self.status_widget.update("✓")
            self.status_widget.remove_class("step-in-progress")
            self.status_widget.add_class("step-complete")

        # update the actual text
        if self.text_widget:
            if time_taken is not None:
                self.text_widget.update(f"{self.work_step.name} ({time_taken:.2f}s)")
            else:
                self.text_widget.update(self.work_step.name)
            self.text_widget.remove_class("step-text")
            self.text_widget.add_class("step-text-complete")

    def mark_grey(self) -> None:
        """Mark the work step as grey (completed but not current focus)."""
        if self.status_widget and self.text_widget:
            self.status_widget.remove_class("step-complete")
            self.status_widget.add_class("step-complete-grey")
            self.text_widget.remove_class("step-text")
            self.text_widget.add_class("step-text-grey")

    def mark_current_green(self) -> None:
        """Mark the work step as current active green."""
        if self.status_widget and self.text_widget:
            self.status_widget.remove_class("step-complete-grey")
            self.status_widget.add_class("step-complete")
            self.text_widget.remove_class("step-text-grey")
            self.text_widget.add_class("step-text")

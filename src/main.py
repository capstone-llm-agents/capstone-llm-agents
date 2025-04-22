"""Entry point of the program."""

from app import App
from mas.examples.task_testing import test_task


def main():
    """Entry point of the program."""
    app = App()
    app.run()

    test_task(app)


if __name__ == "__main__":
    main()

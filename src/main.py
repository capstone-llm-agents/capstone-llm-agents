"""Entry point of the program."""

from app import App
from mas.examples.mas_testing import test_basic_mas


def main():
    """Entry point of the program."""
    app = App()
    app.run()

    test_basic_mas(app)


if __name__ == "__main__":
    main()

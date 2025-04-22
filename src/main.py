"""Entry point of the program."""

from app import App
from mas.examples.yaml_test import test_yaml_to_pydantic


def main():
    """Entry point of the program."""
    app = App()
    app.run()

    # test_task(app)
    test_yaml_to_pydantic(app)


if __name__ == "__main__":
    main()

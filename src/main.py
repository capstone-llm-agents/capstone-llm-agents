"""Entry point of the program."""

from app import App
#from mas.examples.mas_testing import test_basic_mas
from mas.examples.recipe_testing import test_recipe_mas

def main():
    """Entry point of the program."""
    app = App()
    app.run()

    test_recipe_mas(app)


if __name__ == "__main__":
    main()

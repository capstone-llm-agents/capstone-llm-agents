"""Module to run a simple model using Autogen2 to complete a basic task of writing a sentence about a topic."""

from pydantic import BaseModel
from typing import List, Optional
from mas.base_resource import BaseResource
from mas.task import Task


class UserRequestResource(BaseResource):
    class UserRequestModel(BaseModel):
        '''user specifications'''
        ingredients: Optional[List[str]] # its own data struc?? or is that separate
        dietary_requirement: Optional[List[str]]
        cooking_time: Optional[int] #mins
        flavour_profile: Optional[str]

        def __init__(self, *, ingredients: Optional[List[str]] = None, dietary_requirement: Optional[List[str]] = None, cooking_time: Optional[int] = None, flavour_profile: Optional[str] = None,):
            super().__init__(ingredients=ingredients, dietary_requirement=dietary_requirement, cooking_time=cooking_time, flavour_profile=flavour_profile)
            self.ingredients = ingredients
            self.dietary_requirement = dietary_requirement
            self.cooking_time = cooking_time
            self.flavour_profile = flavour_profile

    def __init__(self, request: UserRequestModel):
        super().__init__(request)
        self.request = request

    @staticmethod
    def get_model_type() -> type[UserRequestModel]:
        return UserRequestResource.UserRequestModel

class RecipeResource(UserRequestResource):
    class RecipeModel(BaseModel):
        recipe_name: str
        def __init__(self, *, recipe_name: str):
            super().__init__(recipe_name=recipe_name)
            self.recipe_name = recipe_name

    def __init__(self, recipe: RecipeModel):
        super().__init__(recipe)
        self.recipe_name = recipe_name

    @staticmethod
    def get_model_type() -> type[RecipeModel]:
        return RecipeResource.RecipeModel


class FindRecipeTask(Task[UserRequestResource, RecipeResource]):
    def _do_work(self, input_resource: UserRequestResource) -> RecipeResource:
        request = input_resource.request

        recipe_name = f""

        '''append optional attributes'''
        if request.flavour_profile:
            recipe_name += f"{request.flavour_profile} "

        if request.dietary_requirement:
            recipe_name += f"{request.dietary_requirement} "

        if request.ingredients:
            ingredients_list = ", ".join(request.ingredients)
            recipe_name += f"with {ingredients_list} "

        if request.cooking_time:
            recipe_name += f"({request.cooking_time} minutes)"

        # concenate
        return RecipeResource(RecipeResource.RecipeModel(recipe_name=recipe_name))

    def __init__(self):
        super().__init__(
            "FindRecipeTask",
            "A task that generates a recipe name based on preferences from a user request.",
            UserRequestResource.UserRequestModel,
            RecipeResource.RecipeModel,
            self._do_work,
        )
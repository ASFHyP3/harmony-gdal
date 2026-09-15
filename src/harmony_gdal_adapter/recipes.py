from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from recipe_types import Recipe


@dataclass
class RecipeInputOptions:
    """Input options used by recipes."""

    collection_shortname: str
    input_filename: Path
    target_srs: str | None
    spatial_extents: str | None
    output_type: str
    output_filename: str


def build_recipe(options: RecipeInputOptions) -> Recipe:
    """Builds a Recipe for execution from the nisar.k recipe file with the given recipe input options.

    Args:
        options (RecipeInputOptions): the input options for the recipe file

    Returns:
        Recipe: The built recipe from the input options
    """
    raise NotImplementedError()

from argparse_dataclass import ArgumentParser

from harmony_gdal_adapter.gdal import execute_recipe
from harmony_gdal_adapter.recipes import RecipeInputOptions, build_recipe


def run_cli() -> None:

    parser = ArgumentParser(RecipeInputOptions)
    options = parser.parse_args()

    recipe = build_recipe(options)
    execute_recipe(recipe)


if __name__ == '__main__':
    run_cli()

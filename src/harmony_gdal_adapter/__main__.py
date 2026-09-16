from argparse_dataclass import ArgumentParser
from gdal import execute_recipe
from recipes import RecipeInputOptions, build_recipe


def run_cli() -> None:

    parser = ArgumentParser(RecipeInputOptions)
    options = parser.parse_args()

    recipe = build_recipe(options)
    execute_recipe(recipe)


if __name__ == '__main__':
    run_cli()

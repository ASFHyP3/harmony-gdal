from dataclasses import dataclass
from argparse_dataclass import ArgumentParser
import argparse
from recipes import build_recipe,RecipeInputOptions
from gdal import execute_recipe

def run_cli():     

    parser = ArgumentParser(RecipeInputOptions)
    options = parser.parse_args()

    recipe = build_recipe(options)
    execute_recipe(recipe)
    

if __name__ == '__main__':
    run_cli()

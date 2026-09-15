from dataclasses import dataclass, field
import argparse_dataclass
from argparse_dataclass import ArgumentParser
import argparse
from recipes import build_recipe,RecipeInputOptions
from gdal import execute_recipe
from typing import Literal

def run_cli():     

    parser = ArgumentParser(RecipeInputOptions)
    raise NotImplementedError()
    
    # recipe = build_recipe(parser.parse_args())
    # execute_recipe(recipe)
    

if __name__ == '__main__':
    run_cli()

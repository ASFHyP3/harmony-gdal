from dataclasses import dataclass

from osgeo.gdal import WarpOptions


def execute_recipe(recipe: Recipe):
    raise NotImplementedError()


def execute_gdal_translate_recipe(recipe: GdalTranslateRecipe):
    translate_options = build_gdal_translate_options(recipe)
    raise NotImplementedError()


def execute_gdal_warp_recipe(recipe: GdalWarpRecipe):
    warp_options = build_gdal_translate_options(recipe)
    raise NotImplementedError()


def build_gdal_translate_options(recipe: GdalTranslateRecipe):
    raise NotImplementedError()


def build_gdal_warp_options(recipe: GdalWarpRecipe):
    raise NotImplementedError()


def build_input_string(input_options: GdalInputOptions) -> str:
    raise NotImplementedError()

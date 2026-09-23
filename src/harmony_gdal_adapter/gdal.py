from dataclasses import asdict

from osgeo.gdal import Translate, Warp

from harmony_gdal_adapter.build_recipes import (
    GdalOutputOptions,
    GdalTranslateRecipe,
    GdalWarpRecipe,
    Recipe,
)


def execute_recipe(recipe: Recipe) -> None:
    srcDS = build_input_string(recipe)
    destName = build_output_string(recipe)
    if isinstance(recipe.inner, GdalTranslateRecipe):
        execute_gdal_translate_recipe(srcDS, destName, recipe.inner)
    elif isinstance(recipe.inner, GdalWarpRecipe):
        execute_gdal_warp_recipe(srcDS, destName, recipe.inner)
    else:
        raise TypeError('recipe must be GdalTranslateRecipe or GdalWarpRecipe')


def execute_gdal_translate_recipe(srcDS: str, destName: str, recipe: GdalTranslateRecipe) -> None:
    translate_options = build_gdal_translate_options(recipe)
    Translate(destName, srcDS, **translate_options)


def execute_gdal_warp_recipe(srcDS: str, destName: str, recipe: GdalWarpRecipe) -> None:
    warp_options = build_gdal_warp_options(recipe)
    Warp(destName, srcDS, **warp_options)


def build_input_string(recipe: Recipe) -> str:
    input_options = recipe.inner.gdalOptions.inputOptions
    return f'{input_options.driver}:{input_options.virtualFilesystem or ""}{input_options.inputFilePath}:{input_options.datasetPath}'


def build_output_string(recipe: Recipe) -> str:
    output_options = recipe.inner.gdalOptions.outputOptions
    return str(output_options.outputFilePath)


def build_gdal_translate_options(recipe: GdalTranslateRecipe) -> dict:
    translate_options = build_gdal_output_options(recipe.gdalOptions.outputOptions)
    return translate_options


def build_gdal_warp_options(recipe: GdalWarpRecipe) -> dict:
    warp_options = build_gdal_output_options(recipe.gdalOptions.outputOptions)

    flattened_recipe_dictionary = {}

    for key, value in asdict(recipe.warpOptions).items():
        if isinstance(value, dict):
            for inner_key, inner_value in value.items():
                flattened_recipe_dictionary[f'{key}.{inner_key}'] = inner_value
        else:
            flattened_recipe_dictionary[key] = value

    recipe_gdal_mapping = {
        'targetSRS': 'dstSRS',
        'sourceSRS': 'srcSRS',
        'srcAlpha': 'srcAlpha',
        'dstAlpha': 'dstAlpha',
        'multithreaded': 'multithread',
        'copyMetadata': 'copyMetadata',
        'spatialSubset.outputBounds': 'outputBounds',
        'spatialSubset.output_boundsSRS': 'outputBoundsSRS',
        'spatialSubset.cutlineWKT': 'cutlineWKT',
        'spatialSubset.cutlineSRS': 'cutlineSRS',
        'spatialSubset.cutlineLayer': 'cutlineLayer',
        'spatialSubset.cutlineWhere': 'cutlineWhere',
        'spatialSubset.cutlineSQL': 'cutlineSQL',
        'spatialSubset.cutlineBlend': 'cutlineBlend',
        'spatialSubset.cropToCutline': 'cropToCutline',
    }

    for maps_from, maps_to in recipe_gdal_mapping.items():
        if maps_from in flattened_recipe_dictionary:
            warp_options[maps_to] = flattened_recipe_dictionary[maps_from]

    return warp_options


def build_gdal_output_options(output_options: GdalOutputOptions) -> dict:
    gdal_output_options = {}
    gdal_output_options['format'] = output_options.outputType
    return gdal_output_options

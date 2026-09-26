"""Execute GDAL recipes."""

from dataclasses import asdict
from itertools import chain

from osgeo.gdal import OpenEx, Translate, UseExceptions, Warp

from harmony_gdal_adapter.build_recipes import (
    GdalOutputOptions,
    GdalTranslateRecipe,
    GdalWarpRecipe,
    Recipe,
)
from harmony_gdal_adapter.exceptions import InvalidProjectionError, MissingVariableError


def execute_recipe(recipe: Recipe) -> None:
    """Executes a built Recipe as a GDAL operation.

    Args:
        recipe (Recipe): The Recipe representing a given GDAL translate or warp operation.

    Returns:
        None
    """
    UseExceptions()

    _validate_recipe_input(recipe)

    srcDS = _build_input_string(recipe)
    destName = _build_output_string(recipe)
    if isinstance(recipe.inner, GdalTranslateRecipe):
        _execute_gdal_translate_recipe(srcDS, destName, recipe.inner)
    elif isinstance(recipe.inner, GdalWarpRecipe):
        _execute_gdal_warp_recipe(srcDS, destName, recipe.inner)
    else:
        raise TypeError('recipe must be GdalTranslateRecipe or GdalWarpRecipe')


def _execute_gdal_translate_recipe(srcDS: str, destName: str, recipe: GdalTranslateRecipe) -> None:
    translate_options = _build_gdal_translate_options(recipe)
    Translate(destName, srcDS, **translate_options)


def _execute_gdal_warp_recipe(srcDS: str, destName: str, recipe: GdalWarpRecipe) -> None:
    warp_options = _build_gdal_warp_options(recipe)
    Warp(destName, srcDS, **warp_options)


def _build_input_string(recipe: Recipe) -> str:
    input_options = recipe.inner.gdal_options.input_options
    return f'{input_options.driver}:{input_options.virtual_filesystem or ""}"{input_options.input_file_path}":{input_options.dataset_path}'


def _build_output_string(recipe: Recipe) -> str:
    output_options = recipe.inner.gdal_options.output_options
    return str(output_options.output_file_path)


def _build_gdal_translate_options(recipe: GdalTranslateRecipe) -> dict:
    translate_options = _build_gdal_output_options(recipe.gdal_options.output_options)
    return translate_options


def _build_gdal_warp_options(recipe: GdalWarpRecipe) -> dict:
    warp_options = _build_gdal_output_options(recipe.gdal_options.output_options)

    flattened_recipe_dictionary = {}

    for key, value in asdict(recipe.warp_options).items():
        if isinstance(value, dict):
            for inner_key, inner_value in value.items():
                flattened_recipe_dictionary[f'{key}.{inner_key}'] = inner_value
        else:
            flattened_recipe_dictionary[key] = value

    recipe_gdal_mapping = {
        'target_srs': 'dstSRS',
        'source_srs': 'srcSRS',
        'src_alpha': 'srcAlpha',
        'dst_alpha': 'dstAlpha',
        'multithreaded': 'multithread',
        'copy_metadata': 'copyMetadata',
        'spatial_subset.output_bounds': 'outputBounds',
        'spatial_subset.output_bounds_srs': 'outputBoundsSRS',
        'spatial_subset.cutline_wkt': 'cutlineWKT',
        'spatial_subset.cutline_srs': 'cutlineSRS',
        'spatial_subset.cutline_layer': 'cutlineLayer',
        'spatial_subset.cutline_where': 'cutlineWhere',
        'spatial_subset.cutline_sql': 'cutlineSQL',
        'spatial_subset.cutline_blend': 'cutlineBlend',
        'spatial_subset.crop_to_cutline': 'cropToCutline',
    }

    for maps_from, maps_to in recipe_gdal_mapping.items():
        if maps_from in flattened_recipe_dictionary:
            warp_options[maps_to] = flattened_recipe_dictionary[maps_from]

    return warp_options


def _build_gdal_output_options(output_options: GdalOutputOptions) -> dict:
    gdal_output_options = {}
    gdal_output_options['format'] = output_options.output_type
    return gdal_output_options


def _validate_recipe_input(recipe: Recipe) -> None:
    _validate_input_string(_build_input_string(recipe), recipe)

    match recipe.inner:
        case GdalWarpRecipe() as warp_recipe:
            if (target_srs := warp_recipe.warp_options.target_srs) is not None:
                _validate_srs(target_srs)


def _validate_input_string(input_string: str, recipe: Recipe) -> None:
    input_options = recipe.inner.gdal_options.input_options
    truth_file = OpenEx(
        f'{input_options.virtual_filesystem or ""}{input_options.input_file_path}',
        allowed_drivers=[input_options.driver],
    )
    truth_input_strings = [dataset[0] for dataset in truth_file.GetSubDatasets()]

    if input_string not in truth_input_strings:
        raise MissingVariableError(input_options.dataset_path)


def _validate_srs(srs: str) -> None:
    valid_codes = ['EPSG:4326', 'EPSG:3031', 'EPSG:3413', 'EPSG:3412']

    for code in chain(range(32601, 32661), range(32701, 32761)):
        valid_codes += f'EPSG:{code}'

    if srs not in valid_codes:
        raise InvalidProjectionError(srs)

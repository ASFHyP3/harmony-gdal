from pathlib import Path

from osgeo.gdal import Translate, TranslateOptions, Warp, WarpOptions

from harmony_gdal_adapter.recipes import (
    GdalOutputOptions,
    GdalTranslateRecipe,
    GdalWarpBoundsSpatialSubset,
    GdalWarpCutlineSpatialSubset,
    GdalWarpRecipe,
    Recipe,
)


def execute_recipe(recipe: Recipe) -> None:
    srcDS = build_input_string(recipe)
    destName = build_output_string(recipe)
    if isinstance(recipe, GdalTranslateRecipe):
        execute_gdal_translate_recipe(srcDS, destName, recipe)
    elif isinstance(recipe, GdalWarpRecipe):
        execute_gdal_warp_recipe(srcDS, destName, recipe)
    else:
        raise TypeError('recipe must be GdalTranslateRecipe or GdalWarpRecipe')


def execute_gdal_translate_recipe(srcDS: str, destName: str, recipe: GdalTranslateRecipe) -> None:
    translate_options = build_gdal_translate_options(recipe)
    Translate(destName, srcDS, **translate_options)


def execute_gdal_warp_recipe(srcDS: str, destName: str, recipe: GdalWarpRecipe) -> None:
    warp_options = build_gdal_warp_options(recipe)
    Warp(destName, srcDS, **warp_options)


def build_input_string(recipe: Recipe) -> str:
    input_options = recipe.inner.gdal_options.inputOptions
    return f'{input_options.driver}:{input_options.virtual_filesystem}{input_options.filename}:{input_options.dataset_path}'


def build_output_string(recipe: Recipe) -> str:
    output_options = recipe.inner.gdal_options.outputOptions
    output_path = Path(output_options.outputDirectory)
    output_path = output_path / output_options.outputDirectory
    return str(output_path)


def build_gdal_translate_options(recipe: GdalTranslateRecipe) -> dict:
    translate_options = build_gdal_output_options(recipe.gdal_options.outputOptions)
    return translate_options


def build_gdal_warp_options(recipe: GdalWarpRecipe) -> dict:
    warp_options = build_gdal_output_options(recipe.gdal_options.outputOptions)
    if recipe.warp_options.target_srs is not None:
        warp_options['dstSRS'] = recipe.warp_options.target_srs
    if recipe.warp_options.source_srs is not None:
        warp_options['srcSRS'] = recipe.warp_options.source_srs
    if recipe.warp_options.srcAlpha is not None:
        warp_options['srcAlpha'] = recipe.warp_options.srcAlpha
    if recipe.warp_options.dstAlpha is not None:
        warp_options['dstAlpha'] = recipe.warp_options.dstAlpha
    warp_options['multithread'] = recipe.warp_options.multithreaded
    warp_options['copyMetadata'] = recipe.warp_options.copyMetadata
    spatial_subset = recipe.warp_options.spatial_subset
    if isinstance(spatial_subset, GdalWarpBoundsSpatialSubset):
        warp_options['outputBounds'] = spatial_subset.outputBounds
        if spatial_subset.outputBoundsSRS is not None:
            warp_options['outputBoundsSRS'] = spatial_subset.outputBoundsSRS
    elif isinstance(spatial_subset, GdalWarpCutlineSpatialSubset):
        warp_options['cutlineWKT'] = spatial_subset.cutline_wkt
        if spatial_subset.cutline_srs is not None:
            warp_options['cutlineSRS'] = spatial_subset.cutline_srs
        if spatial_subset.cutline_layer is not None:
            warp_options['cutlineLayer'] = spatial_subset.cutline_layer
        if spatial_subset.cutline_where is not None:
            warp_options['cutlineWhere'] = spatial_subset.cutline_where
        if spatial_subset.cutline_sql is not None:
            warp_options['cutlineSQL'] = spatial_subset.cutline_sql
        if spatial_subset.cutline_blend is not None:
            warp_options['cutlineBlend'] = spatial_subset.cutline_blend
        warp_options['cropToCutline'] = spatial_subset.crop_to_cutline
    return warp_options


def build_gdal_output_options(output_options: GdalOutputOptions) -> dict:
    gdal_output_options = {}
    gdal_output_options['format'] = output_options.outputType
    return gdal_output_options

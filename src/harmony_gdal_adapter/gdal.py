from dataclasses import dataclass
from osgeo.gdal import WarpOptions, Warp, Translate
from recipes import GdalTranslateRecipe, GdalWarpRecipe, Recipe, GdalWarpBoundsSpatialSubset, \
    GdalWarpCutlineSpatialSubset, GdalWarpOptions
from pathlib import Path

def execute_recipe(recipe: Recipe):
    srcDS = build_input_string(recipe)
    destName = build_output_string(recipe)
    if isinstance(recipe, GdalTranslateRecipe):
        execute_gdal_translate_recipe(srcDS, destName, recipe)
    elif isinstance(recipe, GdalWarpRecipe):
        execute_gdal_warp_recipe(srcDS, destName, recipe)
    else:
        raise ValueError("recipe must be GdalTranslateRecipe or GdalWarpRecipe")


def execute_gdal_translate_recipe(srcDS: str, destName: str, recipe: GdalTranslateRecipe):
    Translate(destName, srcDS)


def execute_gdal_warp_recipe(srcDS: str, destName: str, recipe: GdalWarpRecipe):
    warp_options = build_gdal_warp_options(recipe)
    Warp(destName, srcDS, **warp_options)


def build_gdal_translate_options(recipe: GdalTranslateRecipe):
    raise NotImplementedError()

def build_input_string(recipe: Recipe):
    input_options = recipe.inner.gdal_options.inputOptions
    input_path = Path(input_options.dataset_path)
    input_path = input_path / input_options.filename
    return str(input_path)

def build_output_string(recipe: Recipe):
    output_options = recipe.inner.gdal_options.outputOptions
    output_path = Path(output_options.outputDirectory)
    output_path = output_path / output_options.outputDirectory
    return str(output_path)

def build_gdal_warp_options(recipe: GdalWarpRecipe):
    spatial_subset = recipe.warp_options.spatial_subset
    warp_options = GdalWarpOptions()
    warp_options.dstSRS = recipe.warp_options.target_srs
    warp_options.srcSRS = recipe.warp_options.source_srs
    warp_options.srcAlpha = recipe.warp_options.srcAlpha
    warp_options.dstAlpha = recipe.warp_options.dstAlpha
    warp_options.multithread = recipe.warp_options.multithreaded
    warp_options.copyMetadata = recipe.warp_options.copyMetadata
    if isinstance(spatial_subset, GdalWarpBoundsSpatialSubset):
        warp_options.outputBounds = spatial_subset.outputBounds
        warp_options.outputBoundsSRS = spatial_subset.outputBoundsSRS
    elif isinstance(spatial_subset,GdalWarpCutlineSpatialSubset):
        warp_options.cutlineWKT = spatial_subset.cutline_wkt
        warp_options.cutlineSRS = spatial_subset.cutline_srs
        warp_options.cutlineLayer = spatial_subset.cutline_layer
        warp_options.cutlineWhere = spatial_subset.cutline_where
        warp_options.cutlineSQL = spatial_subset.cutline_sql
        warp_options.cutlineBlend = spatial_subset.cutline_blend
        warp_options.cropToCutline = spatial_subset.crop_to_cutline
    return warp_options

"""Execute GDAL recipes."""

from dataclasses import asdict
from harmony_gdal_adapter.build_recipes import (
    GdalOutputOptions,
    GdalWarpBoundsSpatialSubset,
    GdalWarpCutlineSpatialSubset,
    GdalTranslateRecipe,
    GdalWarpRecipe,
    Recipe,
)
from osgeo.gdal import Translate, Warp
from osgeo import ogr, osr, gdal
import pprint

def execute_recipe(recipe: Recipe) -> None:
    """Executes a built Recipe as a GDAL operation.

    Args:
        recipe (Recipe): The Recipe representing a given GDAL translate or warp operation.

    Returns:
        None
    """
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
    pprint.pprint(recipe)
    recipe = _clip_spatial_extents(recipe)
    pprint.pprint(recipe)
    warp_options = _build_gdal_warp_options(recipe)
    Warp(destName, srcDS, **warp_options)


def _build_input_string(recipe: Recipe) -> str:
    input_options = recipe.inner.gdal_options.input_options
    return f'{input_options.driver}:{input_options.virtual_filesystem or ""}{input_options.input_file_path}:{input_options.dataset_path}'


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


def _clip_spatial_extents(recipe: GdalWarpRecipe) -> GdalWarpRecipe:
    """
    Clip the spatial extents arguments to fit within the bounding box
    """
    if isinstance(recipe.warp_options.spatial_subset, GdalWarpBoundsSpatialSubset):
        print("bbox clip")
        recipe.warp_options.spatial_subset.output_bounds = _calculate_bounding_box_intersection(recipe)
    if isinstance(recipe.warp_options.spatial_subset, GdalWarpCutlineSpatialSubset):
        print("wkt clip")
        recipe.warp_options.spatial_subset.cutline_wkt = _calculate_wkt_intersection(recipe)
    return recipe


def _calculate_wkt_intersection(recipe: GdalWarpRecipe) -> str:
    """
    Calculate the intersection of wkt spatial extent and the asset extent
    """
    subset_polygon = _create_polygon_from_wkt(
        recipe.warp_options.spatial_subset.cutline_wkt,
        recipe.warp_options.spatial_subset.cutline_srs
        )
    intersection_polygon = _calculate_polygon_intersection(subset_polygon, recipe)
    intersection_wkt = intersection_polygon.ExportToWkt()
    return intersection_wkt

def _calculate_bounding_box_intersection(recipe:GdalWarpRecipe) -> [float, float, float, float]:
    """
    Calculate the intersection of bounding box spatial extent and the asset extent
    """
    subset_polygon = _create_polygon_from_bounding_box(
        recipe.warp_options.spatial_subset.output_bounds,
        recipe.warp_options.spatial_subset.output_bounds_srs
    )
    intersection_polygon = _calculate_polygon_intersection(subset_polygon, recipe)
    intersection_envelope = intersection_polygon.GetEnvelope()
    # envelope is in format [minx, maxx, miny, maxy], must be rearranged to [minx, min, maxx, maxy]
    intersection_bounding_box = \
    [intersection_envelope[0], intersection_envelope[2], \
     intersection_envelope[1], intersection_envelope[3]]
    return intersection_bounding_box


def _calculate_polygon_intersection(subset_polygon: ogr.Geometry, recipe: GdalWarpRecipe) -> ogr.Geometry:
    """
    calculate the intersection of polygon spatial extent and the asset extent
    """
    source_polygon = _get_asset_polygon(recipe, subset_polygon.GetSpatialReference())
    assert subset_polygon.IsValid(), "spatial extent polygon invalid"
    assert source_polygon.IsValid(), "source data polygon invalid"
    assert subset_polygon.Intersects(source_polygon), "Subset polygon and source polygon do not overlap"
    intersection_polygon = subset_polygon.Intersection(source_polygon)
    return intersection_polygon


def _create_polygon_from_bounding_box(bounding_box: [float,float, float, float], bounding_box_srs: str | None) -> ogr.geometry.Polygon:
    polygon_srs = osr.SpatialReference()
    polygon_srs.SetFromUserInput(bounding_box_srs)
    polygon = ogr.CreateGeometryFromEnvelope(*bounding_box)
    polygon.AssignSpatialReference(polygon_srs)
    return polygon


def _create_polygon_from_wkt(cutline_wkt: str, cutline_srs: str | None) -> ogr.geometry.Polygon:
    polygon_srs = osr.SpatialReference()
    polygon_srs.SetFromUserInput(cutline_srs)
    return ogr.CreateGeometryFromWkt(cutline_wkt, reference=polygon_srs)

def _get_asset_polygon(recipe: Recipe, bounds_srs: osr.SpatialReference) -> ogr.geometry.Polygon:
    """
    Return Asset spatial extents as a polygon in the SRS of the bounding polygon
    """
    #force longitude to x axis
    bounds_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    gdal_driver = recipe.gdal_options.input_options.driver
    if recipe.gdal_options.input_options.dataset_path:
        gdal_dataset_string = \
            f"{gdal_driver}:{recipe.gdal_options.input_options.input_file_path}:{recipe.gdal_options.input_options.dataset_path}"
    else:
        gdal_dataset_string = f"{gdal_driver}:{recipe.gdal_options.input_options.input_file_path}"
    dataset = gdal.Open(gdal_dataset_string)
    dataset_extents = dataset.GetExtent()
    pprint.pprint(dataset_extents)
    dataset_bounding_box = [dataset_extents[0], dataset_extents[2], \
    dataset_extents[1], dataset_extents[3]]
    dataset_srs = dataset.GetSpatialRef()
    transformer = osr.CoordinateTransformation(dataset_srs, bounds_srs)
    dataset_bounding_box = transformer.TransformBounds(*dataset_bounding_box, 21)
    asset_polygon = ogr.CreateGeometryFromEnvelope(*dataset_bounding_box)
    asset_polygon.AssignSpatialReference(bounds_srs)
    return asset_polygon
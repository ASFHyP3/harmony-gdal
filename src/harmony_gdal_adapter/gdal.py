"""Execute GDAL recipes."""

from itertools import chain
from typing import TypedDict, cast

from osgeo import gdal, ogr, osr
from osgeo.gdal import OpenEx, Translate, UseExceptions, Warp

from harmony_gdal_adapter.build_recipes import (
    GdalOutputOptions,
    GdalTranslateRecipe,
    GdalWarpBoundsSpatialSubset,
    GdalWarpCutlineSpatialSubset,
    GdalWarpRecipe,
    Recipe,
)
from harmony_gdal_adapter.exceptions import InvalidProjectionError, MissingVariableError


class _WarpOptions(TypedDict, total=False):
    format: str | None
    dstSRS: str | None
    srcSRS: str | None
    srcAlpha: bool | None
    dstAlpha: bool | None
    multithread: bool | None
    copyMetadata: bool | None
    outputBounds: list[float] | None
    outputBoundsSRS: str | None
    cutlineWKT: str | None
    cutlineSRS: str | None
    cutlineWhere: str | None
    cutlineSQL: str | None
    cutlineBlend: int | None
    cropToCutline: bool | None


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


def _validate_recipe_input(recipe: Recipe) -> None:
    _validate_input_string(_build_input_string(recipe), recipe)

    match recipe.inner:
        case GdalWarpRecipe() as warp_recipe:
            if (target_srs := warp_recipe.warp_options.target_srs) is not None:
                _validate_srs(target_srs)


def execute_recipe(recipe: Recipe) -> None:
    """Executes a built Recipe as a GDAL operation.

    Args:
        recipe (Recipe): The Recipe representing a given GDAL translate or warp operation.

    Returns:
        None
    """
    source_dataset = _build_input_string(recipe)
    destination_name = _build_output_string(recipe)
    UseExceptions()
    _validate_recipe_input(recipe)

    match recipe.inner:
        case GdalTranslateRecipe() as translate_recipe:
            _execute_gdal_translate_recipe(source_dataset, destination_name, translate_recipe)
        case GdalWarpRecipe() as warp_recipe:
            _execute_gdal_warp_recipe(source_dataset, destination_name, warp_recipe)
        case _:
            raise TypeError('recipe must be GdalTranslateRecipe or GdalWarpRecipe')


def _execute_gdal_translate_recipe(source_dataset: str, destination_name: str, recipe: GdalTranslateRecipe) -> None:
    translate_options = _build_gdal_translate_options(recipe)
    Translate(destination_name, source_dataset, **translate_options)


def _execute_gdal_warp_recipe(source_dataset: str, destination_name: str, recipe: GdalWarpRecipe) -> None:
    if isinstance(recipe.warp_options.spatial_subset, GdalWarpBoundsSpatialSubset):
        recipe.warp_options.spatial_subset = _convert_bounds_subset_to_cutline_subset(
            recipe.warp_options.spatial_subset
        )
    recipe = _clip_spatial_extents(recipe)
    warp_options = _build_gdal_warp_options(recipe)
    Warp(destination_name, source_dataset, **warp_options)


def _build_input_string(recipe: Recipe) -> str:
    """Return input string file from recipe."""
    input_options = recipe.inner.gdal_options.input_options
    return f'{input_options.driver}:{input_options.virtual_filesystem or ""}"{input_options.input_file_path}":{input_options.dataset_path}'


def _build_output_string(recipe: Recipe) -> str:
    """Return output file path from recipe."""
    output_options = recipe.inner.gdal_options.output_options
    return str(output_options.output_file_path)


def _build_gdal_translate_options(recipe: GdalTranslateRecipe) -> dict:
    translate_options = _build_gdal_output_options(recipe.gdal_options.output_options)
    return translate_options


def _build_gdal_warp_options(recipe: GdalWarpRecipe) -> _WarpOptions:
    input_warp_options = recipe.warp_options

    warp_options = _build_gdal_output_options(recipe.gdal_options.output_options)

    warp_options |= _WarpOptions(
        dstSRS=input_warp_options.target_srs,
        srcSRS=input_warp_options.source_srs,
        srcAlpha=input_warp_options.src_alpha,
        dstAlpha=input_warp_options.dst_alpha,
        multithread=input_warp_options.multithreaded,
        copyMetadata=input_warp_options.copy_metadata,
    )

    if spatial_subset := input_warp_options.spatial_subset:
        match spatial_subset:
            case GdalWarpBoundsSpatialSubset() as bounds:
                warp_options |= _WarpOptions(
                    outputBounds=bounds.output_bounds, outputBoundsSRS=bounds.output_bounds_srs
                )
            case GdalWarpCutlineSpatialSubset() as cutline:
                warp_options |= _WarpOptions(
                    cutlineWKT=cutline.cutline_wkt,
                    cutlineSRS=cutline.cutline_srs,
                    cutlineWhere=cutline.cutline_where,
                    cutlineSQL=cutline.cutline_sql,
                    cutlineBlend=cutline.cutline_blend,
                    cropToCutline=cutline.crop_to_cutline,
                )

    warp_options = cast(_WarpOptions, {k: v for k, v in warp_options.items() if v is not None})

    return warp_options


def _build_gdal_output_options(output_options: GdalOutputOptions) -> dict:
    """Build gdalOptions dictionary."""
    gdal_output_options = {}
    gdal_output_options['format'] = output_options.output_type
    return gdal_output_options


def _clip_spatial_extents(recipe: GdalWarpRecipe) -> GdalWarpRecipe:
    """Clip the spatial extents arguments to fit within the bounding box."""
    match recipe.warp_options.spatial_subset:
        case GdalWarpBoundsSpatialSubset():
            recipe.warp_options.spatial_subset.output_bounds = _calculate_bounding_box_intersection(recipe)
        case GdalWarpCutlineSpatialSubset():
            recipe.warp_options.spatial_subset.cutline_wkt = _calculate_wkt_intersection(recipe)
    return recipe


def _calculate_wkt_intersection(recipe: GdalWarpRecipe) -> str:
    """Calculate the intersection of wkt spatial extent and granule extent."""
    subset_polygon = _create_polygon_from_wkt(
        recipe.warp_options.spatial_subset.cutline_wkt, recipe.warp_options.spatial_subset.cutline_srs
    )
    intersection_polygon = _calculate_polygon_intersection(subset_polygon, recipe)
    intersection_wkt = intersection_polygon.ExportToWkt()
    return intersection_wkt


def _calculate_bounding_box_intersection(recipe: GdalWarpRecipe) -> list[float]:
    """Calculate the intersection of bounding box spatial extent and granule extent."""
    subset_polygon = _create_polygon_from_bounding_box(
        recipe.warp_options.spatial_subset.output_bounds, recipe.warp_options.spatial_subset.output_bounds_srs
    )
    intersection_polygon = _calculate_polygon_intersection(subset_polygon, recipe)
    intersection_envelope = intersection_polygon.GetEnvelope()
    # envelope is in format [minx, maxx, miny, maxy], must be rearranged to [minx, min, maxx, maxy]
    intersection_bounding_box = [
        intersection_envelope[0],
        intersection_envelope[2],
        intersection_envelope[1],
        intersection_envelope[3],
    ]
    return intersection_bounding_box


def _calculate_polygon_intersection(subset_polygon: ogr.Geometry, recipe: GdalWarpRecipe) -> ogr.Geometry:
    """Calculate the intersection of subset polygon spatial extent and granule polygon extent."""
    source_polygon = _get_granule_polygon(recipe, subset_polygon.GetSpatialReference())
    assert subset_polygon.IsValid(), 'spatial extent polygon invalid'
    assert source_polygon.IsValid(), 'source data polygon invalid'
    print(f"do they intersect?: {subset_polygon.Intersects(source_polygon)}")
    assert subset_polygon.Intersects(source_polygon), 'Subset polygon and source polygon do not overlap'
    intersection_polygon = subset_polygon.Intersection(source_polygon)
    return intersection_polygon


def _convert_bounds_subset_to_cutline_subset(
        bounds_subset: GdalWarpBoundsSpatialSubset,
) -> GdalWarpCutlineSpatialSubset:
    """Convert GdalWarpBoundsSpatialSubset to GdalWarpCutlineSpatialSubset."""
    polygon = _create_polygon_from_bounding_box(bounds_subset.output_bounds, bounds_subset.output_bounds_srs)
    wkt = polygon.ExportToWkt()
    cutline_subset = GdalWarpCutlineSpatialSubset(
        cutline_wkt=wkt, cutline_srs=bounds_subset.output_bounds_srs, crop_to_cutline=True
    )
    return cutline_subset


def _create_polygon_from_bounding_box(bounding_box: list[float], bounding_box_srs: str | None) -> ogr.geometry.Polygon:
    """Create polygon object from bounding box."""
    polygon_srs = osr.SpatialReference()
    polygon_srs.SetFromUserInput(bounding_box_srs)
    polygon = ogr.CreateGeometryFromEnvelope(*bounding_box)
    polygon.AssignSpatialReference(polygon_srs)
    return polygon


def _create_polygon_from_wkt(cutline_wkt: str, cutline_srs: str | None) -> ogr.geometry.Polygon:
    """Create polygon object from wkt string."""
    polygon_srs = osr.SpatialReference()
    polygon_srs.SetFromUserInput(cutline_srs)
    return ogr.CreateGeometryFromWkt(cutline_wkt, reference=polygon_srs)


def _get_granule_polygon(recipe: Recipe, bounds_srs: osr.SpatialReference) -> ogr.geometry.Polygon:
    """Return granule spatial extents as a polygon in the SRS of the bounding polygon."""
    # force longitude to x axis
    bounds_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    gdal_driver = recipe.gdal_options.input_options.driver
    if recipe.gdal_options.input_options.dataset_path:
        gdal_dataset_string = f'{gdal_driver}:{recipe.gdal_options.input_options.input_file_path}:{recipe.gdal_options.input_options.dataset_path}'
    else:
        gdal_dataset_string = f'{gdal_driver}:{recipe.gdal_options.input_options.input_file_path}'
    dataset = gdal.Open(gdal_dataset_string)
    dataset_extents = dataset.GetExtent(srs=bounds_srs)
    dataset_bounding_box = [dataset_extents[0], dataset_extents[2], dataset_extents[1], dataset_extents[3]]
    granule_polygon = ogr.CreateGeometryFromEnvelope(*dataset_bounding_box)
    granule_polygon.AssignSpatialReference(bounds_srs)
    return granule_polygon


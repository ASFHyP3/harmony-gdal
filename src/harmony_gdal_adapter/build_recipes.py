"""Build a GDAL Recipe and the GDAL Recipe related types."""

import json
from dataclasses import asdict, dataclass, field
from importlib.resources import files
from typing import Literal

import dacite
from kcl_lib import api as kcl

from harmony_gdal_adapter.exceptions import InputValidationError


@dataclass
class RecipeInputOptions:
    """Input options used by recipes."""

    collection_shortname: str
    input_filename: str
    output_type: str
    output_filename: str
    variable_path: str
    spatial_extents_bounding_box: list[float] | None = field(metadata={'type': float, 'nargs': 4}, default=None)
    target_srs: str | None = None
    spatial_extents_wkt: str | None = None


@dataclass
class GdalInputOptions:
    """GdalInputOptions specifies the options which are used to template the srcDS input string.

    Attributes:
    ----------
    driver : str
        The raster driver to use for loading the input dataset. Must be a valid GDAL raster driver. See [here](https://gdal.org/en/stable/drivers/raster/index.html) for a list of available GDAL raster drivers.
    virtual_filesystem : str, optional, default is None
        The virtual filesystem to use for loading the input dataset. Must be a valid GDAL virtual filesystem name. See [here](https://gdal.org/en/stable/user/virtual_file_systems.html) for a list of available GDAL virtual filesystems.
    dataset_path : str
        The dataset, or variable to extract from the input file.
    input_file_path : str
        The input file path to perform operations on.
    """

    driver: Literal['HDF5', 'NETCDF']
    dataset_path: str
    input_file_path: str
    virtual_filesystem: Literal['/vsicurl/', '/vsis3/'] | None = None


@dataclass
class GdalOutputOptions:
    """GdalOutputOptions specifies the output options to use.

    Attributes:
    ----------
    output_type (str, optional):
        The raster driver to use for output. See [here](https://gdal.org/en/stable/drivers/raster/index.html) for a list of available GDAL raster drivers.
    output_file_path (str, default):
        The file path to output to.
    """

    output_type: Literal['GTiff', 'COG']
    output_file_path: str = 'output'


@dataclass
class GdalOptions:
    """GdalOptions specifies the options which are common to both GDAL Warp and Translate operations.

    Attributes:
    ----------
    input_options (GdalInputOptions):
        The input file path, type, and whether to use a virtual filesystem.
    output_options (GdalOutputOptions):
        The output file path and type.
    config_options (dict, optional):
        The GDAL configuration options to use.
    """

    input_options: GdalInputOptions
    output_options: GdalOutputOptions
    config_options: dict | None = None


@dataclass
class GdalWarpBoundsSpatialSubset:
    """GdalWarpBoundsSpatialSubset allows performing spatial subsetting with a pair of points defining a bounding box.

    Attributes:
    ----------
    output_bounds ((float, float, float, float)):
        The bounding box to spatially subset to.
        Maps directly to GDAL's outputBounds option in osgeo.gdal.WarpOptions.
    output_bounds_srs (str):
        The bounding box to spatially subset to. Must be an accepted GDAL SRS string.
        Maps directly to GDAL's outputBoundsSRS option in osgeo.gdal.WarpOptions.
    """

    output_bounds: list[float]
    output_bounds_srs: str | None = None


@dataclass
class GdalWarpCutlineSpatialSubset:
    """GdalWarpCutlineSpatialSubset allows performing spatial subsetting with a WKT string utilizing GDAL Warp's cutline options.

    Attributes:
    ----------
    cutline_wkt (str):
        The cutline WKT string to operate on. Must be a WKT POLYGON or MULTIPOLYGON string.
        Maps directly to GDAL's cutlineWKT option in osgeo.gdal.WarpOptions.
    cutline_srs (str):
        The spatial reference system of the cutline WKT string. Must be an accepted GDAL SRS string.
        Maps directly to GDAL's cutlineSRS option in osgeo.gdal.WarpOptions.
    cutline_where (str, optional):
        The cutline WHERE clause.
        Maps directly to GDAL's cutlineWHERE option in osgeo.gdal.WarpOptions.
    cutline_sql (str, optional):
        The cutline SQL statement.
        Maps directly to GDAL's cutlineSQL option in osgeo.gdal.WarpOptions.
    cutline_blend (int, optional):
        The cutline blend distance in pixels.
        Maps directly to GDAL's cutlineBlend option in osgeo.gdal.WarpOptions.
    crop_to_cutline (bool):
        Wether to use the cutline extent for output bounds.
        Maps directly to GDALts cropToCutline option isn osgeo.gdal.WarpOptions.
    """

    cutline_wkt: str
    cutline_srs: str | None = None
    cutline_where: str | None = None
    cutline_sql: str | None = None
    cutline_blend: int | None = None
    crop_to_cutline: bool = True


@dataclass
class GdalWarpOptions:
    """GdalWarpOptions specifies the GDAL options specific to Warp operations.

    Attributes:
    ----------
    spatial_subset (GdalWarpBoundsSpatialSubset | GdalWarpCutlineSpatialSubset, optional):
        Specify a spatial subsetting operation to perform. If none is specified no spatial subsetting operation will be performed.
    target_srs (str, optional):
        Specify a spatial reference system to reproject into. Must be an accepted GDAL SRS string. If none is specified no reprojection operation will be performed.
        Maps directly to GDAL's targetSRS option in osgeo.gdal.WarpOptions.
    source_srs (str, optional):
        Specify the spatial reference system which the input dataset is referenced in. If none is specified GDAL will utilize the spatial reference system supplied by the input dataset.
        Maps directly to GDAL's sourceSRS option in osgeo.gdal.WarpOptions.
    src_alpha (bool, optional):
        Whether to force the input dataset to be considered as an alpha band. If none is specified GDAL will attempt to automatically determine if the input dataset contains an alpha band.
        Maps directly to GDAL's srcAlpha option in osgeo.gdal.WarpOptions.
    dst_alpha (bool, optional):
        Whether to force the creation of an output alpha band. If none is specified GDAL will attempt to automatically determine if the creation of an output alpha band is suitable.
        Maps directly to GDAL's dstAlpha option in osgeo.gdal.WarpOptions.
    multithreaded (bool):
        Whether to use multithreaded compute and I/O operations.
        Maps directly to GDAL's multithreaded option in osgeo.gdal.WarpOptions.
    copy_metadata (bool):
        Whether to copy the source metadata.
        Maps directly to GDAL's copyMetadata option in osgeo.gdal.WarpOptions.
    """

    spatial_subset: GdalWarpBoundsSpatialSubset | GdalWarpCutlineSpatialSubset | None = None
    target_srs: str | None = None
    source_srs: str | None = None
    src_alpha: bool | None = None
    dst_alpha: bool | None = None
    multithreaded: bool = True
    copy_metadata: bool = True


@dataclass
class GdalWarpRecipe:
    """GdalWarpRecipe specifies the options for a given GDAL warp run.

    Attributes:
    ----------
    warp_options (GdalWarpOptions):
        The reprojection and spatial subsetting options
    gdal_options (GdalOptions):
        The input, output and config options for the GDAL translate run.
    """

    warp_options: GdalWarpOptions
    gdal_options: GdalOptions


@dataclass
class GdalTranslateRecipe:
    """GdalTranslateRecipe specifies the options for a given GDAL translate run.

    Attributes:
    ----------
    gdal_options (GdalOptions):
        The input, output and config options for the GDAL translate run.
    """

    gdal_options: GdalOptions


@dataclass
class Recipe:
    """Recipe specifies the options for a given GDAL warp or translate processing step.

    Attributes:
    ----------
    inner (GdalWarpRecipe | GdalTranslateRecipe):
        The inner GdalWarpRecipe or GdalTranslateRecipe
    """

    inner: GdalWarpRecipe | GdalTranslateRecipe


def build_recipe(options: RecipeInputOptions) -> Recipe:
    """Builds a Recipe for execution from the nisar.k recipe file with the given recipe input options.

    Args:
        options (RecipeInputOptions): the input options for the recipe file

    Returns:
        Recipe: The built recipe from the input options
    """
    recipe_args = [
        kcl.Argument(name=name, value=str(value)) for name, value in asdict(options).items() if value is not None
    ]
    args = kcl.ExecProgramArgs(
        k_filename_list=[str(files(__package__).joinpath('recipes/nisar.k'))],
        error_format='short',
        args=recipe_args,
    )
    api = kcl.API()
    result = api.exec_program(args)
    if result.err_message:
        raise InputValidationError(result.err_message)

    recipe_dict = json.loads(result.json_result)['recipe']
    recipe = dacite.from_dict(data_class=Recipe, data=recipe_dict, config=dacite.Config(strict=True))
    return recipe

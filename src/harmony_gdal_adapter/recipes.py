from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Tuple


@dataclass
class RecipeInputOptions:
    """Input options used by recipes."""

    collection_shortname: str
    input_filename: Path
    target_srs: str | None
    spatial_extents: str | None
    output_type: str
    output_filename: str


def build_recipe(options: RecipeInputOptions) -> Recipe:
    """Builds a Recipe for execution from the nisar.k recipe file with the given recipe input options.

    Args:
        options (RecipeInputOptions): the input options for the recipe file

    Returns:
        Recipe: The built recipe from the input options
    """
    raise NotImplementedError()


type Recipe = GdalTranslateRecipe | GdalWarpRecipe


class GdalInputOptions:
    driver: Literal['HDF5'] | Literal['NETCDF']
    virtual_filesystem: Optional[Literal['/vsicurl/'] | Literal['/vsis3/']]
    dataset_path: str
    filename: str


class GdalOutput:
    name: str
    extension: str


class GdalOutputOptions:
    outputType: GdalOutput
    outputDirectory: str = ''
    outputName: str = 'output'


class GdalOptions:
    inputOptions: GdalInputOptions
    outputOptions: GdalOutputOptions
    configOptions: dict


class GdalWarpBoundsSpatialSubset:
    outputBounds: Tuple[float, float, float, float]
    outputBoundsSRS: str | None


class GdalWarpCutlineSpatialSubset:
    cutline_wkt: str
    cutline_srs: Optional[str]
    cutline_layer: Optional[str]
    cutline_where: Optional[str]
    cutline_sql: Optional[str]
    cutline_blend: Optional[int]
    crop_to_cutline: bool = True


class GdalWarpOptions:
    spatial_subset: Optional[GdalWarpBoundsSpatialSubset | GdalWarpCutlineSpatialSubset]
    reproject_to_srs: Optional[str]
    source_srs: Optional[str]
    srcAlpha: Optional[bool]
    dstAlpha: Optional[bool]
    multithreaded: bool = True
    copyMetadata: bool = True


class GdalWarpRecipe:
    warp_options: GdalWarpOptions
    gdal_options: GdalOptions


class GdalTranslateRecipe:
    gdal_options: GdalOptions

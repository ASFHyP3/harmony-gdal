import json
from dataclasses import asdict, dataclass
from importlib.resources import files
from pathlib import Path
from typing import Literal

from dacite import from_dict
from kcl_lib import api as kcl


@dataclass
class RecipeInputOptions:
    """Input options used by recipes."""

<<<<<<< HEAD
    collection_shortname: str | None = None
    input_filename: Path | None = None
    target_srs: str | None = None
    spatial_extents: str | None = None
    output_type: str | None = None
    output_filename: str | None = None
=======
    collection_shortname: str
    input_filename: Path
    output_type: str
    output_filename: str
    variable_path: str
    target_srs: str | None = None
    spatial_extents: str | None = None


@dataclass
class GdalInputOptions:
    driver: Literal['HDF5', 'NETCDF']
    virtual_filesystem: Literal['/vsicurl/', '/vsis3/'] | None
    dataset_path: str
    filename: str


@dataclass
class GdalOutput:
    name: str
    extension: str


@dataclass
class GdalOutputOptions:
    outputType: GdalOutput
    outputDirectory: str = ''
    outputName: str = 'output'


@dataclass
class GdalOptions:
    inputOptions: GdalInputOptions
    outputOptions: GdalOutputOptions
    configOptions: dict


@dataclass
class GdalWarpBoundsSpatialSubset:
    outputBounds: tuple[float, float, float, float]
    outputBoundsSRS: str | None


@dataclass
class GdalWarpCutlineSpatialSubset:
    cutline_wkt: str
    cutline_srs: str | None
    cutline_layer: str | None
    cutline_where: str | None
    cutline_sql: str | None
    cutline_blend: int | None
    crop_to_cutline: bool = True


@dataclass
class GdalWarpOptions:
    spatial_subset: GdalWarpBoundsSpatialSubset | GdalWarpCutlineSpatialSubset | None
    target_srs: str | None
    source_srs: str | None
    srcAlpha: bool | None
    dstAlpha: bool | None
    multithreaded: bool = True
    copyMetadata: bool = True


@dataclass
class GdalWarpRecipe:
    warp_options: GdalWarpOptions
    gdal_options: GdalOptions


@dataclass
class GdalTranslateRecipe:
    gdal_options: GdalOptions


@dataclass
class Recipe:
    inner: GdalTranslateRecipe | GdalWarpRecipe
>>>>>>> develop


def build_recipe(options: RecipeInputOptions) -> Recipe:
    """Builds a Recipe for execution from the nisar.k recipe file with the given recipe input options.

    Args:
        options (RecipeInputOptions): the input options for the recipe file

    Returns:
        Recipe: The built recipe from the input options
    """
    args = kcl.ExecProgramArgs(
        k_filename_list=[str(files(__package__).joinpath('recipes/nisar.k'))],
        args=[kcl.Argument(name=name, value=value) for name, value in asdict(options)],
    )
    api = kcl.API()
    result = api.exec_program(args)

    return from_dict(data_class=Recipe, data=json.loads(result.json_result))

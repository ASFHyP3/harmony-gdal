import json
from dataclasses import asdict, dataclass
from importlib.resources import files
from typing import Literal

from dacite import from_dict
from kcl_lib import api as kcl


@dataclass
class RecipeInputOptions:
    """Input options used by recipes."""

    collection_shortname: str
    input_filename: str
    output_type: str
    output_filename: str
    variable_path: str
    target_srs: str | None = None
    spatial_extents: str | None = None


@dataclass
class GdalInputOptions:
    driver: Literal['HDF5', 'NETCDF']
    dataset_path: str
    filename: str
    virtual_filesystem: Literal['/vsicurl/', '/vsis3/'] | None = None


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
    configOptions: dict | None = None


@dataclass
class GdalWarpBoundsSpatialSubset:
    outputBounds: tuple[float, float, float, float]
    outputBoundsSRS: str | None = None


@dataclass
class GdalWarpCutlineSpatialSubset:
    cutline_wkt: str
    cutline_srs: str | None = None
    cutline_layer: str | None = None
    cutline_where: str | None = None
    cutline_sql: str | None = None
    cutline_blend: int | None = None
    crop_to_cutline: bool = True


@dataclass
class GdalWarpOptions:
    spatial_subset: GdalWarpBoundsSpatialSubset | GdalWarpCutlineSpatialSubset | None = None
    target_srs: str | None = None
    source_srs: str | None = None
    srcAlpha: bool | None = None
    dstAlpha: bool | None = None
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
    inner: GdalWarpRecipe | GdalTranslateRecipe


def build_recipe(options: RecipeInputOptions) -> Recipe:
    """Builds a Recipe for execution from the nisar.k recipe file with the given recipe input options.

    Args:
        options (RecipeInputOptions): the input options for the recipe file

    Returns:
        Recipe: The built recipe from the input options
    """
    recipe_args = [kcl.Argument(name=name, value=value) for name, value in asdict(options).items()]
    args = kcl.ExecProgramArgs(
        k_filename_list=[str(files(__package__).joinpath('recipes/nisar.k'))],
        args=recipe_args,
    )
    api = kcl.API()
    result = api.exec_program(args)
    recipe_dict = json.loads(result.json_result)['recipe']
    recipe = from_dict(data_class=Recipe, data=recipe_dict)
    return recipe

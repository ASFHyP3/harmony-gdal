import json
from dataclasses import asdict, dataclass
from importlib.resources import files
from typing import Literal

from dacite import from_dict
from kcl_lib import api as kcl


@dataclass
class RecipeInputOptions:
    """Input options used by recipes."""

    collectionShortname: str
    inputFilename: str
    outputType: str
    outputFilename: str
    variablePath: str
    targetSRS: str | None = None
    spatialExtents: str | None = None


@dataclass
class GdalInputOptions:
    driver: Literal['HDF5', 'NETCDF']
    datasetPath: str
    inputFilePath: str
    virtualFilesystem: Literal['/vsicurl/', '/vsis3/'] | None = None


@dataclass
class GdalOutputOptions:
    outputType: Literal['GTiff', 'COG']
    outputFilePath: str = 'output'


@dataclass
class GdalOptions:
    inputOptions: GdalInputOptions
    outputOptions: GdalOutputOptions
    configOptions: dict | None = None


@dataclass
class GdalWarpBoundsSpatialSubset:
    outputBounds: tuple[float, float, float, float]
    outputBondsSRS: str | None = None


@dataclass
class GdalWarpCutlineSpatialSubset:
    cutlineWKT: str
    cutlineSRS: str | None = None
    cutlineWhere: str | None = None
    cutlineSQL: str | None = None
    cutlineBlend: int | None = None
    cropToCutline: bool = True


@dataclass
class GdalWarpOptions:
    spatialSubset: GdalWarpBoundsSpatialSubset | GdalWarpCutlineSpatialSubset | None = None
    targetSRS: str | None = None
    sourceSRS: str | None = None
    srcAlpha: bool | None = None
    dstAlpha: bool | None = None
    multithreaded: bool = True
    copyMetadata: bool = True


@dataclass
class GdalWarpRecipe:
    warpOptions: GdalWarpOptions
    gdalOptions: GdalOptions


@dataclass
class GdalTranslateRecipe:
    gdalOptions: GdalOptions


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

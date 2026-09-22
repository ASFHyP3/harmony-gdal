# git from harmony_gdal_adapter import gdal_adapter
# from conftest import make_options
# from harmony_gdal_adapter import gdal as hgdal
from pathlib import Path

from harmony_gdal_adapter.build_recipes import build_recipe,RecipeInputOptions,GdalWarpRecipe,GdalTranslateRecipe
from harmony_gdal_adapter.gdal import execute_recipe
import filecmp
import pytest
# from tests.conftest import test_data_dir
from dataclasses import asdict

# make_gcov_granule(test_data_dir)

def make_options(**overrides) -> RecipeInputOptions:
    defaults = dict(
        collection_shortname  = "foobar",
        output_type = "GTiff",
        output_filename = "data/output.tif",
        variable_path = "//science/LSAR/GCOV/grids/frequencyA/HHHH"
    )
    defaults.update(overrides)
    return RecipeInputOptions(**defaults)

def test_variable_subset(data_dir,gcov_granule):
    output = data_dir / "output_variable_extracton.tif"
    overrides = {"output_filename": str(output),
                 "input_filename": str(gcov_granule)}
    options = make_options(**overrides)
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalTranslateRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output,data_dir/"variable_extraction_example.tif")


def test_spatial_subset(data_dir,gcov_granule):
    output = data_dir / "output_spatial_subset.tif"
    overrides = {"output_filename": str(output),
                 "input_filename": str(gcov_granule),
                 "spatial_extents": "POLYGON((-151.470826 0.009020,-151.417068 0.009020,-151.417069 0.036081,-151.470827 0.036078,-151.470826 0.009020))"}
    options = make_options(**overrides)
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output,data_dir/"spatial_subset_example.tif")

def test_reproject(data_dir,gcov_granule):
    output = data_dir / "output_spatial_subset.tif"
    overrides = {"output_filename": str(output),
                 "input_filename": str(gcov_granule),
                 "target_srs": "EPSG:3412"}
    options = make_options(**overrides)
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output,data_dir/"reproject_example.tif")

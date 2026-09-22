# git from harmony_gdal_adapter import gdal_adapter
# from conftest import make_options
# from harmony_gdal_adapter import gdal as hgdal
from harmony_gdal_adapter.build_recipes import build_recipe,RecipeInputOptions,GdalWarpRecipe,GdalTranslateRecipe
from harmony_gdal_adapter.gdal import execute_recipe
import filecmp
import pytest
# from tests.conftest import test_data_dir

# make_gcov_granule(test_data_dir)

def make_options(**overrides) -> RecipeInputOptions:
    defaults = dict(
        collection_shortname  = "foobar",
        input_filename = "data/mock_gcov_granule.h5",
        output_type = "GTiff",
        output_filename = "data/output.tif",
        variable_path = "//science/LSAR/GCOV/grids/frequencyA/HHHH"
    )
    defaults.update(overrides)
    return RecipeInputOptions(**defaults)

def test_variable_subset(data_dir):
    overrides = {"output_filename": data_dir / "output_variable_extracton.tif"}
    options = make_options(**overrides)
    recipe = build_recipe(options)
    print('testing var subset')
    assert isinstance(recipe.inner, GdalTranslateRecipe)
    # assert filecmp()


# def test_dummy(data_dir):
#     overrides = {"output_filename": data_dir / "output_variable_extracton.tif"}
#     print(make_options(**overrides))

#build recipe tests
# def test_build_options_variable_subset():
#     overrides = {"output_filename": test_data_dir / "output_variable_extracton.tif"}
#     options = make_options(**overrides)
#     recipe = build_recipe(options)
#     assert isinstance(recipe.inner,GdalTranslateRecipe)
    # execute_recipe(recipe)
    # assert filecmp.cmp(test_data_dir/"variable_extraction_example.tif",
    #                    test_data_dir / 'output_variable_extracton.tif')
    # print('test')

# def test_build_options_spatial_subset():
#     overrides = {"spatial_extents": 'POLYGON((...))'}
#     options = make_options(**overrides)
#     recipe = build_recipe(options)
#     assert isinstance(recipe.inner,GdalWarpRecipe)
#
# def test_build_options_reproject():
#     overrides = {"target_srs": "EPSG:3011"}
#     options = make_options(**overrides)
#     recipe = build_recipe(options)
#     assert isinstance(recipe.inner,GdalWarpRecipe)
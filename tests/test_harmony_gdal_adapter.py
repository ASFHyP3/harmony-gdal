import filecmp
from functools import partial

from harmony_gdal_adapter.build_recipes import GdalTranslateRecipe, GdalWarpRecipe, RecipeInputOptions, build_recipe
from harmony_gdal_adapter.gdal import execute_recipe


def make_recipe_input_options(**kwargs) -> RecipeInputOptions:
    defaults = RecipeInputOptions(
        collection_shortname='foobar',
        output_type='GTiff',
        output_filename='data/output.tif',
        variable_path='//science/LSAR/GCOV/grids/frequencyA/HHHH',
        **kwargs,
    )

    return defaults


def test_variable_subset(data_dir, gcov_granule):
    output = data_dir / 'output_variable_extracton.tif'
    options = make_recipe_input_options(output_filename=str(output), input_filename=str(gcov_granule))
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalTranslateRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output, data_dir / 'variable_extraction_example.tif')


def test_spatial_subset(data_dir, gcov_granule):
    output = data_dir / 'output_spatial_subset.tif'
    options = make_recipe_input_options(
        output_filename=str(output),
        input_filename=str(gcov_granule),
        spatial_extents_wkt='POLYGON((-151.470826 0.009020,-151.417068 0.009020,-151.417069 0.036081,-151.470827 0.036078,-151.470826 0.009020))',
    )
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output, data_dir / 'spatial_subset_example.tif')


def test_reproject(data_dir, gcov_granule):
    output = data_dir / 'output_reproject.tif'
    options = make_recipe_input_options(
        output_filename=str(output), input_filename=str(gcov_granule), target_srs='EPSG:3412'
    )
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output, data_dir / 'reproject_example.tif')

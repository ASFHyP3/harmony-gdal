import filecmp

import pytest

from harmony_gdal_adapter.build_recipes import GdalTranslateRecipe, GdalWarpRecipe, RecipeInputOptions, build_recipe
from harmony_gdal_adapter.gdal import execute_recipe


def make_recipe_input_options(**kwargs) -> RecipeInputOptions:
    defaults = RecipeInputOptions(
        collection_shortname='foobar',
        output_type='GTiff',
        variable_path='/science/LSAR/GCOV/grids/frequencyA/HHHH',
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


def test_spatial_subset_wkt(data_dir, gcov_granule):
    output = data_dir / 'output_spatial_subset_wkt.tif'
    overrides = {
        'output_filename': str(output),
        'input_filename': str(gcov_granule),
        'spatial_extents_wkt': 'POLYGON((-151.470826 0.009020,-151.417068 0.009020,-151.417069 0.036081,-151.470827 0.036078,-151.470826 0.009020))',
    }
    options = make_recipe_input_options(**overrides)
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output, data_dir / 'spatial_subset_wkt_example.tif')


def test_spatial_subset_wkt_clipped(data_dir, gcov_granule):
    output = data_dir / 'output_spatial_subset_wkt_clipped.tif'
    overrides = {
        'output_filename': str(output),
        'input_filename': str(gcov_granule),
        'spatial_extents_wkt': 'POLYGON((-151.417068 0.036081, -151.417068 -0.976081,-152.470826 -0.976081,-152.470827 0.036081,-151.417068 0.036081))',
    }
    options = make_recipe_input_options(**overrides)
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output, data_dir / 'spatial_subset_wkt_clipped_example.tif')


def test_spatial_subset_bounding_box(data_dir, gcov_granule):
    output = data_dir / 'output_spatial_subset_bounding_box.tif'
    overrides = {
        'output_filename': str(output),
        'input_filename': str(gcov_granule),
        'spatial_extents_bounding_box': [-151.470826, 0.009020, -151.417068, 0.036081],
    }
    options = make_recipe_input_options(**overrides)
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output, data_dir / 'spatial_subset_bounding_box_example.tif')


def test_spatial_subset_bounding_box_clipped(data_dir, gcov_granule):
    output = data_dir / 'output_spatial_subset_bounding_box_clipped.tif'
    overrides = {
        'output_filename': str(output),
        'input_filename': str(gcov_granule),
        'spatial_extents_bounding_box': [-152.470826, -0.976081, -151.417068, 0.036081],
    }
    options = make_recipe_input_options(**overrides)
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output, data_dir / 'spatial_subset_bounding_box_clipped_example.tif')


def test_spatial_subset_out_of_bounds(data_dir, gcov_granule):
    output = data_dir / 'output_spatial_subset_bounding_box_clipped.tif'
    overrides = {
        'output_filename': str(output),
        'input_filename': str(gcov_granule),
        'spatial_extents_bounding_box': [1.0, 1.0, 1.1, 1.1],
    }
    options = make_recipe_input_options(**overrides)
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    with pytest.raises(AssertionError, match='Subset polygon and source polygon do not overlap'):
        execute_recipe(recipe)


def test_reproject(data_dir, gcov_granule):
    output = data_dir / 'output_reproject.tif'
    overrides = {'output_filename': str(output), 'input_filename': str(gcov_granule), 'target_srs': 'EPSG:3412'}
    options = make_recipe_input_options(**overrides)
    recipe = build_recipe(options)
    assert isinstance(recipe.inner, GdalWarpRecipe)
    execute_recipe(recipe)
    assert filecmp.cmp(output, data_dir / 'reproject_example.tif')

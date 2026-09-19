# from harmony_gdal_adapter import gdal as hgdal
import pytest

from harmony_gdal_adapter.build_recipes import build_recipe,RecipeInputOptions

# @pytest.fixture
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


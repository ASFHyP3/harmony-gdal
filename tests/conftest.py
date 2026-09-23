from pathlib import Path

import pytest

from mock.gcov import mock_gcov_granule


# Testing note: the mock_gcov_granules.h5 in tests/data/ is generated outside this script.
# It is similar to nisar-py. Additionally, a "variable_extraction.tif", "spatial_subset.tif"
# and "reproject.tif" need to be generated and places into that folder.


@pytest.fixture
def data_dir():
    return Path(__file__).parent / 'data'


@pytest.fixture
def gcov_granule(tmp_path) -> Path:
    """ "Generate mock GCOV file for every test.
    Can be manually generated with: pytest --basetemp=./.pytest_tmp"""
    return mock_gcov_granule(tmp_path)


GCOV_GRIDS = '//science/LSAR/GCOV/grids'


@pytest.fixture
def gcov_subdataset(gcov_granule):
    """Return GDAL path of to raster.
    Usage in a test: gcov_subdataset('frequencyA', 'HHHH')
    """

    def _path(frequency: str, variable: str) -> str:
        return f'HDF5:{gcov_granule}:{GCOV_GRIDS}/{frequency}/{variable}'

    return _path

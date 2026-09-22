import numpy as np
import pytest
from osgeo import gdal

from mock.gcov import DEFAULT_EPSG, NCOLS, NROWS, VALUE_SCALE


@pytest.mark.parametrize(
    'frequency, variable',
    [('frequencyA', 'HHHH'), ('frequencyB', 'VVVV'), ('frequencyB', 'VHVH')],
)
def test_raster_has_crs_and_shape(gcov_subdataset, frequency, variable):
    ds = gdal.Open(gcov_subdataset(frequency, variable))
    assert ds.GetSpatialRef().GetAuthorityCode(None) == str(DEFAULT_EPSG)
    assert (ds.RasterXSize, ds.RasterYSize) == (NCOLS, NROWS)

def test_hhhh_values_encode_column(gcov_subdataset):
    arr = gdal.Open(gcov_subdataset('frequencyA', 'HHHH')).ReadAsArray()
    expected_row = np.arange(NCOLS) * VALUE_SCALE
    np.testing.assert_array_equal(arr, np.broadcast_to(expected_row, arr.shape))

def test_vvvv_values_encode_row(gcov_subdataset):
    arr = gdal.Open(gcov_subdataset('frequencyB', 'VVVV')).ReadAsArray()
    expected_row = np.arange(NCOLS) * VALUE_SCALE
    np.testing.assert_array_equal(arr, np.broadcast_to(expected_row, arr.shape))

def test_vhvh_values_encode_row(gcov_subdataset):
    arr = gdal.Open(gcov_subdataset('frequencyB', 'VHVH')).ReadAsArray()
    expected_col = (NROWS - np.arange(NROWS)) * VALUE_SCALE
    np.testing.assert_array_equal(arr, np.broadcast_to(expected_col[:, None], arr.shape))

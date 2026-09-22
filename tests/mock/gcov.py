from osgeo import osr
from xarray import DataArray, DataTree, Dataset, Variable

osr.UseExceptions()

NCOLS, NROWS = 100, 50
STEP_SIZE = 100.0   # pixel size in meters; sets the geotransform
VALUE_SCALE = 100   # stretches stored values only; unrelated to geography
DEFAULT_EPSG = 32606  # UTM zone 6N

def _coordinate_variable(dim: str, values: list, is_x: bool) -> Variable:
    """"Create the coordinate variable emulating real GCOV product"""
    attrs = {
        'standard_name': 'projection_x_coordinate' if is_x else 'projection_y_coordinate',
        'long_name': f'{"X" if is_x else "Y"} coordinates of projection',
        'units': 'meters',
        'pixel_coordinate_convention': 'center',
    }
    return Variable(dims=dim, data=values, attrs=attrs).astype('float64')


def _projection_variable(epsg: int) -> DataArray:
    """Create projection as variable emulating real GCOV product"""
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    ogc_projection = srs.GetAttrValue('PROJECTION')  # e.g. 'Transverse_Mercator', 'Polar_Stereographic'

    attrs = {
        'epsg_code': str(epsg),
        'spatial_ref': srs.ExportToWkt(),
        'ellipsoid': 'WGS84',
        'semi_major_axis': srs.GetSemiMajor(),
        'inverse_flattening': srs.GetInvFlattening(),
        'false_easting': srs.GetProjParm(osr.SRS_PP_FALSE_EASTING, 0.0),
        'false_northing': srs.GetProjParm(osr.SRS_PP_FALSE_NORTHING, 0.0),
    }
    if ogc_projection == 'Polar_Stereographic':
        attrs.update(
            grid_mapping_name='polar_stereographic',
            latitude_of_projection_origin=srs.GetProjParm(osr.SRS_PP_LATITUDE_OF_ORIGIN, 90.0),
            longitude_of_projection_origin=srs.GetProjParm(osr.SRS_PP_CENTRAL_MERIDIAN, 0.0),
            standard_parallel=srs.GetProjParm(osr.SRS_PP_LATITUDE_OF_ORIGIN, 70.0),
            straight_vertical_longitude_from_pole=srs.GetProjParm(osr.SRS_PP_CENTRAL_MERIDIAN, -45.0),
        )
    elif ogc_projection == 'Transverse_Mercator':
        attrs.update(
            grid_mapping_name='transverse_mercator',
            utm_zone_number=srs.GetUTMZone(),
            longitude_of_central_meridian=srs.GetProjParm(osr.SRS_PP_CENTRAL_MERIDIAN, 0.0),
            latitude_of_projection_origin=srs.GetProjParm(osr.SRS_PP_LATITUDE_OF_ORIGIN, 0.0),
            scale_factor_at_central_meridian=srs.GetProjParm(osr.SRS_PP_SCALE_FACTOR, 0.9996),
        )
    else:
        # Fallback
        attrs['grid_mapping_name'] = (ogc_projection or 'unknown').lower()

    return DataArray(epsg, attrs=attrs)


def mock_gcov_granule(tmp_path, epsg: int = 32606):
    """Creates a mock gcov .h5 granule with sufficient data to be tested by harmony-gdal tool.

    frequencyA contains a 100x50 HHHH raster with pixel values = column index * value_scale

    frequencyB contains a 100x50 VVVV raster with pixel values = column index * value_scale,
    and a VHVH raster with pixel values = row index * value_scale (see value_scale below).
    """
    step_size = 100.0
    value_scale = 100
    x_coordinates = [ii * step_size for ii in range(0, 100, 1)]
    y_coordinates = [ii * step_size for ii in range(50, 0, -1)]
    x_values = [ii * value_scale for ii in range(0, 100, 1)]
    y_values = [ii * value_scale for ii in range(50, 0, -1)]

    dt = DataTree.from_dict(
        {
            '/': Dataset(attrs={'mission_name': 'NISAR'}),
            '/science/LSAR/GCOV/grids/frequencyA': Dataset(
                {
                    'HHHH': Variable(
                        dims=('yCoordinates', 'xCoordinates'),
                        data=[[x for x in x_values] for y in y_values],
                        attrs={'grid_mapping': 'projection'},
                    ).astype('float32'),
                    'mask': Variable(
                        dims=('yCoordinates', 'xCoordinates'),
                        data=[[0.0 if x == y else 1.0 for x in x_coordinates] for y in y_coordinates],
                        attrs={'grid_mapping': 'projection'},
                    ).astype('float32'),
                    'xCoordinates': _coordinate_variable('xCoordinates', x_coordinates, is_x=True),
                    'yCoordinates': _coordinate_variable('yCoordinates', y_coordinates, is_x=False),
                    'xCoordinateSpacing': step_size,
                    'yCoordinateSpacing': -step_size,
                    'listOfPolarizations': (
                        'phony_dim_0',
                        ['HH'],
                    ),
                    'projection': _projection_variable(epsg),
                },
            ),
            '/science/LSAR/GCOV/grids/frequencyB': Dataset(
                {
                    'VVVV': Variable(
                        dims=('yCoordinates', 'xCoordinates'),
                        data=[[x for x in x_values] for y in y_values],
                        attrs={'grid_mapping': 'projection'},
                    ).astype('float32'),
                    'VHVH': Variable(
                        dims=('yCoordinates', 'xCoordinates'),
                        data=[[y for x in x_values] for y in y_values],
                        attrs={'grid_mapping': 'projection'},
                    ).astype('float32'),
                    'mask': Variable(
                        dims=('yCoordinates', 'xCoordinates'),
                        data=[[255.0 if x == y else 2.0 for x in x_coordinates] for y in y_coordinates],
                        attrs={'grid_mapping': 'projection'},
                    ).astype('float32'),
                    'xCoordinates': _coordinate_variable('xCoordinates', x_coordinates, is_x=True),
                    'yCoordinates': _coordinate_variable('yCoordinates', y_coordinates, is_x=False),
                    'xCoordinateSpacing': step_size,
                    'yCoordinateSpacing': -step_size,
                    'listOfPolarizations': (
                        'phony_dim_0',
                        ['VV', 'VH'],
                    ),
                    'projection': _projection_variable(epsg),
                },
            ),
            '/science/LSAR/identification': Dataset(
                {
                    'productType': 'GCOV',
                    'missionId': 'NISAR',
                    'absoluteOrbitNumber': 123,
                    'lookDirection': 'Left',
                    'orbitPassDirection': 'Ascending',
                    'zeroDopplerStartTime': '2026-01-01T00:00:00.000000000',
                    'zeroDopplerEndTime': '2026-01-01T00:00:01.000000000',
                    'boundingPolygon': 'POLYGON ((0.0 0.0, 0.0 .05, 0.1 .05, 0.1 0.0, 0.0 0.0))',
                    'listOfFrequencies': ['A', 'B'],
                    'diagnosticModeFlag': 0,
                    'plannedDatatakeId': 'dtid_2025359150444',
                    'plannedObservationId': 'oid_2025359150500',
                    'isUrgentObservation': 'False',
                    'isJointObservation': 'False',
                },
            ),
        },
    )

    output_path = tmp_path / 'mock_gcov_granule.h5'
    dt.to_netcdf(
        filepath=output_path,
        engine='h5netcdf',
        encoding={
            '/science/LSAR/GCOV/grids/frequencyA': {
                'HHHH': {'chunksizes': (50, 50), 'compression': 'gzip'},
            },
            '/science/LSAR/GCOV/grids/frequencyB': {
                'VVVV': {'chunksizes': (50, 50), 'compression': 'gzip'},
                'VHVH': {'chunksizes': (50, 50), 'compression': 'gzip'},
            },
        },
    )
    return output_path
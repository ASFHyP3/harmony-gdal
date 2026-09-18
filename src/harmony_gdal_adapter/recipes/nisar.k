import schema

collection_shortname = option("collection_shortname", 'str', False, None)
input_filename = option("input_filename", 'str')
target_srs = option("target_srs", 'str', False, None)
spatial_extents = option("spatial_extents", 'str', False, None)
output_type = option("output_type", 'str')
output_filename = option("output_filename", 'str')
variable_path = option("variable_path", 'str')

_gdal_options = schema.GdalOptions {
    input_options = schema.GdalInputOptions {
        driver = "HDF5"
        dataset_path = variable_path
        input_file_path = input_filename
    }
    output_options = schema.GdalOutputOptions {
        output_file_path = output_filename
    }
}

recipe: schema.Recipe = schema.Recipe {
    if target_srs or spatial_extents:
        inner = schema.GdalWarpRecipe {
            warp_options = schema.GdalWarpOptions {
                dst_alpha = True
                if spatial_extents:
                    spatial_subset = schema.GdalWarpCutlineSpatialSubset {
                        cutline_wkt = spatial_extents
                        cutline_srs = "WGS84"
                        crop_to_cutline = True
                    }
                if target_srs:
                    target_srs = target_srs
            }
            gdal_options = _gdal_options
        }
    else:
        inner = schema.GdalTranslateRecipe {
            gdal_options: _gdal_options
        }
}

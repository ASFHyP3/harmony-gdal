import schema

collection_shortname = option("collection_shortname", 'str', False) or None
input_filename = option("input_filename", 'str')
target_srs = option("target_srs", 'str', False) or None
spatial_extents_wkt = option("spatial_extents_wkt", 'str', False) or None
spatial_extents_bounding_box = option("spatial_extents_bounding_box", 'list', False) or None
output_type = option("output_type", 'str')
output_filename = option("output_filename", 'str')
variable_path = option("variable_path", 'str')

assert not (spatial_extents_wkt is not None and spatial_extents_bounding_box is not None), "Invalid input options: spatial extents wkt string and bounding box specified"

_gdal_options = schema.GdalOptions {
    input_options = schema.GdalInputOptions {
        driver = "HDF5"
        dataset_path = variable_path
        input_file_path = input_filename
    }
    output_options = schema.GdalOutputOptions {
        output_type = output_type
        output_file_path = output_filename
    }
}

recipe: schema.Recipe = schema.Recipe {
    if target_srs or spatial_extents_wkt or spatial_extents_bounding_box:
        inner = schema.GdalWarpRecipe {
            warp_options = schema.GdalWarpOptions {
                dst_alpha = None
                if spatial_extents_wkt:
                    spatial_subset = schema.GdalWarpCutlineSpatialSubset {
                        cutline_wkt = spatial_extents_wkt
                        cutline_srs = "EPSG:4326"
                        crop_to_cutline = True
                    }
                elif spatial_extents_bounding_box:
                    spatial_subset = schema.GdalWarpBoundsSpatialSubset {
                        output_bounds = spatial_extents_bounding_box
                        output_bounds_srs = "EPSG:4326"
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

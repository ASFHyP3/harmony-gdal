import schema

collectionShortname = option("collection_shortname", 'str', False, None)
inputFilename = option("input_filename", 'str')
targetSRS = option("target_srs", 'str', False, None)
spatialExtents = option("spatial_extents", 'str', False, None)
outputType = option("output_type", 'str')
outputFilename = option("output_filename", 'str')
variablePath = option("variable_path", 'str')

_gdal_options = schema.GdalOptions {
    inputOptions = schema.GdalInputOptions {
        driver = "HDF5"
        dataset_path = variablePath
        filename = inputFilename
    }
    outputOptions = schema.GdalOutputOptions {
        outputType = schema.GdalGTiffOutput
        outputName = outputFilename
    }
}

recipe: schema.Recipe = schema.Recipe {
    if targetSRS or spatialExtents:
        inner = schema.GdalWarpRecipe {
            warp_options = schema.GdalWarpOptions {
                dstAlpha = True
                if spatialExtents:
                    spatial_subset = schema.GdalWarpCutlineSpatialSubset {
                        cutline_wkt = spatialExtents
                        cutline_srs = "WGS84"
                        crop_to_cutline = True
                    }
                if targetSRS:
                    target_srs = targetSRS
            }
            gdal_options = _gdal_options
        }
    else:
        inner = schema.GdalTranslateRecipe {
            gdal_options: _gdal_options
        }
}

import schema

collectionShortname = option("collection_shortname", 'str', False, None)
inputFilename = option("input_filename", 'str')
targetSRS = option("target_srs", 'str', False, None)
spatialExtents = option("spatial_extents", 'str', False, None)
outputType = option("output_type", 'str')
outputFilename = option("output_filename", 'str')
variablePath = option("variable_path", 'str')

_gdalOptions = schema.GdalOptions {
    inputOptions = schema.GdalInputOptions {
        driver = "HDF5"
        datasetPath = variablePath
        inputFilePath = inputFilename
    }
    outputOptions = schema.GdalOutputOptions {
        outputType = schema.GdalGTiffOutput
        outputFilePath = outputFilename
    }
}

recipe: schema.Recipe = schema.Recipe {
    if targetSRS or spatialExtents:
        inner = schema.GdalWarpRecipe {
            warpOptions = schema.GdalWarpOptions {
                dstAlpha = True
                if spatialExtents:
                    spatialSubset = schema.GdalWarpCutlineSpatialSubset {
                        cutlineWKT = spatialExtents
                        cutlineSRS = "WGS84"
                        cropToCutline = True
                    }
                if targetSRS:
                    targetSRS = targetSRS
            }
            gdalOptions = _gdalOptions
        }
    else:
        inner = schema.GdalTranslateRecipe {
            gdalOptions: _gdalOptions
        }
}

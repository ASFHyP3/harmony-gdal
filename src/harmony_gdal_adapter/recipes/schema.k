schema Recipe:
    inner: GdalWarpRecipe | GdalTranslateRecipe

schema GdalWarpRecipe:
    warp_options: GdalWarpOptions
    gdal_options: GdalOptions

schema GdalTranslateRecipe:
    gdal_options: GdalOptions

schema GdalOptions:
    inputOptions: GdalInputOptions
    outputOptions: GdalOutputOptions
    configOptions?: dict

schema GdalInputOptions:
    driver: "HDF5" | "NETCDF"
    virtual_filesystem?: "/vsicurl/" | "/vsis3/"
    dataset_path: str
    filename: str

schema GdalOutputOptions:
    outputType: GdalOutput
    outputDirectory: str = ""
    outputName: str = "output"

    check:
        outputType in [GdalGTiffOutput, GdalCogOutput]

schema GdalOutput:
    name: str
    extension: str

GdalGTiffOutput = GdalOutput {
    name: "GTiff"
    extension: ".tif"
}

GdalCogOutput = GdalOutput {
    name: "COG"
    extension: ".tif"
}

schema GdalWarpOptions:
    spatial_subset?: GdalWarpBoundsSpatialSubset | GdalWarpCutlineSpatialSubset
    target_srs?: str
    source_srs?: str
    srcAlpha?: bool
    dstAlpha?: bool
    multithreaded: bool = True
    copyMetadata: bool = True

schema GdalWarpBoundsSpatialSubset:
    outputBounds: (float, float, float, float)
    outputBoundsSRS?: str

schema GdalWarpCutlineSpatialSubset:
    cutline_wkt: str
    cutline_srs?: str
    cutline_layer?: str
    cutline_where?: str
    cutline_sql?: str
    cutline_blend?: int
    crop_to_cutline: bool = True


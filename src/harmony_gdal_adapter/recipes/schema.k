schema Recipe:
    inner: GdalWarpRecipe | GdalTranslateRecipe

schema GdalWarpRecipe:
    warpOptions: GdalWarpOptions
    gdalOptions: GdalOptions

schema GdalTranslateRecipe:
    gdalOptions: GdalOptions

schema GdalOptions:
    """GdalOptions specifies the options which are common to both GDAL Warp and Translate operations.

    attributes
    ----------
    inputOptions : GdalInputOptions
        The input file path, type, and whether to use a virtual filesystem.
    outputOptions : GdalOutputOptions
        The output file path and type.
    configOptions : dict, optional, default is None
        The GDAL configuration options to use.
    """
    inputOptions: GdalInputOptions
    outputOptions: GdalOutputOptions
    configOptions?: dict

schema GdalInputOptions:
    """GdalInputOptions specifies the options which are used to template the srcDS input string.

    attributes
    ----------
    driver : str
        The raster driver to use for loading the input dataset. Must be a valid GDAL raster driver. See [here](https://gdal.org/en/stable/drivers/raster/index.html) for a list of available GDAL raster drivers.
    virtualFilesystem : str, optional, default is None
        The virtual filesystem to use for loading the input dataset. Must be a valid GDAL virtual filesystem name. See [here](https://gdal.org/en/stable/user/virtual_file_systems.html) for a list of available GDAL virtual filesystems.
    datasetPath : str
        The dataset, or variable to extract from the input file.
    inputFilePath : str
        The input file path to perform operations on.
    """
    driver: "HDF5" | "NETCDF"
    virtualFilesystem?: "vsicurl" | "vsis3"
    datasetPath: str
    inputFilePath: str

schema GdalOutputOptions:
    """GdalOutputOptions specifies the output options to use.

    Attributes
    ----------
    outputType : GdalOutput
        The output format to use. This option sets the extension the file uses and the raster driver which is used for output.
    outputFilePath : str, default is "output"
        The file path to output to.
    """
    outputType: GdalOutput
    outputFilePath: str = "output"

    check:
        outputType in [GdalGTiffOutput, GdalCogOutput]

schema GdalOutput:
    """GdalOutput specifies the output file type to use.

    Attributes
    ----------
    name : str
        The name of the raster driver to use for output. See [here](https://gdal.org/en/stable/drivers/raster/index.html) for a list of available GDAL raster drivers.
        This maps to the format option in osgeo.gdal.WarpOptions or osgeo.gdal.TranslateOptions.
    extension: str
        The desired file extension.
    """
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
    """GdalWarpOptions specifies the GDAL options specific to Warp operations.

    Attributes
    ----------
    spatialSubset : GdalWarpBoundsSpatialSubset | GdalWarpCutlineSpatialSubset, optional, default is None
        Specify a spatial subsetting operation to perform. If none is specified no spatial subsetting operation will be performed.
    targetSRS : str, optional, default is None
        Specify a spatial reference system to reproject into. Must be an accepted GDAL SRS string. If none is specified no reprojection operation will be performed.
        Maps directly to GDAL's targetSRS option in osgeo.gdal.WarpOptions.
    sourceSRS : str, optional, default is None
        Specify the spatial reference system which the input dataset is referenced in. If none is specified GDAL will utilize the spatial reference system supplied by the input dataset.
        Maps directly to GDAL's sourceSRS option in osgeo.gdal.WarpOptions.
    srcAlpha : bool, optional, default is None
        Whether to force the input dataset to be considered as an alpha band. If none is specified GDAL will attempt to automatically determine if the input dataset contains an alpha band.
        Maps directly to GDAL's srcAlpha option in osgeo.gdal.WarpOptions.
    dstAlpha : bool, optional, default is None
        Whether to force the creation of an output alpha band. If none is specified GDAL will attempt to automatically determine if the creation of an output alpha band is suitable.
        Maps directly to GDAL's dstAlpha option in osgeo.gdal.WarpOptions.
    multithreaded : bool, default is True
        Whether to use multithreaded compute and I/O operations.
        Maps directly to GDAL's multithreaded option in osgeo.gdal.WarpOptions.
    copyMetadata : bool, default is True
        Whether to copy the source metadata.
        Maps directly to GDAL's copyMetadata option in osgeo.gdal.WarpOptions.
    """
    spatialSubset?: GdalWarpBoundsSpatialSubset | GdalWarpCutlineSpatialSubset
    targetSRS?: str
    sourceSRS?: str
    srcAlpha?: bool
    dstAlpha?: bool
    multithreaded: bool = True
    copyMetadata: bool = True

schema GdalWarpBoundsSpatialSubset:
    """GdalWarpBoundsSpatialSubset allows performing spatial subsetting with a pair of points defining a bounding box.

    Attributes
    ----------
    output_bounds : (float, float, float, float)
        The bounding box to spatially subset to.
        Maps directly to GDAL's outputBounds option in osgeo.gdal.WarpOptions.
    output_bounds_srs : str, default is WGS84
        The bounding box to spatially subset to. Must be an accepted GDAL SRS string.
        Maps directly to GDAL's outputBoundsSRS option in osgeo.gdal.WarpOptions.
    """
    outputBounds: (float, float, float, float)
    outputBoundsSRS: str = "WGS84"

schema GdalWarpCutlineSpatialSubset:
    """GdalWarpCutlineSpatialSubset allows performing spatial subsetting with a WKT string utilizing GDAL Warp's cutline options.

    Attributes
    ----------
    cutline_wkt : str
        The cutline WKT string to operate on. Must be a WKT POLYGON or MULTIPOLYGON string.
        Maps directly to GDAL's cutlineWKT option in osgeo.gdal.WarpOptions.
    cutline_srs : str, default is WGS84
        The spatial reference system of the cutline WKT string. Must be an accepted GDAL SRS string.
        Maps directly to GDAL's cutlineSRS option in osgeo.gdal.WarpOptions.
    cutline_where : str, optional, default is None
        The cutline WHERE clause.
        Maps directly to GDAL's cutlineWHERE option in osgeo.gdal.WarpOptions.
    cutline_sql : str, optional, default is None
        The cutline SQL statement.
        Maps directly to GDAL's cutlineSQL option in osgeo.gdal.WarpOptions.
    cutline_blend : int, optional, default is None
        The cutline blend distance in pixels.
        Maps directly to GDAL's cutlineBlend option in osgeo.gdal.WarpOptions.
    crop_to_cutline : bool, default is True
        Wether to use the cutline extent for output bounds.
        Maps directly to GDALts cropToCutline option isn osgeo.gdal.WarpOptions.
    """
    cutlineWKT: str
    cutlineWHERE: str
    cutlineSQL: str
    cutlineBlend: int
    cutlineSRS: str = "WGS84"
    cropToCutline: bool = True


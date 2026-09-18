# Harmony GDAL Adapter

## Developer setup

```
mamba env create -f environment.yml
mamba activate harmony-gdal-adapter
pytest
```

## Harmony GDAL Adapter CLI

You can use the local development testing cli by running `hga` in the harmony-gdal-adapter environment.

For example to perform a simple dataset extraction to geotiff:
```bash
hga --input-filename "NISAR_L2_PR_GCOV_005_149_A_024_4005_DHDH_A_20251120T123755_20251120T123830_X05009_N_F_J_001.h5" --collection-shortname "foobar" --output-type GTiff --output-filename output.tif --variable-path "//science/LSAR/GCOV/grids/frequencyB/HHHH"
```

To perform a spatial subsetting operation:
```bash
hga --input-filename NISAR_L2_PR_GCOV_030_106_A_027_4005_DHDH_A_20260913T130434_20260913T130510_P05023_N_F_J_001.h5 --collection-shortname "foobar" --output-type GTiff --output-filename "output_cropped.tif" --variable-path "//science/LSAR/GCOV/grids/frequencyB/HHHH" --spatial-extents "POLYGON((-125.1989 49.2151,-125.1461 49.2151,-125.1461 49.2583,-125.1989 49.2583,-125.1989 49.2151))"
```

To perform a reprojection operation:
```
hga --input-filename NISAR_L2_PR_GCOV_030_106_A_027_4005_DHDH_A_20260913T130434_20260913T130510_P05023_N_F_J_001.h5 --collection-shortname "foobar" --output-type GTiff --output-filename "output.tif" --variable-path "//science/LSAR/GCOV/grids/frequencyB/HHHH" --target-srs EPSG:32602
```

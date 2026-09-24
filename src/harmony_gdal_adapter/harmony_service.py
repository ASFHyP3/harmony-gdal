"""Harmony service for the GDAL Adapter."""

import argparse
import tempfile
from pathlib import Path
from typing import Tuple

import harmony_service_lib
import pystac
from harmony_service_lib.exceptions import HarmonyException
from harmony_service_lib.util import download, stage

from harmony_gdal_adapter.build_recipes import RecipeInputOptions, build_recipe
from harmony_gdal_adapter.gdal import execute_recipe


def bbox_to_wkt(bbox: tuple[float, float, float, float]) -> str:
    return f'POLYGON(({bbox[0]} {bbox[1]}, {bbox[2]} {bbox[3]}, {bbox[0]}, {bbox[1]}'


class HarmonyAdapter(harmony_service_lib.BaseHarmonyAdapter):
    """Harmony adapter for harmony-gdal-adapter."""

    def process_item(self, item: pystac.Item, source: harmony_service_lib.message.Source) -> pystac.Item:
        """Processes a single input item.

        Parameters
        ----------
        item : pystac.Item
            the item that should be processed
        source : harmony_service_lib.message.Source
            the input source defining the variables, if any, to subset from the item

        Returns:
        -------
        pystac.Item
            a STAC catalog whose metadata and assets describe the service output
        """
        self.logger.info(f'Processing item {item.id}')

        granule_url = _get_asset_url(item, '.h5')

        with tempfile.TemporaryDirectory() as temp_dir:
            granule_filename = download(
                url=granule_url,
                destination_dir=temp_dir,
                logger=self.logger,
                access_token=self.message.accessToken,
            )

            output_path = Path(f'{temp_dir}/output.tif')

            input_options = RecipeInputOptions(
                input_filename=granule_filename,
                output_filename=str(output_path),
                collection_shortname=str(source.process('shortName')),
                output_type='GTiff',
                variable_path=source.process('variables')[0],
                target_srs=self.message.format.process('CRS')
                if self.message.format and self.message.format.crs
                else None,
                spatial_extents=bbox_to_wkt(self.message.subset.process('bbox'))
                if self.message.subset and self.message.subset.bbox
                else None,
            )

            try:
                recipe = build_recipe(input_options)
                execute_recipe(recipe)
            except Exception as e:
                raise HarmonyException(str(e))

            url = stage(
                local_filename=str(output_path),
                remote_filename=output_path.name,
                mime='image/tiff',
                location=self.message.stagingLocation,
                logger=self.logger,
            )

            result = item.clone()
            result.assets = {
                'rgb_browse': pystac.Asset(url, title=output_path.name, media_type='image/tiff', roles=['visual'])
            }

        return result


def _get_asset_url(item: pystac.Item, suffix: str) -> str:
    try:
        return next(asset.href for asset in item.assets.values() if asset.href.endswith(suffix))
    except StopIteration:
        raise HarmonyException(f'No {suffix} asset found for {item.id}')


def main() -> None:
    """Run the Harmony service."""
    parser = argparse.ArgumentParser(description='Run the Harmony service')
    harmony_service_lib.setup_cli(parser)
    args = parser.parse_args()
    harmony_service_lib.run_cli(parser, args, HarmonyAdapter)


if __name__ == '__main__':
    main()

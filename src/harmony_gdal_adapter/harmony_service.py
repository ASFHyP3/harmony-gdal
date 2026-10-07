"""Harmony service for the GDAL Adapter. This is the entrypoint for the Harmony CLI."""

import argparse
import tempfile
from dataclasses import dataclass
from os import getenv
from pathlib import Path
from pprint import pformat
from urllib.parse import urljoin, urlparse

import harmony_service_lib
import pystac
import requests
from harmony_service_lib.exceptions import HarmonyException
from harmony_service_lib.util import download, generate_output_filename, stage
from requests.exceptions import RequestException

from harmony_gdal_adapter.build_recipes import RecipeInputOptions, build_recipe
from harmony_gdal_adapter.exceptions import (
    EmptyOutputError,
    HGANoRetryException,
    MissingVariableError,
    UnsupportedFileFormatError,
)
from harmony_gdal_adapter.gdal import execute_recipe


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
        if (requested_type := self.message.format.process('mime')) != 'image/tiff':
            raise UnsupportedFileFormatError(requested_type)

        self.logger.info(f'Processing item {item.id}')

        granule_url = _get_asset_url(item, '.h5')

        with tempfile.TemporaryDirectory() as temp_dir:
            granule_filename = download(
                url=granule_url,
                destination_dir=temp_dir,
                logger=self.logger,
                access_token=self.message.accessToken,
            )

            granule_name = Path(urlparse(granule_url).path).stem

            result = item.clone()
            result.assets = {}

            variables = source.process('variables') or _get_mmt_variables(
                str(source.process('collection')), self.message.accessToken
            )

            for variable in variables:
                self.logger.info(f'Processing variable: {pformat(variable)}')
                input_options = RecipeInputOptions(
                    input_filename=granule_filename,
                    output_filename='',
                    collection_shortname=str(source.process('shortName')),
                    output_type=requested_type,
                    variable_path=variable.fullPath,
                )

                if (format := self.message.format) and (srs := format.srs) and (epsg := srs.epsg):
                    input_options.target_srs = epsg

                if (subset := self.message.subset) and (bounding_box := subset.bbox):
                    input_options.spatial_extents_bounding_box = bounding_box

                output_filename = generate_output_filename(
                    filename=granule_name,
                    variable_subset=[variable.fullPath],
                    ext='.tif',
                    is_subsetted=input_options.spatial_extents_bounding_box != None,
                )
                input_options.output_filename = f'{temp_dir}/{output_filename}'

                self.logger.info(f'Building recipe with the following Input Options: {pformat(input_options)}')
                recipe = build_recipe(input_options)
                self.logger.info(f'Running the following GDAL Recipe: {pformat(recipe)}')

                try:
                    execute_recipe(recipe)
                except RuntimeError as e:
                    raise HGANoRetryException(str(e))
                except MissingVariableError:
                    self.logger.info('Variable is not present in source dataset, skipping.')
                    continue

                url = stage(
                    local_filename=input_options.output_filename,
                    remote_filename=output_filename,
                    mime='image/tiff',
                    location=self.message.stagingLocation,
                    logger=self.logger,
                )

                result.assets[variable.fullPath] = pystac.Asset(
                    url, title=output_filename, media_type=requested_type, roles=['data']
                )

            if result.assets == {}:
                raise EmptyOutputError

        return result


def _get_asset_url(item: pystac.Item, suffix: str) -> str:
    try:
        return next(asset.href for asset in item.assets.values() if asset.href.endswith(suffix))
    except StopIteration:
        raise HarmonyException(f'No {suffix} asset found for {item.id}')


@dataclass
class _MMTVariable:
    fullPath: str


def _get_mmt_variables(collection_concept_id: str, access_token: str) -> list[_MMTVariable]:
    cmr_url = getenv('CMR_ENDPOINT') or 'https://cmr.earthdata.nasa.gov'
    url = urljoin(cmr_url, '/search/variables.umm_json')

    params = {
        'keyword': collection_concept_id,
        'page_size': '2000',
    }

    header_params = {'Authorization': f'Bearer {access_token}', 'Client-Id': 'harmony-gdal-adapter'}

    try:
        response = requests.get(url, params=params, headers=header_params)
        response.raise_for_status()
    except RequestException as e:
        raise HarmonyException(f'Error while fetching variables from CMR: {e!s}')

    return [
        _MMTVariable(fullPath=variable['umm']['Name'])
        for variable in response.json()['items']
        if collection_concept_id in variable['meta']['associations']['collections']
    ]


def main() -> None:
    """Run the Harmony service."""
    parser = argparse.ArgumentParser(description='Run the Harmony service')
    harmony_service_lib.setup_cli(parser)
    args = parser.parse_args()
    harmony_service_lib.run_cli(parser, args, HarmonyAdapter)


if __name__ == '__main__':
    main()

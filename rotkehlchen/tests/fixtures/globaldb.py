from typing import List, Optional

import pytest

from rotkehlchen.chain.ethereum.typing import CustomEthereumToken
from rotkehlchen.constants.resolver import ETHEREUM_DIRECTIVE
from rotkehlchen.globaldb import GlobalDBHandler
from rotkehlchen.typing import AssetType


@pytest.fixture(name='custom_ethereum_tokens')
def fixture_custom_ethereum_tokens() -> Optional[List[CustomEthereumToken]]:
    return None


def create_globaldb(
        data_directory,
        custom_ethereum_tokens,
) -> GlobalDBHandler:
    # Since this is a singleton and we want it initialized everytime the fixture
    # is called make sure its instance is always starting from scratch
    GlobalDBHandler._GlobalDBHandler__instance = None  # type: ignore

    handler = GlobalDBHandler(data_dir=data_directory)
    if custom_ethereum_tokens is not None:
        for entry in custom_ethereum_tokens:
            asset_id = ETHEREUM_DIRECTIVE + entry.address
            handler.add_asset(asset_id=asset_id, asset_type=AssetType.ETHEREUM_TOKEN, data=entry)

    return handler


@pytest.fixture(name='globaldb')
def fixture_globaldb(
        data_dir,
        custom_ethereum_tokens,
):
    return create_globaldb(data_directory=data_dir, custom_ethereum_tokens=custom_ethereum_tokens)

from epigen import epigen

from epigen_config import EpiGenConfig
from epigen_config import EpiGenManifest

import pytest


@pytest.mark.order(3)
class TestCodeGenerator:

    @pytest.mark.parametrize('dirpath,modules', [
        (
            'tests/data/samples/codegen/subfolder/subfolder_module',
            [
                'tests/data/samples/codegen/subfolder/subfolder_module'
            ]
        ),
        (
            'tests/data/samples/codegen',
            [
                'tests/data/samples/codegen',
                'tests/data/samples/codegen/subfolder/subfolder_module'
            ]
        ),
    ])
    def test_sequence(self, tmpdir: str, dirpath: str, modules: list):

        config = EpiGenConfig()
        config.dir_input = dirpath
        config.dir_output = tmpdir
        config.dir_output_build = tmpdir
        config.ignore_list = []
        config.debug = True
        config.backup = False

        manifest = EpiGenManifest()
        manifest.modules = modules

        epigen(config, manifest)

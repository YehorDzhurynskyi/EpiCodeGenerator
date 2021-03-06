from epigen import epigen

from epigen.config import EpiGenConfig
from epigen.config import EpiGenManifest

import pytest
import os


@pytest.mark.order(3)
class TestCodeGenerator:

    @pytest.mark.parametrize('dirpath,modules', [
        (
            'tests/data/samples/codegen',
            [
                'tests/data/samples/codegen',
                os.path.abspath('tests/data/samples/codegen/subfolder/subfolder')
            ]
        ),
        (
            os.path.abspath('tests/data/samples/codegen/subfolder/subfolder'),
            [
                'tests/data/samples/codegen/subfolder/subfolder'
            ]
        ),
        (
            'tests/data/samples/codegen/subfolder/subfolder',
            [
                'tests/data/samples/codegen/subfolder/subfolder'
            ]
        ),
        (
            os.path.abspath('tests/data/samples/codegen/subfolder/subfolder'),
            [
                os.path.abspath('tests/data/samples/codegen/subfolder/subfolder')
            ]
        ),
        (
            'tests/data/samples/codegen/subfolder/subfolder',
            [
                os.path.abspath('tests/data/samples/codegen/subfolder/subfolder')
            ]
        ),
        (
            'tests/data/samples/codegen',
            [
                'tests/data/samples/codegen',
                'tests/data/samples/codegen/subfolder/subfolder'
            ]
        ),
        (
            os.path.abspath('tests/data/samples/codegen'),
            [
                'tests/data/samples/codegen',
                'tests/data/samples/codegen/subfolder/subfolder'
            ]
        ),
        (
            os.path.abspath('tests/data/samples/codegen'),
            [
                'tests/data/samples/codegen',
                os.path.abspath('tests/data/samples/codegen/subfolder/subfolder')
            ]
        ),
    ])
    def test_sequence(self, tmpdir: str, dirpath: str, modules: list):

        for iteration in range(4):

            config = EpiGenConfig(dirpath, tmpdir, tmpdir)
            config.ignore_list = []
            config.debug = False
            config.backup = False
            config.caching = iteration not in [0, 1]

            manifest = EpiGenManifest(**{'modules': modules})

            epigen.epigen(config, manifest)

            for root, _, files in os.walk(tmpdir):

                for f in filter(lambda f: f.endswith('h') or f.endswith('hxx') or f.endswith('cpp') or f.endswith('cxx'), files):

                    abspath = os.path.join(os.path.relpath(root, tmpdir), f)
                    abspath = os.path.normpath(abspath)
                    abspath = os.path.join(tmpdir, abspath)
                    abspath = os.path.abspath(abspath)

                    relpath = os.path.relpath(abspath, tmpdir)
                    relpath = os.path.normpath(relpath)

                    abspath_exp = os.path.join(config.dir_input, relpath)
                    filename = os.path.splitext(abspath_exp)[0]
                    ext = os.path.splitext(abspath_exp)[1]
                    abspath_exp = f'{filename}.ref{ext}'

                    with open(abspath_exp, 'r') as expected_f:
                        content_exp = expected_f.read()

                    with open(abspath, 'r') as f:
                        content = f.read()

                    assert content == content_exp, f'Checking {abspath} (len={len(content)} == len-exp={len(content_exp)})'

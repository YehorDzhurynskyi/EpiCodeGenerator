from epigen import epigen

from epigen.config import EpiGenConfig
from epigen.config import EpiGenManifest

import argparse


if __name__ == "__main__":

    class ExtendAction(argparse.Action):

        def __call__(self, parser, namespace, values, option_string=None):

            items = getattr(namespace, self.dest) or []
            items.extend(values)

            setattr(namespace, self.dest, items)

    argparser = argparse.ArgumentParser()
    argparser.register('action', 'extend', ExtendAction)

    grp_required = argparser.add_argument_group('required')
    grp_optional = argparser.add_argument_group('optional')

    grp_required.add_argument(
        '-i',
        '--dir-input',
        type=str,
        required=True
    )

    grp_optional.add_argument(
        '-m',
        '--manifest',
        type=str
    )

    grp_optional.add_argument(
        '-o',
        '--dir-output',
        type=str
    )

    grp_optional.add_argument(
        '--dir-output-build',
        type=str
    )

    grp_optional.add_argument(
        '--debug',
        action='store_true'
    )

    grp_optional.add_argument(
        '--backup',
        action='store_true'
    )

    grp_optional.add_argument(
        '--no-caching',
        action='store_true'
    )

    grp_optional.add_argument(
        '--ignore-list',
        action="extend",
        nargs="+",
        type=str,
        default=[]
    )

    grp_optional.add_argument(
        '--print-dependencies',
        action='store_true'
    )

    grp_optional.add_argument(
        '--print-outputs',
        action='store_true'
    )

    args = argparser.parse_args()

    dir_output = args.dir_output if args.dir_output is not None else args.dir_input
    dir_output_build = args.dir_output_build if args.dir_output_build is not None else dir_output

    config = EpiGenConfig(args.dir_input, dir_output, dir_output_build)
    config.ignore_list = args.ignore_list
    config.debug = args.debug
    config.backup = args.backup
    config.caching = args.no_caching is None or not args.no_caching

    if args.print_dependencies:

        dependencies = epigen.epigen_dependencies(config)
        print(';'.join(dependencies).replace('\\', '/'))

        exit(0)

    if args.print_outputs:

        outputs = epigen.epigen_outputs(config)
        print(';'.join(outputs).replace('\\', '/'))

        exit(0)

    with open(args.manifest) as manifest_file:

        import json

        manifest_json = json.load(manifest_file)
        assert isinstance(manifest_json, dict)

        manifest = EpiGenManifest(**manifest_json)

    epigen.epigen(config, manifest)

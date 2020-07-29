import argparse
import json


if __name__ == '__main__':

    class ExtendAction(argparse.Action):

        def __call__(self, parser, namespace, values, option_string=None):

            items = getattr(namespace, self.dest) or []
            items.extend(values)

            setattr(namespace, self.dest, items)

    argparser = argparse.ArgumentParser()
    argparser.register('action', 'extend', ExtendAction)

    argparser.add_argument(
        '-o',
        '--dir-output',
        type=str,
        required=True
    )

    argparser.add_argument(
        '--name',
        type=str,
        default='epigen-manifest.json'
    )

    argparser.add_argument(
        '--modules',
        action="extend",
        nargs="+",
        type=str,
        default=[]
    )

    manifest = dict()

    args = argparser.parse_args()
    manifest['modules'] = args.modules

    with open(f'{args.dir_output}/{args.name}', 'w') as f:
        json.dump(manifest, f, indent=4)

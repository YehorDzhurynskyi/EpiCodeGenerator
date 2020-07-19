import os
import logging
import argparse
import shutil
import fnmatch

from epi_code_generator.tokenizer import Tokenizer
from epi_code_generator.inheritance_tree import InheritanceTree
from epi_code_generator.inheritance_tree import InheritanceError
from epi_code_generator.idlparser.idlparser import IDLParser
from epi_code_generator.code_generator.code_generator import CodeGenerator
from epi_code_generator.code_generator.code_generator import CodeGenerationError


logger = logging.getLogger()

def print_dependencies(args):

    depds = []
    for root, _, files in os.walk(args.input_dir):

        for file in filter(lambda f: f.endswith('epi'), files):

            relpath = os.path.join(os.path.relpath(root, args.input_dir), file)
            if any(fnmatch.fnmatch(relpath, p) for p in args.ignore):
                continue

            depds.append(os.path.join(root, relpath))

    print(';'.join(depds).replace('\\', '/'))

def print_outputs(args, output_dir):

    outputs = []
    for root, _, files in os.walk(args.input_dir):

        for file in filter(lambda f: f.endswith('epi'), files):

            relpath = os.path.join(os.path.relpath(root, args.input_dir), file)
            if any(fnmatch.fnmatch(relpath, p) for p in args.ignore):
                continue

            path = os.path.join(output_dir, relpath)
            basename = os.path.splitext(path)[0]
            outputs += [f'{basename}.{ext}' for ext in ['cpp', 'cxx', 'h', 'hxx']]

    print(';'.join(outputs).replace('\\', '/'))

def ignore_on_copy(dirname, files):

    filtered = []
    for f in files:

        p = os.path.join(dirname, f)
        if any(fnmatch.fnmatch(p, i) for i in args.ignore):
            filtered.append(f)

    return filtered

def init_logger(log_level: int):

    logger.setLevel(log_level)

    formatter = logging.Formatter('[%(levelname)5s] %(message)s')

    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.INFO)
    stderr_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('epi_code_generator.log', mode='w')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(stderr_handler)
    logger.addHandler(file_handler)

if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    grp_required = argparser.add_argument_group('required')
    grp_optional = argparser.add_argument_group('optional')

    grp_required.add_argument(
        '-i',
        '--input-dir',
        type=str,
        required=True,
        help='TODO: fill'
    )

    grp_optional.add_argument(
        '-o',
        '--output-dir',
        type=str,
        help='TODO: fill'
    )

    grp_optional.add_argument(
        '--output-dir-cxx-hxx',
        type=str,
        help='TODO: fill'
    )

    grp_optional.add_argument(
        '--debug',
        action='store_true',
        help='TODO: fill'
    )

    grp_optional.add_argument(
        '--nobackup',
        action='store_true',
        help='TODO: fill'
    )

    grp_optional.add_argument(
        '--ignore',
        action="extend",
        nargs="+",
        type=str,
        help='TODO: fill',
        default=[]
    )

    grp_optional.add_argument(
        '--print-dependencies',
        action='store_true',
        help='TODO: fill'
    )

    grp_optional.add_argument(
        '--print-outputs',
        action='store_true',
        help='TODO: fill'
    )

    args = argparser.parse_args()

    output_dir = args.output_dir if args.output_dir is not None else args.input_dir
    output_dir_cxx_hxx = args.output_dir_cxx_hxx if args.output_dir_cxx_hxx is not None else output_dir

    if args.print_dependencies:

        print_dependencies(args)
        exit(0)

    if args.print_outputs:

        print_outputs(args, output_dir)
        exit(0)

    os.makedirs(output_dir, exist_ok=True)

    if args.debug:

        init_logger(logging.DEBUG)
        logger.info(f'Debug mode enabled')

    else:
        init_logger(logging.INFO)

    logger.info(f'Input Dir: {args.input_dir}')
    logger.info(f'Output Dir: {output_dir}')
    logger.info(f'Output CXX HXX Dir: {output_dir_cxx_hxx}')
    logger.info(f'Ignore-list: {";".join(args.ignore)}')

    if not args.nobackup:

        from tempfile import TemporaryDirectory
        from tempfile import gettempdir
        from uuid import uuid1

        backupdir = f'{gettempdir()}/EpiCodeGenerator-{uuid1()}-backup'
        logger.info(f'Backup <input dir> into {backupdir}')
        shutil.copytree(args.input_dir, backupdir, ignore=ignore_on_copy)

    registry_global = {}
    for root, _, files in os.walk(args.input_dir):

        for file in filter(lambda f: f.endswith('epi'), files):

            relpath = os.path.join(os.path.relpath(root, args.input_dir), file)
            abspath = os.path.join(root, file)

            if any(fnmatch.fnmatch(relpath, p) for p in args.ignore):
                logger.info(f'Ignoring: {relpath}')
                continue

            logger.info(f'Parsing: {relpath}')

            tokenizer = Tokenizer(abspath, relpath)
            tokens = tokenizer.tokenize()

            for t in tokens:
                logger.debug(str(t))

            parser = IDLParser(tokens)
            registry_local, errors_syntax = parser.parse()

            for e in errors_syntax:
                logger.error(str(e))

            if len(errors_syntax) != 0:
                exit(-1)

            registry_intersection = registry_global.keys() & registry_local.keys()
            if len(registry_intersection) == 0:
                registry_global = { **registry_global, **registry_local }
            else:

                for v in registry_intersection:
                    logging.error(f'{v} is already defined in {registry_global[v].token.filepath}')

                exit(-1)

    try:
        inheritance_tree = InheritanceTree(registry_global)
    except InheritanceError as e:

        logger.error(str(e))
        exit(-1)

    code_generator = CodeGenerator(args.input_dir, output_dir, output_dir_cxx_hxx)
    for sym in registry_global.values():

        logger.info(f'Generating code for: {sym.token.filepath}')

        try:
            code_generator.code_generate(sym, sym.token.filepath)
        except CodeGenerationError as e:

            logger.error(str(e))
            exit(-1)

    code_generator.dump()

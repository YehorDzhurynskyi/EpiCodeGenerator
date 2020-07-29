from epigen.tokenizer import Tokenizer

from epigen.idlparser import idlparser_base as idl
from epigen.linker import linker as ln
from epigen.code_generator import code_generator as cgen

from epigen.config import EpiGenConfig
from epigen.config import EpiGenManifest

import os
import logging
import shutil
import fnmatch


logger = logging.getLogger()


def epigen_dependencies(config: EpiGenConfig) -> list:

    dependencies = []
    for root, _, files in os.walk(config.dir_input):

        for epifile in filter(lambda f: f.endswith('epi'), files):

            relpath = os.path.join(os.path.relpath(root, config.dir_input), epifile)
            relpath = os.path.normpath(relpath)
            if any(fnmatch.fnmatch(relpath, p) for p in config.ignore_list):

                logger.debug(f'Ignoring: `{relpath}`')
                continue

            abspath = os.path.join(config.dir_input, relpath)
            abspath = os.path.abspath(abspath)
            dependencies.append(abspath)

    return dependencies


def epigen_outputs(config: EpiGenConfig) -> list:

    outputs = []
    for root, _, files in os.walk(config.dir_input):

        for epifile in filter(lambda f: f.endswith('epi'), files):

            relpath = os.path.join(os.path.relpath(root, config.dir_input), epifile)
            relpath = os.path.normpath(relpath)
            if any(fnmatch.fnmatch(relpath, p) for p in config.ignore_list):

                logger.debug(f'Ignoring: `{relpath}`')
                continue

            path_output = os.path.join(config.dir_output, relpath)
            basename_output = os.path.splitext(path_output)[0]
            outputs += [f'{basename_output}.{ext}' for ext in ['h', 'cpp']]

            path_output_build = os.path.join(config.dir_output_build, relpath)
            basename_output_build = os.path.splitext(path_output_build)[0]
            outputs += [f'{basename_output_build}.{ext}' for ext in ['hxx','cxx']]

    return outputs


def _ignore_on_copy(dirname, files):

    filtered = []
    for f in files:

        p = os.path.join(dirname, f)
        if any(fnmatch.fnmatch(p, i) for i in config.ignore_list):
            filtered.append(f)

    return filtered


def _init_logger(log_level: int, outdir: str):

    logger.setLevel(log_level)

    formatter = logging.Formatter('[%(levelname)5s] %(message)s')

    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.INFO)
    stderr_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(os.path.join(outdir, 'epigen.log'), mode='w')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(stderr_handler)
    logger.addHandler(file_handler)


def epigen(config: EpiGenConfig, manifest: EpiGenManifest):

    os.makedirs(config.dir_output, exist_ok=True)
    os.makedirs(config.dir_output_build, exist_ok=True)

    if config.debug:

        _init_logger(logging.DEBUG, config.dir_output_build)
        logger.info(f'Debug mode enabled')

    else:
        _init_logger(logging.INFO, config.dir_output_build)

    logger.info(f'Input Dir: {config.dir_input}')
    logger.info(f'Output Dir: {config.dir_output}')
    logger.info(f'Output CXX HXX Dir: {config.dir_output_build}')
    logger.info(f'Ignore-list: {";".join(config.ignore_list)}')
    logger.debug(f'Caching is enabled: {config.caching}')
    logger.debug(f'Modules: {";".join(manifest.modules)}')

    if config.backup:

        from tempfile import TemporaryDirectory
        from tempfile import gettempdir
        from uuid import uuid1

        backupdir = f'{gettempdir()}/EpiCodeGenerator-{uuid1()}-backup'
        logger.info(f'Backup <input dir> into {backupdir}')
        shutil.copytree(config.dir_input, backupdir, ignore=_ignore_on_copy)

    linker = ln.Linker()

    modules = manifest.modules[:]

    def modulepath_dir_input(p: str) -> str:

        p = os.path.relpath(p, config.dir_input)
        p = os.path.join(os.path.basename(config.dir_input), p)
        p = os.path.normpath(p)

        return p

    modules = [modulepath_dir_input(m) for m in modules]
    modules.sort(reverse=True)
    for abspath in epigen_dependencies(config):

        relpath = os.path.relpath(abspath, config.dir_input)
        relpath = os.path.normpath(relpath)

        relpath_dir_input = os.path.join(os.path.basename(config.dir_input), relpath)

        module = next((m for m in modules if m in relpath_dir_input), None)
        if module is None:

            logger.fatal(f"Error while defining a module for `{relpath_dir_input}`")
            exit(-1)

        modulepath = os.path.relpath(relpath_dir_input, module)
        modulepath = os.path.normpath(modulepath)
        modulepath = os.path.join(os.path.basename(module), modulepath)

        logger.info(f'Parsing: `{modulepath}` (`{relpath_dir_input}`)')

        tokenizer = Tokenizer(abspath, relpath, modulepath)
        tokens = tokenizer.tokenize()

        for t in tokens:
            logger.debug(str(t))

        parser = idl.IDLParser(tokens)
        registry_local, errors_syntax = parser.parse()

        for e in errors_syntax:

            logger.error(str(e))
            exit(-1)

        linker.register(registry_local)

    errors_linkage = linker.link()

    for e in errors_linkage:

        logger.error(str(e))
        exit(-1)

    symbols = list(linker.registry.values())
    codegen = cgen.CodeGenerator(symbols, config)
    errors_codegen = codegen.code_generate()

    for e in errors_codegen:

        logger.error(str(e))
        exit(-1)

    codegen.dump()

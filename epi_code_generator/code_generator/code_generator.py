from epi_code_generator.symbol import EpiSymbol
from epi_code_generator.symbol import EpiClass

from epi_code_generator.code_generator import code_generator_emitter as emmiter
from epi_code_generator.code_generator import code_generator_emitter as emmiter
from epi_code_generator.code_generator import code_generator_emitter as emmiter
from epi_code_generator.code_generator import code_generator_emitter as emmiter
from epi_code_generator.code_generator import code_generator_emitter as emmiter
from epi_code_generator.code_generator import code_generator_emitter as emmiter

import os
import pickle
import hashlib
from enum import Enum, auto


class CodeGenerationErrorCode(Enum):

    CorruptedFile = auto()
    CorruptedAnchor = auto()


class CodeGenerationError(Exception):

    __CODE_GENERATION_ERROR_MSGS = {
        CodeGenerationErrorCode.CorruptedFile: 'File corrupted',
        CodeGenerationErrorCode.CorruptedAnchor: 'Anchor corrupted'
    }

    def __init__(self, basename, err_code, tip = ''):

        self.__basename = basename
        self.__err_code = err_code
        self.__err_message = CodeGenerationError.__CODE_GENERATION_ERROR_MSGS[err_code]
        self.__tip = tip

    def __str__(self):

        s = f'Code Generation error {self.__basename}: {self.__err_message}'
        if len(self.__tip) != 0:
            s = f'{s} ({self.__tip})'

        return s

    @property
    def err_code(self):
        return self.__err_code


class CodeGenerator:

    def __init__(self, symbols: list, dir_input: str, dir_output: str, dir_output_build: str):

        self.__symbols = symbols
        self.__dir_input = dir_input
        self.__dir_output = dir_output
        self.__dir_output_build = dir_output_build

        self.__codegen_erros = []

        self.__cache_files_generated = {}
        self.__cache_files_storebuff = {}

        if os.path.exists(f'{self.__dir_output_build}/epigen_cache.bin'):

            with open(f'{self.__dir_output_build}/epigen_cache.bin', 'rb') as f:
                self.__cache_files_generated = pickle.load(f)

    def dump(self):

        for path, content in self.__cache_files_storebuff.items():

            with open(path, 'w') as f:
                f.write(content)

            self.__cache_files_generated[path] = hashlib.md5(content.encode()).hexdigest()

        with open(f'{self.__dir_output_build}/epigen_cache.bin', 'wb') as f:
            pickle.dump(self.__cache_files_generated, f)

    def _content_load(self, basename: str, ext: str) -> str:

        filepath = self._filepath_of(basename, ext)
        if filepath not in self.__cache_files_storebuff:

            with open(filepath, 'r') as f:

                content = f.read()
                self.__cache_files_storebuff[filepath] = content

        content = self.__cache_files_storebuff[filepath]

        return content

    def _content_store(self, content: str, basename: str, ext: str):

        filepath = self._filepath_of(basename, ext)
        self.__cache_files_storebuff[filepath] = content

    def _lookup(self, needle: str, basename: str, ext: str) -> int:
        return self._content_load(basename, ext).find(needle)

    def _filepath_of(self, basename: str, ext: str) -> str:

        assert ext == 'h' or ext == 'cpp' or ext == 'hxx' or ext == 'cxx' or ext == 'epi'

        outdirs = {
            'cxx': self.__dir_output_build,
            'hxx': self.__dir_output_build,
            'cpp': self.__dir_output,
            'h': self.__dir_output,
            'epi': self.__dir_input
        }

        outdir = outdirs[ext]

        return f'{os.path.join(outdir, basename)}.{ext}'


    def _is_dirty(self, basename: str, ext: str):

        filepath = self._filepath_of(basename, ext)

        if not os.path.exists(filepath):
            return True

        if filepath not in self.__cache_files_generated:
            return True

        checksum = self.__cache_files_generated[filepath]
        if self._file_checksum(filepath) != checksum:
            return True

        epifilepath = f'{os.path.join(self.__dir_input, basename)}.epi'
        assert os.path.exists(epifilepath)

        if epifilepath not in self.__cache_files_generated:
            return True

        epichecksum = self.__cache_files_generated[epifilepath]
        if self._file_checksum(epifilepath) != epichecksum:
            return True

        return False

    def _file_checksum(self, filename: str):

        with open(filename, 'r') as f:

            content = f.read()
            digest = hashlib.md5(content.encode()).hexdigest()

        return digest

    def _code_generate_inject(self,
                              inj: str,
                              basename: str,
                              ext: str,
                              before: str = None,
                              after: str = None):

        content = self._content_load(basename, ext)
        if before is None and after is None:
            lbound = len(content)
            rbound = len(content)
        else:
            if before is not None and after is not None:
                lbound = content.find(after) + len(after)
                rbound = content.find(before)
            elif before is not None:
                rbound = content.find(before)
                lbound = rbound
            elif after is not None:
                lbound = content.find(after) + len(after)
                rbound = lbound

        if rbound == -1 or lbound == -1:

            tip = f'Can\'t find `{before if before is not None else after}` anchor'
            raise CodeGenerationError(f'{basename}.{ext}', CodeGenerationErrorCode.CorruptedFile, tip)

        newcontent = content[:lbound] + inj + content[rbound:]
        self._content_store(newcontent, basename, ext)

    def code_generate(self, symbol: EpiSymbol, basename: str) -> list:

        os.makedirs(os.path.dirname(os.path.join(self.__dir_output, basename)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.join(self.__dir_output_build, basename)), exist_ok=True)
        basename = os.path.splitext(basename)[0]

        assert isinstance(symbol, EpiClass)

        if self._is_dirty(basename, 'hxx'):

            with open(self._filepath_of(basename, 'hxx'), 'w') as f:
                f.write(emmiter.emit_sekeleton_file(basename, 'hxx'))

            injection = f'\n{emmiter.emit_class_declaration_hidden(symbol).build()}'
            self._code_generate_inject(injection, basename, 'hxx')

        if self._is_dirty(basename, 'cxx'):

            with open(self._filepath_of(basename, 'cxx'), 'w') as f:
                f.write(emmiter.emit_sekeleton_file(basename, 'cxx'))

            injection = f'{emmiter.emit_class_serialization(symbol).build()}\n'
            self._code_generate_inject(injection, basename, 'cxx', before='EPI_NAMESPACE_END()')

            injection = f'{emmiter.emit_class_meta(symbol).build()}\n'
            self._code_generate_inject(injection, basename, 'cxx', before='EPI_NAMESPACE_END()')

        if self._is_dirty(basename, 'cpp'):

            filepath = self._filepath_of(basename, 'cpp')
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(emmiter.emit_sekeleton_file(basename, 'cpp'))

            # NOTE: fake injection to force cache its content
            self._code_generate_inject('', basename, 'cpp', before='EPI_NAMESPACE_END()')

        if self._is_dirty(basename, 'h'):

            filepath = self._filepath_of(basename, 'h')
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(emmiter.emit_sekeleton_file(basename, 'h'))

            if self._lookup(f'EPI_GENREGION_END({symbol.name})', basename, 'h') == -1:

                if self._lookup(f'EPI_GENREGION_BEGIN({symbol.name})', basename, 'h') != -1:

                    tip = f'`EPI_GENREGION_END({symbol.name})` is absent while corresponding anchor `EPI_GENREGION_BEGIN({symbol.name})` is present'
                    raise CodeGenerationError(f'{basename}.h', CodeGenerationErrorCode.CorruptedAnchor, tip)

                # NOTE: symbol isn't present add it to the end
                injection = f'{emmiter.emit_skeleton_class(symbol).build()}\n'
                self._code_generate_inject(
                    injection,
                    basename,
                    'h',
                    before='EPI_NAMESPACE_END()'
                )

            else:

                if self._lookup(f'EPI_GENREGION_BEGIN({symbol.name})', basename, 'h') == -1:

                    tip = f'`EPI_GENREGION_BEGIN({symbol.name})` is absent while corresponding anchor `EPI_GENREGION_END({symbol.name})` is present'
                    raise CodeGenerationError(f'{basename}.h', CodeGenerationErrorCode.CorruptedAnchor, tip)

                # NOTE: symbol is present add it to the corresponding region
                injection = f'\n{emmiter.emit_class_declaration(symbol).build()}\n'
                self._code_generate_inject(
                    injection,
                    basename,
                    'h',
                    before=f'EPI_GENREGION_END({symbol.name})',
                    after=f'EPI_GENREGION_BEGIN({symbol.name})'
                )

        filepath = self._filepath_of(basename, 'epi')
        self.__cache_files_generated[filepath] = self._file_checksum(filepath)

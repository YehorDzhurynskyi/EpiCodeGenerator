from epigen.symbol import EpiSymbol

from epigen.code_generator import code_generator_emitter as emmiter
from epigen.code_generator import code_generator_builder as bld
from epigen.symbol import EpiClass, EpiEnum

from epigen.config import EpiGenConfig

import os
import pickle
import hashlib
from enum import Enum, auto


class CodeGenerationErrorCode(Enum):

    CorruptedAnchor = auto()


class CodeGenerationError:

    __CODE_GENERATION_ERROR_MSGS = {
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


class CodeGenerationErrorFatal(Exception):
    pass


class CodeGenerator:

    def __init__(self, symbols: list, config: EpiGenConfig):

        self.__symbols = symbols
        self.__config = config

        self.__codegen_erros = []

        self.__cache_files_generated = {}
        self.__cache_files_storebuff = {}

        if self.__config.caching and os.path.exists(f'{self.__config.dir_output_build}/epigen-cache.bin'):

            with open(f'{self.__config.dir_output_build}/epigen-cache.bin', 'rb') as f:
                self.__cache_files_generated = pickle.load(f)

    def dump(self):

        for path, content in self.__cache_files_storebuff.items():

            with open(path, 'w') as f:
                f.write(content)

            if self.__config.caching:
                self.__cache_files_generated[path] = hashlib.md5(content.encode()).hexdigest()

        if self.__config.caching:
            with open(f'{self.__config.dir_output_build}/epigen-cache.bin', 'wb') as f:
                pickle.dump(self.__cache_files_generated, f)

    def _push_error(self, basename: str, err_code: CodeGenerationErrorCode, tip: str = ''):
        self.__codegen_erros.append(CodeGenerationError(basename, err_code, tip))
        raise CodeGenerationErrorFatal()

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
            'cxx': self.__config.dir_output_build,
            'hxx': self.__config.dir_output_build,
            'cpp': self.__config.dir_output,
            'h': self.__config.dir_output,
            'epi': self.__config.dir_input
        }

        return f'{os.path.join(outdirs[ext], basename)}.{ext}'

    def _is_dirty(self, basename: str, ext: str):

        filepath = self._filepath_of(basename, ext)

        if not os.path.exists(filepath):
            return True

        if filepath not in self.__cache_files_generated:
            return True

        checksum = self.__cache_files_generated[filepath]
        if self._file_checksum(filepath) != checksum:
            return True

        epifilepath = f'{os.path.join(self.__config.dir_input, basename)}.epi'
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

    def _inject(self,
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

            if before is not None and content[rbound + len(before):].find(before) != -1:
                tip = f'There is a duplicating anchor: `{before}`'
                self._push_error(f'{basename}.{ext}', CodeGenerationErrorCode.CorruptedAnchor, tip)

            if after is not None and content[lbound + len(after):].find(after) != -1:
                tip = f'There is a duplicating anchor: `{after}`'
                self._push_error(f'{basename}.{ext}', CodeGenerationErrorCode.CorruptedAnchor, tip)

        if rbound == -1 or lbound == -1:

            tip = f'Can\'t find `{before if before is not None else after}` anchor'
            self._push_error(f'{basename}.{ext}', CodeGenerationErrorCode.CorruptedAnchor, tip)

        newcontent = content[:lbound] + inj + content[rbound:]
        self._content_store(newcontent, basename, ext)

    def _inject_symbol(self, symbolname: str, basename: str, ext: str, injection_skeleton: str, injection_content: str):

        assert ext in ['h']

        if self._lookup(f'EPI_GENREGION_END({symbolname})', basename, ext) == -1:

            if self._lookup(f'EPI_GENREGION_BEGIN({symbolname})', basename, ext) != -1:

                tip = f'`EPI_GENREGION_END({symbolname})` is absent while corresponding anchor `EPI_GENREGION_BEGIN({symbolname})` is present'
                self._push_error(f'{basename}.{ext}', CodeGenerationErrorCode.CorruptedAnchor, tip)

            # NOTE: symbol isn't present add it to the end
            self._inject(
                injection_skeleton,
                basename,
                ext,
                before='EPI_NAMESPACE_END()'
            )

        if self._lookup(f'EPI_GENREGION_BEGIN({symbolname})', basename, ext) == -1:

            tip = f'`EPI_GENREGION_BEGIN({symbolname})` is absent'
            self._push_error(f'{basename}.{ext}', CodeGenerationErrorCode.CorruptedAnchor, tip)

        if self._lookup(f'EPI_GENREGION_END({symbolname})', basename, ext) == -1:

            tip = f'`EPI_GENREGION_END({symbolname})` is absent'
            self._push_error(f'{basename}.{ext}', CodeGenerationErrorCode.CorruptedAnchor, tip)

        # NOTE: symbol is present add it to the corresponding region
        self._inject(
            injection_content,
            basename,
            ext,
            before=f'EPI_GENREGION_END({symbolname})',
            after=f'EPI_GENREGION_BEGIN({symbolname})'
        )

    def _code_generate_hxx(self, symbol: EpiSymbol, basename: str, module_basename: str):

        with open(self._filepath_of(basename, 'hxx'), 'w') as f:
            f.write(emmiter.emit_sekeleton_file(module_basename, 'hxx', bld.Builder()).build())

        if isinstance(symbol, EpiClass):
            injection = f'\n{emmiter.emit_class_declaration_hidden(symbol, bld.Builder()).build()}'
            self._inject(injection, basename, 'hxx')

        elif isinstance(symbol, EpiEnum):
            pass

    def _code_generate_cxx(self, symbol: EpiSymbol, basename: str, module_basename: str):

        with open(self._filepath_of(basename, 'cxx'), 'w') as f:
            f.write(emmiter.emit_sekeleton_file(module_basename, 'cxx', bld.Builder()).build())

        if isinstance(symbol, EpiClass):
            injection = f'{emmiter.emit_class_serialization(symbol, bld.Builder()).build()}\n'
            self._inject(injection, basename, 'cxx', before='EPI_NAMESPACE_END()')

            injection = f'{emmiter.emit_class_meta(symbol, bld.Builder()).build()}\n'
            self._inject(injection, basename, 'cxx', before='EPI_NAMESPACE_END()')

        elif isinstance(symbol, EpiEnum):
            pass

    def _code_generate_cpp(self, symbol: EpiSymbol, basename: str, module_basename: str):

        filepath = self._filepath_of(basename, 'cpp')
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(emmiter.emit_sekeleton_file(module_basename, 'cpp', bld.Builder()).build())

        injection = f'\n{emmiter.emit_include_section(module_basename, "cpp", bld.Builder()).nl().build()}'
        self._inject(injection,
                     basename,
                     'cpp',
                     before='EPI_GENREGION_END(include)',
                     after='EPI_GENREGION_BEGIN(include)')

    def _code_generate_h(self, symbol: EpiSymbol, basename: str, module_basename: str):

        filepath = self._filepath_of(basename, 'h')
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(emmiter.emit_sekeleton_file(module_basename, 'h', bld.Builder()).build())

        injection = f'\n{emmiter.emit_include_section(module_basename, "h", bld.Builder()).nl().build()}'
        self._inject(injection,
                     basename,
                     'h',
                     before='EPI_GENREGION_END(include)',
                     after='EPI_GENREGION_BEGIN(include)')

        if isinstance(symbol, EpiClass):

            injection_skeleton = f'{emmiter.emit_skeleton_class(symbol, bld.Builder()).build()}\n'
            injection_content = f'\n{emmiter.emit_class_declaration(symbol, bld.Builder()).build()}\n'
            self._inject_symbol(symbol.name, basename, 'h', injection_skeleton, injection_content)

            for symbol_inner in symbol.inner().values():

                assert isinstance(symbol_inner, EpiEnum)

                builder = bld.Builder()
                builder.tab()

                injection = f'\n{emmiter.emit_enum_declaration(symbol_inner, builder).nl().build()}'
                self._inject(
                    injection,
                    basename,
                    'h',
                    before=f'EPI_GENREGION_END({symbol_inner.fullname})',
                    after=f'EPI_GENREGION_BEGIN({symbol_inner.fullname})'
                )

        elif isinstance(symbol, EpiEnum):

            injection_skeleton = f'{emmiter.emit_skeleton_enum(symbol, symbol.name, bld.Builder()).build()}\n'
            injection_content = f'\n{emmiter.emit_enum_declaration(symbol, bld.Builder()).nl().build()}'
            self._inject_symbol(symbol.name, basename, 'h', injection_skeleton, injection_content)

    def code_generate(self) -> list:

        for symbol in self.__symbols:

            # TODO: move these functions to the Token class
            basename = os.path.splitext(symbol.token.relpath)[0]
            module_basename = os.path.splitext(symbol.token.modulepath)[0]

            # TODO: do the OS-independent file path adoption in a smarter way
            basename = basename.replace('\\', '/')
            module_basename = module_basename.replace('\\', '/')

            os.makedirs(os.path.dirname(os.path.join(self.__config.dir_output, basename)), exist_ok=True)
            os.makedirs(os.path.dirname(os.path.join(self.__config.dir_output_build, basename)), exist_ok=True)

            if self._is_dirty(basename, 'hxx'):
                self._code_generate_hxx(symbol, basename, module_basename)

            if self._is_dirty(basename, 'cxx'):
                self._code_generate_cxx(symbol, basename, module_basename)

            if self._is_dirty(basename, 'cpp'):
                self._code_generate_cpp(symbol, basename, module_basename)

            if self._is_dirty(basename, 'h'):
                self._code_generate_h(symbol, basename, module_basename)

            if self.__config.caching:

                # TODO: move in the other place
                filepath = self._filepath_of(basename, 'epi')
                self.__cache_files_generated[filepath] = self._file_checksum(filepath)

        return self.__codegen_erros

import os
import zlib
import pickle
import hashlib
from enum import Enum, auto

from ..symbol import EpiSymbol
from ..symbol import EpiClass

from .code_generator_emitter import emit_sekeleton_file
from .code_generator_emitter import emit_skeleton_class
from .code_generator_emitter import emit_class_declaration
from .code_generator_emitter import emit_class_declaration_hidden
from .code_generator_emitter import emit_class_serialization
from .code_generator_emitter import emit_class_meta


class CodeGenerationErrorCode(Enum):

    CorruptedFile = auto()
    CorruptedAnchor = auto()


CODE_GENERATION_ERROR_MSGS = {
    CodeGenerationErrorCode.CorruptedFile: 'File corrupted',
    CodeGenerationErrorCode.CorruptedAnchor: 'Anchor corrupted'
}


class CodeGenerationError(Exception):

    def __init__(self, basename, err_code, tip = ''):

        self.basename = basename
        self.err_code = err_code
        self.err_message = CODE_GENERATION_ERROR_MSGS[err_code]
        self.tip = tip

    def __str__(self):

        s = f'Code Generation error {self.basename}: {self.err_message}'
        if len(self.tip) != 0:
            s = f'{s} ({self.tip})'

        return s


class CodeGenerator:

    def __init__(self, input_dir: str, output_dir: str, output_dir_cxx_hxx: str):

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir_cxx_hxx = output_dir_cxx_hxx
        self.generated_files_cache = {}
        self.files_outbuff_cache = {}

        if os.path.exists(f'{output_dir_cxx_hxx}/epigen_cache.bin'):

            with open(f'{output_dir_cxx_hxx}/epigen_cache.bin', 'rb') as f:
                self.generated_files_cache = pickle.load(f)

    def dump(self):

        for path, content in self.files_outbuff_cache.items():

            with open(path, 'w') as f:
                f.write(content)

            self.generated_files_cache[path] = hashlib.md5(content.encode()).hexdigest()

        with open(f'{self.output_dir_cxx_hxx}/epigen_cache.bin', 'wb') as f:
            pickle.dump(self.generated_files_cache, f)

    def _lookup(self, needle: str, basename: str, ext: str) -> int:

        assert ext == 'h' or ext == 'cpp'

        path = f'{os.path.join(self.output_dir, basename)}.{ext}'
        if path not in self.files_outbuff_cache:

            with open(path, 'r') as f:

                content = f.read()
                self.files_outbuff_cache[path] = content

        content = self.files_outbuff_cache[path]

        return content.find(needle)

    def _should_be_regenerated(self, basename: str, ext: str):

        if ext == 'cxx' or ext == 'hxx':
            filename = f'{os.path.join(self.output_dir_cxx_hxx, basename)}.{ext}'
        elif ext == 'cpp' or ext == 'h':
            filename = f'{os.path.join(self.output_dir, basename)}.{ext}'
        else:
            assert False, "Unexpected file extension"

        if not os.path.exists(filename):
            return True

        if filename not in self.generated_files_cache:
            return True

        checksum = self.generated_files_cache[filename]
        if self._calc_file_checksum(filename) != checksum:
            return True

        epifilename = f'{os.path.join(self.input_dir, basename)}.epi'
        assert os.path.exists(epifilename)

        if epifilename not in self.generated_files_cache:
            return True

        epichecksum = self.generated_files_cache[epifilename]
        if self._calc_file_checksum(epifilename) != epichecksum:
            return True

        return False

    def _calc_file_checksum(self, filename: str):

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

        outdir = self.output_dir if ext == 'h' or ext == 'cpp' else self.output_dir_cxx_hxx

        path = f'{os.path.join(outdir, basename)}.{ext}'
        if path not in self.files_outbuff_cache:

            with open(path, 'r') as f:
                content = f.read()

        else:
            content = self.files_outbuff_cache[path]

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

        self.files_outbuff_cache[path] = content[:lbound] + inj + content[rbound:]

    def code_generate(self, symbol: EpiSymbol, basename: str):

        os.makedirs(os.path.dirname(os.path.join(self.output_dir, basename)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.join(self.output_dir_cxx_hxx, basename)), exist_ok=True)
        basename = os.path.splitext(basename)[0]

        assert isinstance(symbol, EpiClass)

        if self._should_be_regenerated(basename, 'hxx'):

            filename = f'{os.path.join(self.output_dir_cxx_hxx, basename)}.hxx'
            with open(filename, 'w') as f:
                f.write(emit_sekeleton_file(basename, 'hxx'))

            injection = f'\n{emit_class_declaration_hidden(symbol).build()}'
            self._code_generate_inject(injection, basename, 'hxx')

        if self._should_be_regenerated(basename, 'cxx'):

            filename = f'{os.path.join(self.output_dir_cxx_hxx, basename)}.cxx'
            with open(filename, 'w') as f:
                f.write(emit_sekeleton_file(basename, 'cxx'))

            injection = f'{emit_class_serialization(symbol).build()}\n'
            self._code_generate_inject(injection, basename, 'cxx', before='EPI_NAMESPACE_END()')

            injection = f'{emit_class_meta(symbol).build()}\n'
            self._code_generate_inject(injection, basename, 'cxx', before='EPI_NAMESPACE_END()')

        if self._should_be_regenerated(basename, 'cpp'):

            filename = f'{os.path.join(self.output_dir, basename)}.cpp'
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write(emit_sekeleton_file(basename, 'cpp'))

            # NOTE: fake injection to force cache its content
            self._code_generate_inject('', basename, 'cpp', before='EPI_NAMESPACE_END()')

        if self._should_be_regenerated(basename, 'h'):

            filename = f'{os.path.join(self.output_dir, basename)}.h'
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write(emit_sekeleton_file(basename, 'h'))

            if self._lookup(f'EPI_GENREGION_END({symbol.name})', basename, 'h') == -1:

                if self._lookup(f'EPI_GENREGION_BEGIN({symbol.name})', basename, 'h') != -1:

                    tip = f'`EPI_GENREGION_END({symbol.name})` is absent while corresponding anchor `EPI_GENREGION_BEGIN({symbol.name})` is present'
                    raise CodeGenerationError(f'{basename}.h', CodeGenerationErrorCode.CorruptedAnchor, tip)

                # NOTE: symbol isn't present add it to the end
                injection = f'{emit_skeleton_class(symbol).build()}\n'
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
                injection = f'\n{emit_class_declaration(symbol).build()}\n'
                self._code_generate_inject(
                    injection,
                    basename,
                    'h',
                    before=f'EPI_GENREGION_END({symbol.name})',
                    after=f'EPI_GENREGION_BEGIN({symbol.name})'
                )

        epifilename = f'{os.path.join(self.input_dir, basename)}.epi'
        with open(epifilename, 'r') as f:
            epicontent = f.read()

        self.generated_files_cache[epifilename] = hashlib.md5(epicontent.encode()).hexdigest()


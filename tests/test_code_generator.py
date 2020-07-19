from epi_code_generator.tokenizer import Tokenizer

from epi_code_generator.idlparser import idlparser_base as idl
from epi_code_generator.linker import linker as ln
from epi_code_generator.code_generator import code_generator as cgen

import pytest


@pytest.mark.order(3)
class TestCodeGenerator:

    @pytest.mark.parametrize('content', [
    ])
    def test_sequence(self, tmpdir: str, content: str):

        linker = ln.Linker()

        path = f'{tmpdir}/test.epi'

        with open(path, 'w') as f:
            f.write(content)

        tokenizer = Tokenizer(path, path)
        tokens = tokenizer.tokenize()

        parser = idl.IDLParser(tokens)
        registry_local, errors_syntax = parser.parse()

        assert len(errors_syntax) == 0

        linker.register(registry_local)

        errors_linkage = linker.link()

        assert len(errors_linkage) == 0

        errors_codegen = []
        code_generator = cgen.CodeGenerator(tmpdir, tmpdir, tmpdir)
        for sym in linker.registry.values():

            errors_codegen_local = code_generator.code_generate(sym, sym.token.filepath)
            errors_codegen.extend(errors_codegen_local)

        assert len(errors_codegen) == 0

        code_generator.dump()


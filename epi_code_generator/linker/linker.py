from epi_code_generator.tokenizer import TokenType

from epi_code_generator.symbol import EpiSymbol
from epi_code_generator.symbol import EpiProperty

from enum import Enum, auto
import zlib


class LinkerErrorCode(Enum):

    DuplicatingSymbol = auto()
    NoSuchSymbol = auto()
    HashCollision = auto()
    IncompleteTypeUsage = auto()


class LinkerError:

    __LINKER_ERROR_MSGS = {
        LinkerErrorCode.DuplicatingSymbol: 'The symbol with such a name has been already defined!',
        LinkerErrorCode.NoSuchSymbol: "The symbol doesn't exists!",
        LinkerErrorCode.HashCollision: 'Hash collision has been occured!',
        LinkerErrorCode.IncompleteTypeUsage: "This incomplete type couldn't be used in this context!"
    }

    def __init__(self, symbol: EpiSymbol, err_code: LinkerErrorCode, tip: str):

        self.__symbol = symbol
        self.__err_code = err_code
        self.__err_message = LinkerError.__LINKER_ERROR_MSGS[err_code]
        self.__tip = tip

    @property
    def err_code(self):
        return self.__err_code

    def __str__(self):

        s = f'Syntax error {self.__symbol.token}: {self.__err_message}'
        if len(self.__tip) != 0:
            s = f'{s} ({self.__tip})'

        return s

    def __repr__(self):
        return f'{repr(self.__err_code)}: {repr(self.__symbol.token)} {self.__tip}'


class Linker:

    def __init__(self):

        self.__registry = {}
        self.__linker_errors = []

    @property
    def registry(self):
        return self.__registry

    def _push_error(self, symbol: EpiSymbol, err_code: LinkerErrorCode, tip: str = ''):
        self.__linker_errors.append(LinkerError(symbol, err_code, tip))

    def register(self, registry: dict):

        def _typeids(symbols: list) -> set:
            return [(s, hex(zlib.crc32(s.name.encode()) & 0xffffffff)) for s in symbols]

        def _validate_duplicates(typeid_pairs: list) -> bool:

            valid = True
            for lhs, rhs in typeid_pairs:

                if lhs[0].name == rhs[0].name:

                    valid = False
                    tip = f'The symbol has been already defined in `{rhs[0].token.filepath}`'
                    self._push_error(lhs[0], LinkerErrorCode.DuplicatingSymbol, tip)

                elif lhs[1] == rhs[1]:

                    valid = False
                    tip = f'Hash collision with `{rhs[0].name}` defined in `{rhs[0].token.filepath}`'
                    self._push_error(lhs[0], LinkerErrorCode.HashCollision, tip)

            return valid

        typeids_local = _typeids(list(registry.values()))
        typeids_local_typeids_local = [(lhs, rhs) for lhs in typeids_local for rhs in typeids_local]

        # NOTE: `typeids_local_typeids_local` is cartesian product A * A,
        # so we need exclude (a0, a0), (a1, a1) and (a0, a1), (a1, a0) pairs
        ii = 0
        typeids_local_len = len(typeids_local)
        for i in range(typeids_local_len):

            del typeids_local_typeids_local[i + ii : typeids_local_len + ii]
            ii += i

        valid = _validate_duplicates(typeids_local_typeids_local)

        typeids_global = _typeids(list(self.__registry.values()))
        typeids_local_typeids_global = [(lhs, rhs) for lhs in typeids_local for rhs in typeids_global]

        valid = _validate_duplicates(typeids_local_typeids_global) and valid

        if valid:
            self.__registry = { **self.__registry, **registry }

    def link(self) -> list:

        from epi_code_generator.linker import linker_inheritance_tree as lntree

        if len(self.__linker_errors) > 0:
            return self.__linker_errors

        inheritance_tree = lntree.InheritanceTree(self.__registry)
        inheritance_tree.build(self)
        inheritance_tree.validate(self)

        for sym in self.__registry.values():

            for p in (p for p in sym.properties if p.tokentype.tokentype == TokenType.Identifier):

                if p.typename_basename() not in self.__registry:

                    tip = f'No such symbol exists: `{p.tokentype.text}`'
                    self._push_error(p, LinkerErrorCode.NoSuchSymbol, tip)

                elif p.typename_basename() == sym.name and not p.is_polymorphic():

                    tip = f'The symbol should be a complete type, but not: `{p.tokentype.text}`'
                    self._push_error(p, LinkerErrorCode.IncompleteTypeUsage, tip)

            for p in (p for p in sym.properties if p.form == EpiProperty.Form.Template):

                for n in p.tokens_nested:

                    if n.tokentype != TokenType.Identifier:
                        continue

                    if n.text == sym.name and not p.is_polymorphic():

                        tip = f'Template argument symbol should be a complete type, but not: `{n.text}`'
                        self._push_error(p, LinkerErrorCode.IncompleteTypeUsage, tip)

                    elif n.text not in self.__registry:

                        tip = f"Template argument symbol doesn't exist: `{n.text}`"
                        self._push_error(p, LinkerErrorCode.NoSuchSymbol, tip)

        return self.__linker_errors

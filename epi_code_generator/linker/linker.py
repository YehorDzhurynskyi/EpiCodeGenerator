from epi_code_generator.tokenizer import TokenType

from epi_code_generator.symbol import EpiSymbol
from epi_code_generator.symbol import EpiProperty

from enum import Enum, auto


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

    def _push_error(self, symbol: EpiSymbol, err_code: LinkerErrorCode, tip: str = ''):
        self.__linker_errors.append(LinkerError(symbol, err_code, tip))

    def register(self, registry: dict):

        intersection = self.__registry.keys() & registry.keys()
        if len(intersection) != 0:

            for v in intersection:

                tip = f'{v} is already defined in {self.__registry[v].token.filepath}'
                self._push_error(registry[v], LinkerErrorCode.DuplicatingSymbol, tip)

        else:
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

                if p.tokentype_basename() not in self.__registry:

                    tip = f'No such symbol exists with a name {p.tokentype.text}'
                    self._push_error(p, LinkerErrorCode.NoSuchSymbol, tip)

                elif p.tokentype_basename() == sym.name and not p.is_polymorphic():

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

from epigen.tokenizer import TokenType

from epigen.symbol import EpiSymbol
from epigen.symbol import EpiClass
from epigen.symbol import EpiProperty
from epigen.symbol import EpiEnum
from epigen.symbol import EpiEnumEntry

from enum import Enum, auto
import zlib


class LinkerErrorCode(Enum):

    DuplicatingSymbol = auto()
    NoSuchSymbol = auto()
    HashCollision = auto()
    IncompleteTypeUsage = auto()
    BadTemplateArgument = auto()
    IncorrectValueAssignment = auto()


class LinkerError:

    __LINKER_ERROR_MSGS = {
        LinkerErrorCode.DuplicatingSymbol: 'The symbol with such a name has been already defined!',
        LinkerErrorCode.NoSuchSymbol: "The symbol doesn't exists!",
        LinkerErrorCode.HashCollision: 'Hash collision has been occured!',
        LinkerErrorCode.IncompleteTypeUsage: "This incomplete type couldn't be used in this context!",
        LinkerErrorCode.BadTemplateArgument: "Provided template argument isn't a `type`",
        LinkerErrorCode.IncorrectValueAssignment: 'Incorrect value assignment'
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
                    tip = f'The symbol has been already defined in `{rhs[0].token.modulepath}`'
                    self._push_error(lhs[0], LinkerErrorCode.DuplicatingSymbol, tip)

                elif lhs[1] == rhs[1]:

                    valid = False
                    tip = f'Hash collision with `{rhs[0].name}` defined in `{rhs[0].token.modulepath}`'
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

        valid_locally = _validate_duplicates(typeids_local_typeids_local)

        typeids_global = _typeids(list(self.__registry.values()))
        typeids_local_typeids_global = [(lhs, rhs) for lhs in typeids_local for rhs in typeids_global]

        if _validate_duplicates(typeids_local_typeids_global) and valid_locally:
            self.__registry = { **self.__registry, **registry }


    def lookup_symbol(self, ref: str, sym_outer: EpiSymbol = None) -> EpiSymbol:

        path = ref.split('::')
        assert len(path) > 1 or (len(path) == 1 and sym_outer is not None)

        if isinstance(sym_outer, EpiClass):
            clss_parent = sym_outer
            while True:

                if path[0] in clss_parent.inner():
                    sym_lookup = clss_parent.inner()[path[0]]
                    break

                if clss_parent.parent is None:
                    sym_lookup = None
                    break

                assert clss_parent.parent in self.__registry
                clss_parent = self.__registry[clss_parent.parent]

        if isinstance(sym_outer, EpiClass) and sym_lookup is not None:
            pass
        elif isinstance(sym_outer, EpiEnum) and next((e for e in sym_outer.entries if e.name == path[0]), None) is not None:
            sym_lookup = next(e for e in sym_outer.entries if e.name == path[0])
        elif path[0] in self.__registry:
            sym_lookup = self.__registry[path[0]]
        else:
            sym_lookup = None

        if sym_lookup is not None:

            for i, pathnode in enumerate(path[1:]):

                if isinstance(sym_lookup, EpiEnum):

                    entry = next((e for e in sym_lookup.entries if pathnode == e.name), None)
                    sym_lookup = entry if i == len(path[1:]) - 1 else None
                    break

                elif isinstance(sym_lookup, EpiClass) and pathnode in sym_lookup.inner():
                    sym_lookup = sym_lookup.inner()[pathnode]

                else:
                    sym_lookup = None
                    break

        return sym_lookup

    def _validate_class_properties(self, clss: EpiClass):

        for p in (p for p in clss.properties if p.tokentype.tokentype == TokenType.Identifier):

            if p.typename_basename() == clss.name and not p.is_polymorphic():

                tip = f'The symbol should be a complete type, but not: `{p.tokentype.text}`'
                self._push_error(p, LinkerErrorCode.IncompleteTypeUsage, tip)

            p.symbol = self.lookup_symbol(p.typename_basename(), clss)
            if p.symbol is None:

                tip = f'No such symbol exists: `{ p.typename_basename() }`'
                self._push_error(p, LinkerErrorCode.NoSuchSymbol, tip)

            if p.value_is_assigned() and p.tokenvalue.tokentype == TokenType.Identifier:

                if self.lookup_symbol(p.tokenvalue.text, clss) is None:

                    tip = f'No such symbol exists: `{ p.tokenvalue.text }`'
                    self._push_error(p, LinkerErrorCode.NoSuchSymbol, tip)

                elif p.symbol is not None and p.symbol != self.lookup_symbol(p.tokenvalue_typename(), clss):

                    tip = f"Couldn't assign `{p.tokenvalue_typename()}` to `{p.typename_basename()}` type"
                    self._push_error(p, LinkerErrorCode.IncorrectValueAssignment, tip)

        for p in (p for p in clss.properties if p.form == EpiProperty.Form.Template):

            for n in p.tokens_nested:

                if n.tokentype != TokenType.Identifier:
                    continue

                if n.text == clss.name and not p.is_polymorphic():

                    tip = f'Template argument symbol should be a complete type, but not: `{n.text}`'
                    self._push_error(p, LinkerErrorCode.IncompleteTypeUsage, tip)

                else:

                    sym_lookup = self.lookup_symbol(n.text, clss)
                    assert not isinstance(sym_lookup, EpiProperty)

                    if sym_lookup is None:
                        tip = f"Template argument symbol doesn't exist: `{n.text}`"
                        self._push_error(p, LinkerErrorCode.NoSuchSymbol, tip)

                    elif isinstance(sym_lookup, EpiEnumEntry):
                        tip = f"Template argument should be a type: `{sym_lookup.name}`"
                        self._push_error(p, LinkerErrorCode.BadTemplateArgument, tip)

    def _validate_enum_entries(self, enum: EpiEnum):

        for i, e in enumerate(enum.entries):

            for v in (v for v in e.valuetokens if v.tokentype == TokenType.Identifier):

                sym_lookup = self.lookup_symbol(v.text, enum)
                if sym_lookup is None:
                    tip = f'No such symbol exists: `{v.text}`'
                    self._push_error(e, LinkerErrorCode.NoSuchSymbol, tip)

                elif not isinstance(sym_lookup, EpiEnumEntry):
                    tip = f"Couldn't assign `{v.text}` to the `enum` type"
                    self._push_error(e, LinkerErrorCode.IncorrectValueAssignment, tip)

                elif enum.entries.index(sym_lookup) >= i:
                    tip = f'No such symbol exists: `{v.text}`'
                    self._push_error(e, LinkerErrorCode.NoSuchSymbol, tip)

    def _resolve_enum_values(self, enum: EpiEnum):

        assert isinstance(enum, EpiEnum)

        attr_flagmask = enum.attr_find(TokenType.FlagMask)

        value = 0
        for e in enum.entries:
            e.value = f'(1 << {str(value + 1)})' if attr_flagmask is not None else str(value)

            if len(e.valuetokens) > 1:
                continue

            if len(e.valuetokens) == 1:
                if e.valuetokens[0].tokentype != TokenType.IntegerLiteral:
                    continue

                value = int(e.valuetokens[0].text)

            value += 1

    def link(self) -> list:

        from epigen.linker import linker_inheritance_tree as lntree

        if len(self.__linker_errors) > 0:
            return self.__linker_errors

        inheritance_tree = lntree.InheritanceTree(self.__registry)
        inheritance_tree.build(self)
        inheritance_tree.validate(self)

        for sym in self.__registry.values():

            if isinstance(sym, EpiClass):
                self._validate_class_properties(sym)

                for sym_inner in sym.inner().values():
                    assert isinstance(sym_inner, EpiEnum)
                    self._validate_enum_entries(sym_inner)

            elif isinstance(sym, EpiEnum):
                self._validate_enum_entries(sym)

        for sym in self.__registry.values():

            if isinstance(sym, EpiClass):
                for enum in (inner for inner in sym.inner().values() if isinstance(inner, EpiEnum)):
                    self._resolve_enum_values(enum)

            elif isinstance(sym, EpiEnum):
                self._resolve_enum_values(sym)

        return self.__linker_errors

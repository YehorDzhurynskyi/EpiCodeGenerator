import abc
import sys
from enum import Enum, auto

from epigen.tokenizer import Tokenizer
from epigen.tokenizer import Token
from epigen.tokenizer import TokenType


_EPIATTRIBUTE_CONFLICT_TABLE = {
    TokenType.DisplayName: [],
    TokenType.WriteCallback: [TokenType.ReadOnly],
    TokenType.ReadCallback: [TokenType.WriteOnly],
    TokenType.Virtual: [],
    TokenType.ReadOnly: [TokenType.WriteOnly, TokenType.WriteCallback, TokenType.Min, TokenType.Max],
    TokenType.WriteOnly: [TokenType.ReadOnly, TokenType.ReadCallback],
    TokenType.Transient: [],
    TokenType.Min: [TokenType.ReadOnly],
    TokenType.Max: [TokenType.ReadOnly]
}
# NOTE: The number of conflicting attributes should be equal to the number of occurrence of this attribute in other conflict lists
assert all(len(conflicts) == sum([conflicts_.count(a) for conflicts_ in _EPIATTRIBUTE_CONFLICT_TABLE.values()]) for a, conflicts in _EPIATTRIBUTE_CONFLICT_TABLE.items())

class EpiAttribute:

    def __init__(self, tokentype: TokenType, token: Token = None):

        self.tokentype = tokentype
        self.token = token
        self.is_implied_indirectly = False
        self.__params_positional = []
        self.__params_named = {}

    def __eq__(self, rhs):

        if not isinstance(rhs, EpiAttribute):
            return False

        return \
            self.tokentype == rhs.tokentype and \
            self.__params_positional == rhs.__params_positional and \
            self.__params_named == rhs.__params_named

    def __repr__(self):

        params_positional = ', '.join([repr(p) for p in self.__params_positional])
        params_named = ', '.join([f'{k} => {repr(p)}' for k, p in self.__params_named.items()])

        return f'tokentype={{{repr(self.tokentype)}}}, params-positional=({params_positional}), params-named=({params_named})'

    def conflicts(self, attr) -> bool:

        assert self.tokentype in _EPIATTRIBUTE_CONFLICT_TABLE
        assert attr.tokentype in _EPIATTRIBUTE_CONFLICT_TABLE

        return attr.tokentype in _EPIATTRIBUTE_CONFLICT_TABLE[self.tokentype]


    @property
    def params(self):

        params = self.__params_positional[:]
        params.extend(list(self.__params_named.values())[:])

        return params

    @property
    def params_positional(self):
        return self.__params_positional

    def param_positional_at(self, index: int) -> Token:
        return self.__params_positional[index]

    def param_positional_of(self, tokentype: TokenType) -> Token:
        return next(p for p in self.__params_positional if p.tokentype == tokentype)

    def param_positional_push(self, token: Token):
        self.__params_positional.append(token)

    @property
    def params_named(self):
        return self.__params_named

    def param_named_of(self, name: str) -> Token:

        if name not in self.__params_named:
            return None

        return self.__params_named[name]

    def param_named_push(self, name: str, token: Token):
        self.__params_named[name] = token

    def param_find(self, param: str):

        p = [p for p in self.params if p.text == param]
        p = p[0] if len(p) != 0 else None

        return p


class EpiSymbol(abc.ABC):

    def __init__(self, token):

        self.token = token
        self.__attrs = []

    @property
    def name(self):
        return self.token.text

    def __str__(self):
        return str(self.token)

    def __repr__(self):

        attrs = ', '.join(repr(a) for a in self.__attrs)
        return f'{{{repr(self.token)}}}, attrs-len={len(self.__attrs)}, attrs=({attrs})'

    def __eq__(self, rhs):

        if not isinstance(rhs, EpiSymbol):
            return False

        return \
            self.token == rhs.token and \
            self.__attrs == rhs.__attrs

    @property
    def attrs(self):
        return self.__attrs

    def attr_push(self, attr: EpiAttribute):

        from epigen.idlparser import idlparser_attr as idlattr

        getattr(idlattr, f'introduce_{attr.tokentype.name}')(attr, self)

        duplicates = [a for a in self.__attrs if attr.tokentype == a.tokentype]
        for duplicate in duplicates:

            # NOTE: there could be a case when a duplicating attribute is implied indirectly
            # for example: [Virtual, ReadCallback(SuppressRef=true)], looking on this example
            # Virtual attribute implies ReadCallback, but later parser stumbles on user-provided
            # ReadCallback attribute, so the collision occurs, but the user-defined attributes
            # couldn't collide and such collision is invalid

            assert duplicate.is_implied_indirectly
            self.__attrs.remove(duplicate)

        assert len(duplicates) <= 1

        conflicts = [a for a in self.__attrs if attr.conflicts(a)]
        for conflict in conflicts:

            # NOTE: there could be a case when a conflicting attribute is implied indirectly
            # for example: [Virtual, ReadOnly], looking on this example
            # Virtual attribute implies WriteCallback, but later parser stumbles on user-provided
            # ReadOnly attribute, so the conflict occurs

            assert conflict.is_implied_indirectly
            self.__attrs.remove(conflict)

        self.__attrs.append(attr)

    def attr_find(self, tokentype: TokenType):

        attr = [a for a in self.attrs if a.tokentype == tokentype]
        attr = attr[0] if len(attr) != 0 else None

        return attr


class EpiProperty(EpiSymbol):

    class Form(Enum):

        # NOTE: should be represented as a mask
        Plain = auto()
        Pointer = auto()
        Template = auto()

    def __init__(self, token: Token, tokentype: Token, form):

        super().__init__(token)

        self.tokentype = tokentype
        self.form = form
        self.tokens_nested = []
        self.__tokenvalue = None

    def typename_basename(self):
        return self.tokentype.text

    def typename(self):

        nested_len = len(self.tokens_nested)
        assert \
            (self.form == EpiProperty.Form.Template and nested_len > 0) or \
            (self.form != EpiProperty.Form.Template and nested_len == 0)

        typename = self.tokentype.text
        if nested_len != 0:
            typename = f'{typename}<{",".join(n.text for n in self.tokens_nested)}>'

        if self.form == EpiProperty.Form.Pointer:

            # NOTE: works only for single-depth pointers
            typename = f'{typename}*'

        return typename

    @property
    def tokenvalue(self) -> Token:
        return self.__tokenvalue if self.value_is_assigned() else self.__value_default()

    @tokenvalue.setter
    def tokenvalue(self, token: Token):
        self.__tokenvalue = token

    def value_is_assigned(self) -> bool:
        return self.__tokenvalue is not None

    def value_of(self):
        return Token(self.tokenvalue.tokentype, self.tokenvalue.text).value()

    def is_polymorphic(self) -> bool:
        return self.tokentype.tokentype == TokenType.PtrArrayType or self.form == EpiProperty.Form.Pointer

    def __value_default(self) -> Token:

        value = None
        tokentype = None
        if self.form == EpiProperty.Form.Pointer:
            value = 'nullptr'
        elif self.tokentype.tokentype == TokenType.BoolType:
            value = 'false'
            tokentype = TokenType.FalseLiteral
        elif self.tokentype.is_integer():
            value = '0'
            tokentype = TokenType.IntegerLiteral
        elif self.tokentype.tokentype == TokenType.SingleFloatingType:
            value = '0.0f'
            tokentype = TokenType.SingleFloatingLiteral
        elif self.tokentype.tokentype == TokenType.DoubleFloatingType:
            value = '0.0'
            tokentype = TokenType.DoubleFloatingLiteral
        elif self.tokentype.tokentype == TokenType.CharType:
            value = "'\\0'"
            tokentype = TokenType.CharLiteral
        elif self.tokentype.tokentype == TokenType.WCharType:
            value = "L'\\0'"
            tokentype = TokenType.WCharLiteral
        elif self.tokentype.tokentype == TokenType.StringType:
            value = 'epiDEBUG_ONLY("Empty")'
            tokentype = TokenType.StringLiteral
        elif self.tokentype.tokentype == TokenType.WStringType:
            value = 'epiDEBUG_ONLY(L"Empty")'
            tokentype = TokenType.WStringLiteral
        else:
            return None

        return Token(tokentype, value)

    def __eq__(self, rhs):

        if not isinstance(rhs, EpiProperty):
            return False

        return \
            super().__eq__(rhs) and \
            self.form == rhs.form and \
            self.__tokenvalue == rhs.__tokenvalue and \
            self.tokentype == rhs.tokentype and \
            self.tokens_nested == rhs.tokens_nested

    def __repr__(self):

        rtokentype_nested = ', '.join([repr(t) for t in self.tokens_nested])
        r = f'{super().__repr__()}, tokentype=({repr(self.tokentype)}), form={self.form}, value={repr(self.__tokenvalue)}, tokentype_nested=({rtokentype_nested})'

        return r


class EpiClass(EpiSymbol):

    def __init__(self, token: Token):

        super().__init__(token)

        self.parent = None
        self.inner = {}
        self.properties = []

    def __eq__(self, rhs):

        if not isinstance(rhs, EpiClass):
            return False

        return \
            super().__eq__(rhs) and \
            self.parent == rhs.parent and \
            self.inner == rhs.inner and \
            self.properties == rhs.properties

    def __repr__(self):

        rinner = ', '.join(repr(i) for i in self.inner.values())
        rproperties = ', '.join([repr(p) for p in self.properties])

        r = f'{super().__repr__()}, parent={self.parent}, inner=({rinner}), properties-len={len(self.properties)}'
        r = f'{r}:{rproperties}'

        return r


class EpiEnumEntry(EpiSymbol):

    def __init__(self, token: Token):

        super().__init__(token)

        self.tokenvalue = None

    def __eq__(self, rhs):

        if not isinstance(rhs, EpiEnumEntry):
            return False

        return \
            super().__eq__(rhs) and \
            self.tokenvalue == rhs.tokenvalue

    def __repr__(self):
        return f'{super().__repr__()}, value={repr(self.tokenvalue)}'


class EpiEnum(EpiSymbol):

    def __init__(self, token: Token):

        super().__init__(token)

        self.__base = None
        self.entries = []

    @property
    def base(self):
        return self.__base

    @base.setter
    def base(self, token: Token):

        assert TokenType.is_integer(token.tokentype)

        self.__base = token

    def __eq__(self, rhs):

        if not isinstance(rhs, EpiEnum):
            return False

        return \
            super().__eq__(rhs) and \
            self.__base == rhs.__base and \
            self.entries == rhs.entries

    def __repr__(self):

        r = f'{super().__repr__()}, base={{{repr(self.__base)}}}, entries-len={len(self.entries)}'
        rentries = ', '.join([repr(e) for e in self.entries])
        r = f'{r}:{rentries}'

        return r


class EpiAttributeBuilder:

    def __init__(self):

        self.__tokentype = None
        self.__params_positional = []
        self.__params_named = {}

    def tokentype(self, tokentype: TokenType):

        self.__tokentype = tokentype
        return self

    def param_positional(self, tokentype: TokenType, tokentext: str):

        self.__params_positional.append(Token(tokentype, tokentext))
        return self

    def param_named(self, name: str, tokentype: TokenType, tokentext: str):

        assert name not in self.__params_named

        self.__params_named[name] = Token(tokentype, tokentext)
        return self

    def build(self):

        assert self.__tokentype is not None

        attr = EpiAttribute(self.__tokentype)

        for p in self.__params_positional:
            attr.param_positional_push(p)

        for k, p in self.__params_named.items():
            attr.param_named_push(k, p)

        return attr


class EpiPropertyBuilder:

    def __init__(self):

        self.__name = None
        self.__tokentype = None
        self.__form = EpiProperty.Form.Plain
        self.__value = None
        self.__attrs = []
        self.__tokens_nested = []

    def name(self, name: str):

        self.__name = name
        return self

    def tokentype_type(self, tokentype: TokenType, tokentext: str = None):

        assert tokentype != TokenType.Identifier or tokentext is not None, '<identifier> should be provided with a text'

        tokentext = tokentext if tokentext is not None else TokenType.repr_of(tokentype)
        self.__tokentype = Token(tokentype, tokentext)

        return self

    def form(self, form: EpiProperty.Form):

        self.__form = form
        return self

    def value(self, value: str, tokentype: TokenType = None):

        if tokentype is not None or self.__tokentype is not None:

            if tokentype is None:
                literals = TokenType.literals_of(self.__tokentype.tokentype)
                assert len(literals) == 1
                tokentype = literals[0]
        else:

            assert False, '`tokentype` or `self.__tokentype_type` should be provided'

        self.__value = Token(tokentype, value)
        return self

    def attr(self, attr: EpiAttribute):

        self.__attrs.append(attr)
        return self

    def token_nested(self, tokentype: TokenType, tokentext: str = None):

        assert tokentype != TokenType.Identifier or tokentext is not None, '<identifier> should be provided with a text'

        tokentext = tokentext if tokentext is not None else TokenType.repr_of(tokentype)
        self.__tokens_nested.append(Token(tokentype, tokentext))

        return self

    def build(self):

        assert self.__name is not None
        assert self.__tokentype is not None

        token = Token(TokenType.Identifier, self.__name)

        prty = EpiProperty(token, self.__tokentype, self.__form)

        for attr in self.__attrs:
            prty.attr_push(attr)

        prty.tokens_nested = self.__tokens_nested

        if self.__value is not None:
            prty.tokenvalue = self.__value

        return prty


class EpiClassBuilder:

    def __init__(self):

        self.__name = None
        self.__parent = None
        self.__properties = []
        self.__inner = {}

    def name(self, name: str):

        self.__name = name
        return self

    def parent(self, parent: str):

        self.__parent = parent
        return self

    def property(self, property: EpiProperty):

        self.__properties.append(property)
        return self

    def inner(self, symbol: EpiSymbol):

        assert isinstance(symbol, EpiEnum)

        self.__inner[symbol.name] = symbol
        return self

    def build(self) -> EpiClass:

        assert self.__name is not None

        token = Token(TokenType.Identifier, self.__name)

        clss = EpiClass(token)
        clss.parent = self.__parent
        clss.properties = self.__properties
        clss.inner = self.__inner

        return clss


class EpiEnumEntryBuilder:

    def __init__(self):

        self.__name = None
        self.__tokenvalue = None
        self.__attrs = []

    def name(self, name: str):

        self.__name = name
        return self

    def value(self, value: str):

        self.__tokenvalue = Token(TokenType.IntegerLiteral, value)
        return self

    def attr(self, attr: EpiAttribute):

        self.__attrs.append(attr)
        return self

    def build(self) -> EpiEnumEntry:

        assert self.__name is not None

        token = Token(TokenType.Identifier, self.__name)

        entry = EpiEnumEntry(token)

        for attr in self.__attrs:
            entry.attr_push(attr)

        entry.tokenvalue = self.__tokenvalue

        return entry


class EpiEnumBuilder:

    def __init__(self):

        self.__name = None
        self.__base = None
        self.__entries = []

    def name(self, name: str):

        self.__name = name
        return self

    def base(self, tokentype: TokenType):

        self.__base = Token(tokentype, TokenType.repr_of(tokentype))
        return self

    def entry(self, entry: EpiEnumEntry):

        self.__entries.append(entry)
        return self

    def build(self) -> EpiEnum:

        assert self.__name is not None

        token = Token(TokenType.Identifier, self.__name)

        enum = EpiEnum(token)

        if self.__base is not None:
            enum.base = self.__base

        enum.entries = self.__entries

        return enum

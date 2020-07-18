import abc
import sys
from enum import Enum, auto

from epi_code_generator.tokenizer import Tokenizer
from epi_code_generator.tokenizer import Token
from epi_code_generator.tokenizer import TokenType


class EpiAttribute:

    def __init__(self, tokentype: TokenType, token: Token = None):

        self.tokentype = tokentype
        self.token = token
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

        params_positional = '\n'.join([repr(p) for p in self.__params_positional])
        return f'tokentype=({repr(self.tokentype)}):{params_positional}'

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

    def param_named_push(self, name: str, tokenvalue: Token):
        self.__params_named[name] = tokenvalue

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

        attrs = '\n'.join(repr(a) for a in self.__attrs)
        return f'{repr(self.token)}, attrs={attrs}'

    def __eq__(self, rhs):

        if not isinstance(rhs, EpiSymbol):
            return False

        return \
            self.token == rhs.token and \
            self.__attrs == rhs.__attrs

    @property
    def attrs(self):
        return self.__attrs

    @attrs.setter
    def attrs(self, attrs: list):

        for attr in attrs:
            self.attr_push(attr)

    def attr_push(self, attr: EpiAttribute):

        from epi_code_generator.idlparser import idlparser_attr as idlattr

        getattr(idlattr, f'introduce_{attr.tokentype.name}')(attr, self)
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

        super(EpiProperty, self).__init__(token)

        self.tokentype = tokentype
        self.form = form
        self.tokens_nested = []
        self.__tokenvalue = None

    @property
    def tokenvalue(self) -> Token:
        return self.__tokenvalue if self.value_is_assigned() else self.__value_default()

    @tokenvalue.setter
    def tokenvalue(self, token: Token):
        self.__tokenvalue = token

    def value_is_assigned(self) -> bool:
        return self.__tokenvalue is not None

    def value_of(self):
        return Token(self.tokenvalue.tokentype, 0, 0, '', self.tokenvalue.text).value()

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

        return Token(tokentype, 0, 0, '', value)

    def __eq__(self, rhs):

        if not isinstance(rhs, EpiProperty):
            return False

        return \
            super(EpiProperty, self).__eq__(rhs) and \
            self.form == rhs.form and \
            self.__tokenvalue == rhs.__tokenvalue and \
            self.tokentype == rhs.tokentype and \
            self.tokens_nested == rhs.tokens_nested

    def __repr__(self):

        rtokentype_nested = ', '.join([repr(t) for t in self.tokens_nested])
        r = f'{super(EpiProperty, self).__repr__()}, tokentype=({repr(self.tokentype)}), form={self.form}, value={repr(self.__tokenvalue)}, tokentype_nested={rtokentype_nested}'

        return r


class EpiClass(EpiSymbol):

    def __init__(self, token):

        super(EpiClass, self).__init__(token)

        self.parent = None
        self.properties = []

    def __eq__(self, rhs):

        if not isinstance(rhs, EpiClass):
            return False

        return \
            super(EpiClass, self).__eq__(rhs) and \
            self.parent == rhs.parent and \
            self.properties == rhs.properties

    def __repr__(self):

        r = f'{super(EpiClass, self).__repr__()}, parent={self.parent}, properties-len={len(self.properties)}'
        rproperties = '\n'.join([repr(p) for p in self.properties])
        r = f'{r}:{rproperties}'

        return r


class EpiAttributeBuilder:

    def __init__(self):

        self.__tokentype = None
        self.__params_positional = []

    def tokentype(self, tokentype: TokenType):

        self.__tokentype = tokentype
        return self

    def param_positional(self, tokentype: TokenType, tokentext: str):

        self.__params_positional.append(Token(tokentype, 0, 0, '', tokentext))
        return self

    def build(self):

        assert self.__tokentype is not None

        attr = EpiAttribute(self.__tokentype)

        for p in self.__params_positional:
            attr.param_positional_push(p)

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
        self.__tokentype = Token(tokentype, 0, 0, '', tokentext)

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

        self.__value = Token(tokentype, 0, 0, '', value)
        return self

    def attr(self, attr: EpiAttribute):

        self.__attrs.append(attr)
        return self

    def token_nested(self, tokentype: TokenType, tokentext: str = None):

        assert tokentype != TokenType.Identifier or tokentext is not None, '<identifier> should be provided with a text'

        tokentext = tokentext if tokentext is not None else TokenType.repr_of(tokentype)
        self.__tokens_nested.append(Token(tokentype, 0, 0, '', tokentext))

        return self

    def build(self):

        assert self.__name is not None
        assert self.__tokentype is not None

        token = Token(TokenType.Identifier, 0, 0, '', self.__name)

        prty = EpiProperty(token, self.__tokentype, self.__form)
        prty.attrs = self.__attrs
        prty.tokens_nested = self.__tokens_nested

        if self.__value is not None:
            prty.tokenvalue = self.__value

        return prty


class EpiClassBuilder:

    def __init__(self):

        self.__name = None
        self.__parent = None
        self.__properties = []

    def name(self, name: str):

        self.__name = name
        return self

    def parent(self, parent: str):

        self.__parent = parent
        return self

    def property(self, property: EpiProperty):

        self.__properties.append(property)
        return self

    def build(self) -> EpiClass:

        assert self.__name is not None

        token = Token(TokenType.Identifier, 0, 0, '', self.__name)

        clss = EpiClass(token)
        clss.parent = self.__parent
        clss.properties = self.__properties

        return clss

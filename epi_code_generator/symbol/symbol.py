import abc
import sys
from enum import Enum, auto

from epi_code_generator.tokenizer import Tokenizer
from epi_code_generator.tokenizer import Token
from epi_code_generator.tokenizer import TokenType


class EpiAttribute:

    def __init__(self, token: Token):

        self.token = token
        self.__params_positional = []
        self.__params_named = {}

    def __eq__(self, rhs):
        return self.token == rhs.token

    @property
    def params(self):

        params = self.__params_positional[:]
        params.extend(list(self.__params_named.values())[:])

        return params

    def param_push_positional(self, token: Token):
        self.__params_positional.append(token)

    def param_push_named(self, name: str, tokenvalue: Token):
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
        return repr(self.token)

    def __eq__(self, rhs):
        return \
            self.token == rhs.token and \
            self.attrs == rhs.attrs

    @property
    def attrs(self):
        return self.__attrs

    @attrs.setter
    def attrs(self, attrs: list):

        for attr in attrs:
            self.attr_push(attr)

    def attr_push(self, attr: EpiAttribute):

        import epi_code_generator.idlparser.idlparser_attr

        import pytest
        pytest.set_trace()

        getattr(epi_code_generator.idlparser.idlparser_attr, f'introduce_{str(attr.tokentype)}')(attr, self)
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
        self.value = self._default_value()
        self.tokentype_nested = []

    def _default_value(self):

        value = None
        if self.form == EpiProperty.Form.Pointer:
            value = 'nullptr'
        elif self.tokentype.tokentype == TokenType.BoolType:
            value = 'false'
        elif self.tokentype.is_integer():
            value = '0'
        elif self.tokentype.tokentype == TokenType.SingleFloatingType:
            value = '0.0f'
        elif self.tokentype.tokentype == TokenType.DoubleFloatingType:
            value = '0.0'
        elif self.tokentype.tokentype == TokenType.CharType:
            value = "'\\0'"
        elif self.tokentype.tokentype == TokenType.WCharType:
            value = "L'\\0'"
        elif self.tokentype.tokentype == TokenType.StringType:
            value = 'epiDEBUG_ONLY("Empty")'
        elif self.tokentype.tokentype == TokenType.WStringType:
            value = 'epiDEBUG_ONLY(L"Empty")'

        return value

    def __eq__(self, rhs):
        return \
            super(EpiProperty, self).__eq__(rhs) and \
            self.form == rhs.form and \
            self.value == rhs.value and \
            self.tokentype == rhs.tokentype

    def __repr__(self):

        rtokentype_nested = ', '.join([repr(t) for t in self.tokentype_nested])
        r = f'{super(EpiProperty, self).__repr__()}, tokentype=({repr(self.tokentype)}), form={self.form}, value={self.value}, tokentype_nested={rtokentype_nested}'

        return r


class EpiClass(EpiSymbol):

    def __init__(self, token):

        super(EpiClass, self).__init__(token)

        self.parent = None
        self.properties = []

    def __eq__(self, rhs):
        return \
            super(EpiClass, self).__eq__(rhs) and \
            self.parent == rhs.parent and \
            self.properties == rhs.properties

    def __repr__(self):

        r = f'{super(EpiClass, self).__repr__()}, parent={self.parent}, properties-len={len(self.properties)}'
        rproperties = '\n'.join([repr(p) for p in self.properties])
        r = f'{r}:{rproperties}'

        return r


class EpiPropertyBuilder:

    def __init__(self):

        self.__name = None
        self.__tokentype_type = None
        self.__tokentype_text = None
        self.__form = EpiProperty.Form.Plain
        self.__value = None
        self.__attrs = []
        self.__tokentype_nested = []

    def name(self, name: str):

        self.__name = name
        return self

    def tokentype_type(self, tokentype: TokenType, tokentext: str = None):

        assert tokentype != TokenType.Identifier or tokentext is not None, '<identifier> should be provided with a text'

        self.__tokentype_type = tokentype
        self.__tokentype_text = tokentext

        return self

    def form(self, form: EpiProperty.Form):

        self.__form = form
        return self

    def value(self, value: str):

        self.__value = value
        return self

    def attr(self, attr: EpiAttribute):

        self.__attrs.append(attr)
        return self

    def tokentype_nested(self, tokentype: TokenType):

        self.__tokentype_nested.append(tokentype)
        return self

    def build(self):

        assert self.__name is not None
        assert self.__tokentype_type is not None

        token = Token(TokenType.Identifier, 0, 0, '', self.__name)

        tokentype_text = self.__tokentype_text if self.__tokentype_text is not None else TokenType.repr_of(self.__tokentype_type)
        tokentype = Token(self.__tokentype_type, 0, 0, '', tokentype_text)

        prty = EpiProperty(token, tokentype, self.__form)
        prty.attrs = self.__attrs
        prty.tokentype_nested = self.__tokentype_nested

        if self.__value is not None:
            prty.value = self.__value

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

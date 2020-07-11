import abc
import sys
from enum import Enum, auto

from epi_code_generator.tokenizer import Tokenizer
from epi_code_generator.tokenizer import Token
from epi_code_generator.tokenizer import TokenType


class EpiAttributeInvalidListError(Exception):
    pass


class EpiAttribute:

    RANGES = {
        TokenType.Private: (0, 0),
        TokenType.WriteCallback: (0, 1),
        TokenType.ReadCallback: (0, 1),
        TokenType.Virtual: (0, 0),
        TokenType.ReadOnly: (0, 0),
        TokenType.WriteOnly: (0, 0),
        TokenType.Transient: (0, 0),
        TokenType.ExpectMin: (1, 1),
        TokenType.ExpectMax: (1, 1),
        TokenType.ForceMin: (1, 1),
        TokenType.ForceMax: (1, 1)
    }

    def __init__(self, tokentype):

        self.tokentype = tokentype
        self.params = []

    def __eq__(self, rhs):
        return self.tokentype == rhs.tokentype

    def find_param(self, param: str):

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
    def attrs(self, attrs):

        self._preprocess_attrs(attrs)
        self.__attrs = attrs

    def find_attr(self, tokentype: TokenType):

        attr = [a for a in self.attrs if a.tokentype == tokentype]
        attr = attr[0] if len(attr) != 0 else None

        return attr

    @abc.abstractmethod
    def _preprocess_attrs(self, attrs):

        if len(attrs) != len(set(attrs)):
            raise EpiAttributeInvalidListError(f'Duplicating attribute')


'''
class EpiMethod(EpiSymbol):

    def __init__(self, token):

        super(EpiMethod, self).__init__(token)
        self.params = []

    def _is_valid_attrs(self, attrs):
        return len(attrs) == 0
'''


class EpiVariable(EpiSymbol):

    class Form(Enum):

        Plain = auto()
        Pointer = auto()
        Array = auto()

    def __init__(self, token: Token, tokentype: Token, form):

        super(EpiVariable, self).__init__(token)

        self.tokentype = tokentype
        self.form = form
        self.value = _default_value()

        def _default_value(self):

            value = None
            if self.form == EpiVariable.Form.Pointer:
                value = 'nullptr'
            elif self.tokentype.type == TokenType.BoolType:
                value = 'false'
            elif self.tokentype.type in [
                TokenType.IntType,
                TokenType.UIntType,
                TokenType.ByteType,
                TokenType.SizeTType,
                TokenType.HashTType
            ]:
                value = '0'
            elif self.tokentype.type == TokenType.SingleFloatingType:
                value = '0.0f'
            elif self.tokentype.type == TokenType.DoubleFloatingType:
                value = '0.0'
            elif self.tokentype.type == TokenType.CharType:
                value = "'\\0'"
            elif self.tokentype.type == TokenType.WCharType:
                value = "L'\\0'"
            elif self.tokentype.type == TokenType.StringType:
                value = 'epiDEBUG_ONLY("Empty")'
            elif self.tokentype.type == TokenType.WStringType:
                value = 'epiDEBUG_ONLY(L"Empty")'

            return value

    def __eq__(self, rhs):
        return \
            super(EpiVariable, self).__eq__(rhs) and \
            self.form == rhs.form and \
            self.value == rhs.value and \
            self.tokentype == rhs.tokentype

    def _preprocess_attrs(self, attrs):

        super(EpiVariable, self)._preprocess_attrs(attrs)

        if any(a.tokentype == TokenType.Virtual for a in attrs):

            if not any(a.tokentype == TokenType.Transient for a in attrs):
                attrs.append(EpiAttribute(TokenType.Transient))

            if not any(a.tokentype == TokenType.ReadCallback for a in attrs):
                attrs.append(EpiAttribute(TokenType.ReadCallback))

            if not any(a.tokentype == TokenType.WriteCallback for a in attrs):
                attrs.append(EpiAttribute(TokenType.WriteCallback))

        for attr in attrs:

            if attr.tokentype.name not in Tokenizer.BUILTIN_PRTY_ATTRS.keys():
                raise EpiAttributeInvalidListError(f'Variable doesn\'t support `{attr.tokentype.name}` attribute')

            if attr.tokentype not in [
                TokenType.ExpectMin,
                TokenType.ExpectMax,
                TokenType.ForceMin,
                TokenType.ForceMax
            ]:
                continue

            if attr.tokentype == TokenType.ExpectMin and any(a.tokentype == TokenType.ForceMin for a in attrs):
                raise EpiAttributeInvalidListError(f'Mutually exclusive attributes `ExpectMin` and `ForceMin`')

            if attr.tokentype == TokenType.ForceMin and any(a.tokentype == TokenType.ExpectMin for a in attrs):
                raise EpiAttributeInvalidListError(f'Mutually exclusive attributes `ExpectMin` and `ForceMin`')

            if attr.tokentype == TokenType.ExpectMax and any(a.tokentype == TokenType.ForceMax for a in attrs):
                raise EpiAttributeInvalidListError(f'Mutually exclusive attributes `ExpectMax` and `ForceMax`')

            if attr.tokentype == TokenType.ForceMax and any(a.tokentype == TokenType.ExpectMax for a in attrs):
                raise EpiAttributeInvalidListError(f'Mutually exclusive attributes `ExpectMax` and `ForceMax`')

            if self.tokentype not in [
                TokenType.SingleFloatingType,
                TokenType.DoubleFloatingType,
                TokenType.IntType,
                TokenType.UIntType,
                TokenType.ByteType,
                TokenType.SizeTType,
                TokenType.HashTType
            ]:
                raise EpiAttributeInvalidListError(f'Attribute type {attr.tokentype.name} for this variable')

            if self.tokentype == TokenType.FloatingType and not all(p.type == TokenType.FloatingLiteral for p in attr.params):
                raise EpiAttributeInvalidListError(f'Attribute parameter type (Expected a float)')

            if self.tokentype in [
                TokenType.IntType,
                TokenType.UIntType,
                TokenType.ByteType,
                TokenType.SizeTType,
                TokenType.HashTType
            ] and not all(p.type == TokenType.IntegerLiteral for p in attr.params):
                raise EpiAttributeInvalidListError(f'Attribute parameter type (Expected an integer)')


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
        return f'{super(EpiClass, self).__repr__()}, parent={self.parent}'

    def _preprocess_attrs(self, attrs):
        super(EpiClass, self)._preprocess_attrs(attrs)


'''
class EpiInterface(EpiSymbol):

    def __init__(self, name):

        super(EpiInterface, self).__init__(name)

        self.parent = None
        self.methods = []

    def _is_valid_attrs(self, attrs):
        return True


class EpiEnumEntry(EpiSymbol):

    def __init__(self, name):
        super(EpiEnumEntry, self).__init__(name)

    def _is_valid_attrs(self, attrs):
        return True


class EpiEnum(EpiSymbol):

    def __init__(self, name):

        super(EpiEnum, self).__init__(name)

        self.entries = []

    def _is_valid_attrs(self, attrs):
        return True
'''

class EpiPropertyBuilder:

    def __init__(self):

        self._name = None
        self._tokentype_type = None
        self._tokentype_value = None
        self._form = EpiVariable.Form.Plain
        self._value = None
        self._attrs = []

    def name(self, name: str):

        self._name = name
        return self

    def tokentype_type(self, tokentype: TokenType):

        self._tokentype_type = tokentype
        return self

    def tokentype_value(self, tokentype: TokenType):

        self._tokentype_value = tokentype
        return self

    def form(self, form: EpiVariable.Form):

        self._form = form
        return self

    def value(self, value: str):

        self._value = value
        return self

    def attr(self, attr: EpiAttribute):

        self._attrs.append(attr)
        return self

    def build(self):

        assert self._name is not None
        assert self._tokentype_type is not None
        assert self._tokentype_value is not None

        tokentype = Token(self._tokentype_type, 0, 0, '', self._name)
        tokenvalue = Token(self._tokentype_type, 0, 0, '', self._name)

        prty = EpiVariable(tokenvalue, tokentype, self._form)
        prty.attrs = self._attrs

        if self._value is not None:
            prty.value = self._value

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

    def property(self, property: EpiVariable):

        self.__properties.append(property)
        return self

    def build(self) -> EpiClass:

        assert self.__name is not None

        token = Token(TokenType.Identifier, 0, 0, '', self.__name)

        clss = EpiClass(token)
        clss.parent = self.__parent
        clss.properties = self.__properties

        return clss

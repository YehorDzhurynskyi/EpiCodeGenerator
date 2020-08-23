import zlib

from epigen.code_generator import code_generator_builder as bld
from epigen.symbol import EpiClass, EpiProperty, EpiEnum
from epigen.tokenizer import Tokenizer, TokenType


def _property_getter(prty: EpiProperty, **kwargs) -> str:

    if prty.attr_find(TokenType.WriteOnly) is not None:
        return None

    const = kwargs['const'] if 'const' in kwargs else True
    body = kwargs['body'] if 'body' in kwargs else True
    suffix = kwargs['suffix'] if 'suffix' in kwargs else ''

    assert isinstance(const, bool)
    assert isinstance(body, bool)
    assert isinstance(suffix, str)

    signature = ''
    if not any(a.tokentype in [TokenType.ReadCallback] for a in prty.attrs):
        signature = 'inline '

    attr_readcallback = prty.attr_find(TokenType.ReadCallback)

    # NOTE: has no effect for value-return types
    if attr_readcallback is not None and not const:
        return None

    if prty.form == EpiProperty.Form.Pointer:
        signature = f'{signature}const ' if const else signature
        signature = f'{signature}{prty.typename()} '

    elif prty.typename_basename() in Tokenizer.fundamentals() or isinstance(prty.symbol, EpiEnum):

        assert prty.form == EpiProperty.Form.Plain

        # NOTE: has no effect for plain types
        if not const:
            return None

        signature = f'{signature}{prty.typename()} '

    elif attr_readcallback is not None and attr_readcallback.param_named_of('SuppressRef') is not None:
        signature = f'{signature}{prty.typename()} '

    else:
        signature = f'{signature}const ' if const else signature
        signature = f'{signature}{prty.typename()}& '

    signature = f'{signature}Get{prty.name}{suffix}()'
    signature = f'{signature} const' if const else signature

    if not body:
        return signature

    signature = f'{signature} {{ return '
    value = f'Get{prty.name}_Callback()' if prty.attr_find(TokenType.ReadCallback) else f'm_{prty.name}'
    signature = f'{signature}{value}; }}'

    return signature

def _property_setter(prty: EpiProperty, **kwargs) -> str:

    if prty.attr_find(TokenType.ReadOnly) is not None:
        return None

    body = kwargs['body'] if 'body' in kwargs else True
    suffix = kwargs['suffix'] if 'suffix' in kwargs else ''

    assert isinstance(body, bool)
    assert isinstance(suffix, str)

    # TODO: if min/max attr doesn't force the value then it shouldn't force a non-inline getter in release build
    signature = ''
    if not any(a.tokentype in [TokenType.WriteCallback,
                               TokenType.Min,
                               TokenType.Max] for a in prty.attrs):
        signature = 'inline '

    signature = f'{signature}void Set{prty.name}{suffix}('
    if prty.form not in [EpiProperty.Form.Pointer] and \
       prty.typename_basename() not in Tokenizer.fundamentals() and \
       not isinstance(prty.symbol, EpiEnum):

        attr_writecallback = prty.attr_find(TokenType.WriteCallback)
        if attr_writecallback is not None and attr_writecallback.param_named_of('SuppressRef') is not None:
            signature = f'{signature}{prty.typename()} '
        else:
            signature = f'{signature}const {prty.typename()}& '

    else:
        signature = f'{signature}{prty.typename()} '

    signature = f'{signature}value)'

    if not body:
        return signature

    signature = f'{signature} {{ '

    attr_min = prty.attr_find(TokenType.Min)
    if attr_min is not None:

        value_min = attr_min.param_positional_at(0)
        force = attr_min.param_named_of('Force')
        if force:
            signature = f'{signature}value = std::max(value, {value_min.value()}); '
        else:
            signature = f'{signature}epiExpected(value >= {value_min.value()}); '

    attr_max = prty.attr_find(TokenType.Max)
    if attr_max is not None:

        value_max = attr_max.param_positional_at(0)
        force = attr_max.param_named_of('Force')
        if force:
            signature = f'{signature}value = std::min(value, {value_max.value()}); '
        else:
            signature = f'{signature}epiExpected(value <= {value_max.value()}); '

    if prty.attr_find(TokenType.WriteCallback) is not None:
        signature = f'{signature}Set{prty.name}_Callback(value)'
    else:
        signature = f'{signature}m_{prty.name} = value'

    signature = f'{signature}; }}'

    return signature

def emit_properties(properties: list, accessor_modifier: str, builder: bld.Builder) -> bld.Builder:

    if len(properties) == 0:
        return builder

    builder.tab(-1)
    builder.line(f'{accessor_modifier}:')
    builder.tab()

    for p in properties:
        builder.line(f'{p.typename()} m_{p.name}{p.tokenvalue_repr()};')

    builder.tab(-1)
    builder.line_empty()

    return builder

def emit_property_callbacks(properties: list, accessor_modifier: str, builder: bld.Builder) -> bld.Builder:

    if len(properties) == 0:
        return builder

    builder.tab(-1)
    builder.line(f'{accessor_modifier}:')
    builder.tab()

    for p in properties:

        if p.attr_find(TokenType.ReadCallback) is not None:

            p_getter = _property_getter(p, body=False, suffix='_Callback')
            if p_getter is not None:
                builder.line(f'{p_getter};')

        if p.attr_find(TokenType.WriteCallback) is not None:

            p_setter = _property_setter(p, body=False, suffix='_Callback')
            if p_setter is not None:
                builder.line(f'{p_setter};')

    builder.tab(-1)
    builder.line_empty()

    return builder

def emit_sekeleton_file(module_basename: str, ext: str, builder: bld.Builder) -> bld.Builder:

    if ext in ['cxx', 'hxx']:

        builder.template('header_comment')
        builder.line_empty()

    if ext == 'hxx':
        return builder

    if ext == 'h':

        builder.template('h/header')
        builder.line_empty()
        builder.anchor_gen_region('include')
        emit_include_section(module_basename, ext, builder)
        builder.anchor_gen_endregion('include')
        builder.line_empty()
        builder.anchor_namespace_begin()
        builder.line_empty()

    elif ext == 'cpp':

        import pathlib
        module_name = pathlib.Path(module_basename).parts[0]

        builder.template('cpp/header', module_name=module_name)
        builder.line_empty()
        builder.anchor_gen_region('include')
        emit_include_section(module_basename, ext, builder)
        builder.anchor_gen_endregion('include')
        builder.line_empty()
        builder.anchor_namespace_begin()

    elif ext == 'cxx':
        builder.template('cxx/header')
        builder.line_empty()

    builder.template('footer')
    builder.line_empty()

    return builder

def emit_include_section(module_basename: str, ext: str, builder: bld.Builder) -> bld.Builder:

    assert ext in ['h', 'cpp']

    if ext == 'h':
        builder.template('h/include', module_basename=module_basename)

    elif ext == 'cpp':
        builder.template('cpp/include', module_basename=module_basename)

    return builder

def emit_class_declaration(clss: EpiClass, builder: bld.Builder) -> bld.Builder:

    assert isinstance(clss, EpiClass)

    if len(clss.inner()) == 0:
        builder.line_empty()

    else:
        builder.line_empty()
        builder.line('public:')
        builder.tab()

        for symbol_inner in clss.inner().values():

            assert isinstance(symbol_inner, EpiEnum)

            symfullname = f'{clss.name}::{symbol_inner.name}'
            emit_skeleton_enum(symbol_inner, symfullname, builder)

        builder.tab(-1)

    clss_typeid = hex(zlib.crc32(clss.name.encode()) & 0xffffffff)
    builder.template('h/class_header', class_name=clss.name, class_typeid=clss_typeid)
    builder.line_empty()

    # pids
    builder.tab()
    builder.line(f'enum {clss.name}_PIDs')
    builder.line('{')
    builder.tab()

    for p in clss.properties:

        crc = hex(zlib.crc32(p.name.encode()) & 0xffffffff)
        builder.line(f'PID_{p.name} = {crc},')

    builder.line(f'PID_COUNT = {len(clss.properties)}')

    builder.tab(-1)
    builder.line('};')
    builder.tab(-1)
    builder.line_empty()

    properties_with_callback = [p for p in clss.properties if p.attr_find(TokenType.ReadCallback) is not None or
                                                              p.attr_find(TokenType.WriteCallback) is not None]
    emit_property_callbacks(properties_with_callback, 'protected', builder)

    properties_non_virtual = [p for p in clss.properties if p.attr_find(TokenType.Virtual) is None]
    emit_properties(properties_non_virtual, 'protected', builder)

    return builder

def emit_skeleton_class(clss: EpiClass, builder: bld.Builder) -> bld.Builder:

    assert isinstance(clss, EpiClass)

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    builder.line(f'class {clss.name} : public {clss_parent}')
    builder.line('{')
    builder.anchor_gen_region(clss.name)
    builder.anchor_gen_endregion(clss.name)
    builder.line('};')
    builder.line_empty()

    return builder

def emit_enum_declaration(enum: EpiEnum, builder: bld.Builder) -> bld.Builder:

    assert isinstance(enum, EpiEnum)
    assert len(enum.values()) == len(enum.entries)

    builder.tab()

    values = enum.values()
    for i, name in enumerate(values):

        value = values[name]
        sep = ',' if i != len(enum.entries) - 1 else ''
        builder.line(f'{name} = {value}{sep}')

    builder.tab(-1)

    return builder

def emit_skeleton_enum(enum: EpiEnum, symfullname: str, builder: bld.Builder) -> bld.Builder:

    assert isinstance(enum, EpiEnum)

    attr_flagmask = enum.attr_find(TokenType.FlagMask)

    enum_base = f' : {enum.base.text}' if enum.base is not None else ''
    enum_type = 'enum' if attr_flagmask is not None else 'enum class'

    builder.line(f'{enum_type} {enum.name}{enum_base}')
    builder.line('{')
    builder.anchor_gen_region(symfullname)
    builder.anchor_gen_endregion(symfullname)
    builder.line('};')
    builder.line_empty()

    return builder

def emit_class_serialization(clss: EpiClass, builder: bld.Builder) -> bld.Builder:

    assert isinstance(clss, EpiClass)

    properties_non_transient = [p for p in clss.properties if p.attr_find(TokenType.Transient) is None]

    builder.template('cxx/class_serialization_header', class_name=clss.name)
    if len(properties_non_transient) > 0:

        builder.line_empty()
        builder.tab()

        for p in properties_non_transient:
            builder.template('cxx/class_serialization_property', property_name=p.name)

        builder.tab(-1)

    builder.line('}')
    builder.line_empty()

    builder.template('cxx/class_deserialization_header', class_name=clss.name)

    if len(properties_non_transient) > 0:

        builder.line_empty()
        builder.tab()

        for p in properties_non_transient:
            builder.template('cxx/class_deserialization_property', property_name=p.name)

        builder.tab(-1)

    builder.line('}')
    builder.line_empty()

    return builder

def emit_class_meta(clss: EpiClass, builder: bld.Builder) -> bld.Builder:

    assert isinstance(clss, EpiClass)

    builder.template('cxx/class_meta_header', class_name=clss.name)
    builder.line_empty()

    builder.tab()
    for p in clss.properties:

        p_nested_typeid = 'MetaTypeID_None'

        # TODO: make it work for >1 template arguments
        if p.form == EpiProperty.Form.Template:
            p_nested_typeid = f'epiHashCompileTime({p.tokens_nested[0].text})'

        p_typeid = f'epiHashCompileTime({p.typename_fullname()})'

        if p.form == EpiProperty.Form.Pointer:

            p_nested_typeid = p_typeid
            p_typeid = 'MetaTypeID_Ptr'

        attr_readcallback = p.attr_find(TokenType.ReadCallback)
        attr_writecallback = p.attr_find(TokenType.WriteCallback)
        attr_readonly = p.attr_find(TokenType.ReadOnly)
        attr_writeonly = p.attr_find(TokenType.WriteOnly)

        flags = []
        if attr_readcallback is not None:
            flags.append('ReadCallback')
        if attr_writecallback is not None:
            flags.append('WriteCallback')
        if attr_readonly is not None:
            flags.append('ReadOnly')
        if attr_writeonly is not None:
            flags.append('WriteOnly')

        flags = [f'MetaProperty::Flags::Mask{f}' for f in flags]

        p_ptr_read = 'nullptr'
        if attr_writeonly is None:
            if attr_readcallback is None:
                p_ptr_read = f'offsetof({clss.name}, m_{p.name})'
            elif attr_writeonly is None:
                p_ptr_read = f'offsetof({clss.name}, Get{p.name}_FuncPtr)'

        p_ptr_write = 'nullptr'
        if attr_readonly is None:
            if attr_writecallback is None:
                p_ptr_write = f'offsetof({clss.name}, m_{p.name})'
            else:
                p_ptr_write = f'offsetof({clss.name}, Set{p.name}_FuncPtr)'

        builder.template('cxx/class_meta_property',
                         property_name=p.name,
                         property_typeid=p_typeid,
                         property_nested_typeid=p_nested_typeid,
                         property_flags=' | '.join(flags),
                         property_ptr_read=p_ptr_read,
                         property_ptr_write=p_ptr_write)

        builder.line_empty()

    builder.tab(-1)

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    builder.template('cxx/class_meta_footer', class_name=clss.name, class_parent_name=clss_parent)
    builder.line_empty()

    return builder

def emit_class_declaration_hidden(clss: EpiClass, builder: bld.Builder) -> bld.Builder:

    assert isinstance(clss, EpiClass)

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    builder.template('hxx/class_hidden_header', class_name=clss.name, class_parent_name=clss_parent)

    if len(clss.properties) > 0:

        builder.line(' \\')
        # getters/setters
        for p in clss.properties:

            p_getter1 = _property_getter(p)
            if p_getter1 is not None:
                builder.line(f'{p_getter1} \\')

            p_getter2 = _property_getter(p, const=False)
            if p_getter2 is not None:
                builder.line(f'{p_getter2} \\')

            p_setter = _property_setter(p)
            if p_setter is not None:
                builder.line(f'{p_setter} \\')

    builder.line(' \\')

    # pidx
    builder.line(f'enum {clss.name}_PIDXs \\')
    builder.line('{ \\')
    builder.tab()

    for i, p in enumerate(clss.properties):
        builder.line(f'PIDX_{p.name} = {i}, \\')

    builder.line(f'PIDX_COUNT = {len(clss.properties)} \\')

    builder.tab(-1)
    builder.line('}; \\')

    # getters/setters function pointers
    properties_func_ptrs = [p for p in clss.properties if p.attr_find(TokenType.ReadCallback) is not None or p.attr_find(TokenType.WriteCallback) is not None]
    if len(properties_func_ptrs) > 0:

        builder.line(' \\')
        builder.line('private: \\')
        for p in properties_func_ptrs:

            attr_readcallback = p.attr_find(TokenType.ReadCallback)
            attr_writecallback = p.attr_find(TokenType.WriteCallback)

            if attr_readcallback is not None:

                if p.form == EpiProperty.Form.Pointer:
                    builder.line(f'const {p.typename()} ({clss.name}::*Get{p.name}_FuncPtr)() const {{ &{clss.name}::Get{p.name} }}; \\')

                elif p.typename_basename() not in Tokenizer.fundamentals() and \
                     not isinstance(p.symbol, EpiEnum) and \
                     attr_readcallback.param_named_of('SuppressRef') is None:
                    builder.line(f'const {p.typename()}& ({clss.name}::*Get{p.name}_FuncPtr)() const {{ &{clss.name}::Get{p.name} }}; \\')

                else:
                    builder.line(f'{p.typename()} ({clss.name}::*Get{p.name}_FuncPtr)() const {{ &{clss.name}::Get{p.name} }}; \\')

            if attr_writecallback is not None:

                if p.typename_basename() not in Tokenizer.fundamentals() and \
                   not isinstance(p.symbol, EpiEnum) and \
                   p.form != EpiProperty.Form.Pointer and \
                   attr_writecallback.param_named_of('SuppressRef') is None:
                    builder.line(f'void ({clss.name}::*Set{p.name}_FuncPtr)(const {p.typename()}&) {{ &{clss.name}::Set{p.name} }}; \\')

                else:
                    builder.line(f'void ({clss.name}::*Set{p.name}_FuncPtr)({p.typename()}) {{ &{clss.name}::Set{p.name} }}; \\')

    builder.line_empty()
    builder.line_empty()

    return builder

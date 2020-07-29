from epigen.code_generator import code_generator_builder as bld

from epigen.tokenizer import TokenType
from epigen.tokenizer import Tokenizer

from epigen.symbol import EpiClass
from epigen.symbol import EpiProperty

import zlib


def _property_getter(prty: EpiProperty, **kwargs) -> str:

    if prty.attr_find(TokenType.WriteOnly) is not None:
        return None

    body = kwargs['body'] if 'body' in kwargs else True
    suffix = kwargs['suffix'] if 'suffix' in kwargs else ''

    assert isinstance(body, bool)
    assert isinstance(suffix, str)

    signature = ''
    if not any(a.tokentype in [TokenType.ReadCallback] for a in prty.attrs):
        signature = 'inline '

    if prty.form == EpiProperty.Form.Pointer:
        signature = f'{signature}const {prty.typename()} '

    elif prty.typename_basename() not in Tokenizer.fundamentals():

        attr_readcallback = prty.attr_find(TokenType.ReadCallback)
        if attr_readcallback is not None and attr_readcallback.param_named_of('SuppressRef') is not None:
            signature = f'{signature}{prty.typename()} '
        else:
            signature = f'{signature}const {prty.typename()}& '

    else:
        signature = f'{signature}{prty.typename()} '

    signature = f'{signature}Get{prty.name}{suffix}() const'

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
    if prty.form not in [EpiProperty.Form.Pointer] and prty.typename_basename() not in Tokenizer.fundamentals():

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

        value = f'{{{p.tokenvalue.text}}}' if p.tokenvalue is not None else ''
        builder.line(f'{p.typename()} m_{p.name}{value};')

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

        builder.template('h/header', module_basename=module_basename)
        builder.line_empty()

    elif ext == 'cpp':

        import pathlib

        module_name = pathlib.Path(module_basename).parts[0]
        builder.template('cpp/header', module_name=module_name, module_basename=module_basename)

    elif ext == 'cxx':

        builder.template('cxx/header')
        builder.line_empty()

    builder.template('footer')
    builder.line_empty()

    return builder

def emit_class_declaration(clss: EpiClass, builder: bld.Builder) -> bld.Builder:

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

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    builder.line(f'class {clss.name} : public {clss_parent}')
    builder.line('{')
    builder.anchor_gen_region(clss.name)

    builder = emit_class_declaration(clss, builder)

    builder.tab(-1)
    builder.anchor_gen_endregion(clss.name)
    builder.line('};')
    builder.line_empty()

    return builder

def emit_class_serialization(clss: EpiClass, builder: bld.Builder) -> bld.Builder:

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

    builder.template('cxx/class_meta_header', class_name=clss.name)
    builder.line_empty()

    builder.tab()
    for p in clss.properties:

        p_nested_typeid = 'MetaTypeID_None'

        # TODO: make it work for >1 template arguments
        if p.form == EpiProperty.Form.Template:
            p_nested_typeid = f'epiHashCompileTime({p.tokens_nested[0].text})'

        p_typeid = f'epiHashCompileTime({p.typename_basename()})'

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

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    builder.template('hxx/class_hidden_header', class_name=clss.name, class_parent_name=clss_parent)

    if len(clss.properties) > 0:

        builder.line(' \\')
        # getters/setters
        for p in clss.properties:

            p_getter = _property_getter(p)
            if p_getter is not None:
                builder.line(f'{p_getter} \\')

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
                elif p.typename_basename() not in Tokenizer.fundamentals() and attr_readcallback.param_named_of('SuppressRef') is None:
                    builder.line(f'const {p.typename()}& ({clss.name}::*Get{p.name}_FuncPtr)() const {{ &{clss.name}::Get{p.name} }}; \\')
                else:
                    builder.line(f'{p.typename()} ({clss.name}::*Get{p.name}_FuncPtr)() const {{ &{clss.name}::Get{p.name} }}; \\')

            if attr_writecallback is not None:

                if p.typename_basename() not in Tokenizer.fundamentals() and p.form != EpiProperty.Form.Pointer and attr_writecallback.param_named_of('SuppressRef') is None:
                    builder.line(f'void ({clss.name}::*Set{p.name}_FuncPtr)(const {p.typename()}&) {{ &{clss.name}::Set{p.name} }}; \\')
                else:
                    builder.line(f'void ({clss.name}::*Set{p.name}_FuncPtr)({p.typename()}) {{ &{clss.name}::Set{p.name} }}; \\')

    builder.line_empty()
    builder.line_empty()

    return builder

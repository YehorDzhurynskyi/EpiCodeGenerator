from .code_generator_builder import Builder

from ..tokenizer import TokenType
from ..tokenizer import Tokenizer

from ..symbol import EpiClass
from ..symbol import EpiProperty

import zlib


def _property_signature_getter(prty: EpiProperty, const: bool) -> str:

    if prty.attr_find(TokenType.WriteOnly) is not None:
        return None

    signature = ''
    if not any(a.tokentype in [TokenType.ReadCallback,
                               TokenType.WriteCallback,
                               TokenType.Min,
                               TokenType.Max] for a in prty.attrs):
        signature = 'inline '

    if prty.form not in [EpiProperty.Form.Pointer] and prty.tokentype_basename() not in Tokenizer.fundamentals():

        attr_readcallback = prty.attr_find(TokenType.ReadCallback)
        param_suppress_ref = attr_readcallback.param_named_of('SuppressRef')
        if param_suppress_ref is not None:

            # NOTE: SuppressRef implies return by the value that in its turn implies constness
            if not const:
                return None

            signature = f'{signature}const '
    else:
        signature = f'{signature}const ' if const else signature

    signature = f'{signature}{prty.tokentype.text} Get{prty.name}()'
    signature = f'{signature} const' if const else signature

    return signature

def _property_signature_setter(property: EpiProperty) -> str:
    pass

def emit_properties(properties: list, accessor_modifier: str, builder: Builder = Builder()) -> Builder:

    if len(properties) == 0:
        return builder

    builder.tab(-1)
    builder.line(f'{accessor_modifier}:')
    builder.tab()

    for p in properties:

        typename = p.tokentype.text
        value = f'{{{p.value}}}' if p.value is not None else ''

        builder.line(f'{typename} m_{p.name}{value};')

    builder.line_empty()

    return builder

def emit_property_callbacks(properties: list, accessor_modifier: str, builder: Builder = Builder()) -> Builder:

    if len(properties) == 0:
        return builder

    builder.tab(-1)
    builder.line(f'{accessor_modifier}:')
    builder.tab()

    for p in properties:

        attr_readcallback = p.attr_find(TokenType.ReadCallback)
        attr_writecallback = p.attr_find(TokenType.WriteCallback)

        ptype = p.tokentype.text
        if p.form == EpiProperty.Form.Array:
            ptype = f'{ptype}<{p.nestedtokentype.text}>'

        if attr_readcallback and not any(a.tokentype == TokenType.WriteOnly for a in p.attrs):

            pptype = ptype
            if pptype not in Tokenizer.BUILTIN_PRIMITIVE_TYPES and p.form != EpiProperty.Form.Pointer:

                if attr_readcallback.find_param('"SuppressRef"') is None:
                    pptype = f'const {pptype}&'

            builder.line(f'{pptype} Get{p.name}_Callback() const;')

        if attr_writecallback and not any(a.tokentype == TokenType.ReadOnly for a in p.attrs):

            pptype = ptype
            if pptype not in Tokenizer.BUILTIN_PRIMITIVE_TYPES and p.form != EpiProperty.Form.Pointer:

                if attr_writecallback.find_param('"SuppressRef"') is None:
                    pptype = f'const {pptype}&'

            builder.line(f'void Set{p.name}_Callback({pptype} value);')

    builder.line_empty()

    return builder

def emit_sekeleton_file(basename: str, ext: str) -> str:

    builder = Builder()

    if ext in ['cxx', 'hxx']:
        builder.template('header_comment')
    if ext == 'h':
        builder.template('h/header', filepath='filepath', basename=basename)
    elif ext == 'cpp':
        builder.template('cpp/header', module_name='module_name', filepath='filepath', basename=basename)
    elif ext == 'cxx':
        builder.template('cxx/header')

    builder.template('footer')

    return builder.build()

def emit_class_declaration(clss: EpiClass, builder: Builder = Builder()) -> Builder:

    clss_typeid = hex(zlib.crc32(clss.name.encode()) & 0xffffffff)
    builder.template('h/class_header', class_name=clss.name, class_typeid=clss_typeid)

    # pids
    builder.line(f'enum {clss.name}_PIDs')
    builder.line('{')
    builder.tab()

    for p in clss.properties:

        crc = hex(zlib.crc32(p.name.encode()) & 0xffffffff)
        builder.line(f'PID_{p.name} = {crc},')

    builder.line(f'PID_COUNT = {len(clss.properties)}')

    builder.tab(-1)
    builder.line('};')
    builder.line_empty()

    emit_property_callbacks(clss.properties, 'protected', builder)

    properties = [p for p in clss.properties if p.attr_find(TokenType.Virtual) is None]
    emit_properties(properties, 'protected', builder)

    builder.template('h/class_footer', class_name=clss.name)

    return builder

def emit_skeleton_class(clss: EpiClass, builder: Builder = Builder()) -> Builder:

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    builder.line(f'class {clss.name} : public {clss_parent}')
    builder.line('{')
    builder.anchor_gen_region(f'{clss.name}')

    emit_class_declaration(clss, builder)

    builder.anchor_gen_endregion(f'{clss.name}')
    builder.tab(-1)
    builder.line('};')
    builder.line_empty()

    return builder

def emit_class_serialization(clss: EpiClass, builder: Builder = Builder()) -> Builder:

    builder.template('cxx/class_serialization_header', class_name=clss.name)

    builder.tab()
    for p in clss.properties:

        if p.attr_find(TokenType.Transient) is None:
            builder.template('cxx/class_serialization_property', property_name=p.name)

    builder.tab(-1)
    builder.line('}')
    builder.line_empty()

    builder.template('cxx/class_deserialization_header', class_name=clss.name)

    builder.tab()
    for p in clss.properties:

        if p.attr_find(TokenType.Transient) is None:
            builder.template('cxx/class_deserialization_property', property_name=p.name)

    builder.tab(-1)
    builder.line('}')
    builder.line_empty()

    return builder

def emit_class_meta(clss: EpiClass, builder: Builder = Builder()) -> Builder:

    builder.template('cxx/class_meta_header', class_name=clss.name)

    for p in clss.properties:

        p_nested_typeid = 'MetaTypeID_None'

        # TODO: make it work for >1 template arguments
        if p.form == EpiProperty.Form.Template:
            p_nested_typeid = f'epiHashCompileTime({p.tokens_nested[0].text})'

        p_typeid = f'epiHashCompileTime({p.tokentype_basename()})'

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
                         class_name=clss.name,
                         property_typeid=p_typeid,
                         property_nested_typeid=p_nested_typeid,
                         property_flags=' | '.join(flags),
                         property_ptr_read=p_ptr_read,
                         property_ptr_write=p_ptr_write)

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    builder.template('cxx/class_meta_footer', class_name=clss.name, class_parent_name=clss_parent)

    return builder

def emit_class_declaration_hidden(clss: EpiClass, builder: Builder = Builder()) -> Builder:

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    builder.template('hxx/class_hidden_header', class_name=clss.name, class_parent_name=clss_parent)

    # getters/setters
    for p in clss.properties:

        ptype = p.tokentype.text

        if p.form == EpiProperty.Form.Array:
            ptype = f'{ptype}<{p.nestedtokentype.text}>'

        body_prologue_set = ''
        body_epilogue_set = f'm_{p.name} = value;'
        body_prologue_get = ''
        body_epilogue_get = f'return m_{p.name};'

        for a in p.attrs:

            if a.tokentype == TokenType.ExpectMin:

                v = a.params[0].text
                body_prologue_set = f'{body_prologue_set}epiExpect(value >= {v});'

            elif a.tokentype == TokenType.ExpectMax:

                v = a.params[0].text
                body_prologue_set = f'{body_prologue_set}epiExpect(value <= {v});'

            elif a.tokentype == TokenType.ForceMin:

                v = a.params[0].text
                body_prologue_set = f'{body_prologue_set}value = std::max(value, {v});'

            elif a.tokentype == TokenType.ForceMax:

                v = a.params[0].text
                body_prologue_set = f'{body_prologue_set}value = std::min(value, {v});'

            elif a.tokentype == TokenType.ReadCallback:
                body_epilogue_get = f'return Get{p.name}_Callback();'

            elif a.tokentype == TokenType.WriteCallback:
                body_epilogue_set = f'Set{p.name}_Callback(value);'

        body_get = f'{body_prologue_get}{body_epilogue_get}'
        body_set = f'{body_prologue_set}{body_epilogue_set}'

        # TODO: add `inline` if no read/write callback attribute present

        if not any(a.tokentype == TokenType.WriteOnly for a in p.attrs):

            pptype = ptype
            if pptype not in Tokenizer.BUILTIN_PRIMITIVE_TYPES and p.form != EpiProperty.Form.Pointer:

                attr_readcallback = p.attr_find(TokenType.ReadCallback)
                if not attr_readcallback or attr_readcallback.find_param('"SuppressRef"') is None:

                    if not attr_readcallback:
                        builder.line(f'{pptype}& Get{p.name}() {{ {body_get} }} \\')

                    pptype = f'const {pptype}&'

            builder.line(f'{pptype} Get{p.name}() const {{ {body_get} }} \\')

        if not any(a.tokentype == TokenType.ReadOnly for a in p.attrs):

            pptype = ptype
            if ptype not in Tokenizer.BUILTIN_PRIMITIVE_TYPES and p.form != EpiProperty.Form.Pointer:

                attr_writecallback = p.attr_find(TokenType.WriteCallback)
                if not attr_writecallback or attr_writecallback.find_param('"SuppressRef"') is None:
                    pptype = f'const {pptype}&'

            builder.line(f'void Set{p.name}({pptype} value) {{ {body_set} }} \\')

    builder.line('\\')

    # pidx
    builder.line(f'enum {clss.name}_PIDXs \\')
    builder.line('{ \\')
    builder.tab()

    for i, p in enumerate(clss.properties):
        builder.line(f'PIDX_{p.name} = {i}, \\')

    builder.line(f'PIDX_COUNT = {len(clss.properties)} \\')

    builder.tab(-1)
    builder.line('}; \\')

    builder.line(' \\')
    builder.line('private: \\')

    # getters/setters function pointers
    for p in clss.properties:

        ptype = p.tokentype.text

        if p.form == EpiProperty.Form.Array:
            ptype = f'{ptype}<{p.nestedtokentype.text}>'

        attr_readcallback = p.attr_find(TokenType.ReadCallback)
        attr_writecallback = p.attr_find(TokenType.WriteCallback)
        attr_readonly = p.attr_find(TokenType.ReadOnly)
        attr_writeonly = p.attr_find(TokenType.WriteOnly)

        if attr_readcallback is not None and attr_writeonly is None:

            if ptype not in Tokenizer.BUILTIN_PRIMITIVE_TYPES and p.form != EpiProperty.Form.Pointer and attr_readcallback.find_param('"SuppressRef"') is None:
                builder.line(f'const {ptype}& ({clss.name}::*Get{p.name}_FuncPtr)() const {{ &{clss.name}::Get{p.name} }}; \\')
            else:
                builder.line(f'{ptype} ({clss.name}::*Get{p.name}_FuncPtr)() const {{ &{clss.name}::Get{p.name} }}; \\')

        if attr_writecallback is not None and attr_readonly is None:

            if ptype not in Tokenizer.BUILTIN_PRIMITIVE_TYPES and p.form != EpiProperty.Form.Pointer and attr_writecallback.find_param('"SuppressRef"') is None:
                builder.line(f'void ({clss.name}::*Set{p.name}_FuncPtr)(const {ptype}&) {{ &{clss.name}::Set{p.name} }}; \\')
            else:
                builder.line(f'void ({clss.name}::*Set{p.name}_FuncPtr)({ptype}) {{ &{clss.name}::Set{p.name} }}; \\')

    builder.line_empty()
    builder.line_empty()

    return builder

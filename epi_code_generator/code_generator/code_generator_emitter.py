from .code_generator_builder import Builder

from ..tokenizer import TokenType
from ..tokenizer import Tokenizer

from ..symbol import EpiClass
from ..symbol import EpiProperty

import zlib


def emit_properties(properties: list, accessor_modifier: str, builder: Builder = Builder()) -> Builder:

    if len(properties) == 0:
        return builder

    builder.tab(-1)
    builder.line(f'{accessor_modifier}:')
    builder.tab()

    for p in properties:

        typename = f'{p.tokentype.text}'
        if p.form == EpiProperty.Form.Array:
            typename = f'{typename}<{p.nestedtokentype.text}>'
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

        attr_readcallback = p.find_attr(TokenType.ReadCallback)
        attr_writecallback = p.find_attr(TokenType.WriteCallback)

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

    if ext == 'h':

        builder.line('#pragma once')
        builder.line_empty()

    if ext in ['cxx', 'hxx']:
        header = \
'''
/*                                                      */
/*  ______       _                                      */
/* |  ____|     (_)                                     */
/* | |__   _ __  _                                      */
/* |  __| | '_ \| |   THIS FILE IS AUTO-GENERATED       */
/* | |____| |_) | |   manual changes won't be saved     */
/* |______| .__/|_|                                     */
/*        | |                                           */
/*        |_|                                           */
/*                                                      */
'''

        builder.line(header.strip())
        builder.line_empty()

    if ext in ['cpp', 'h']:

        builder.anchor_gen_region('include')

        if ext == 'cpp':
            builder.line(f'#include "{basename}.h"')
            builder.line(f'#include "{basename}.cxx"')
        elif ext == 'h':
            builder.line(f'#include "{basename}.hxx"')

        builder.anchor_gen_endregion('include')
        builder.line_empty()

    if ext in ['cxx', 'cpp', 'h']:

        builder.anchor_namespace_begin()
        builder.line_empty()
        builder.anchor_namespace_end()
        builder.line_empty()

    return builder.build()

def emit_class_declaration(clss: EpiClass, builder: Builder = Builder()) -> Builder:

    builder.line_empty()
    builder.line(f'EPI_GENHIDDEN_{clss.name}()')
    builder.line_empty()
    builder.line('public:')
    builder.tab()

    crc = hex(zlib.crc32(clss.name.encode()) & 0xffffffff)
    builder.line(f'constexpr static MetaTypeID TypeID{{{crc}}};')
    builder.line_empty()

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

    filter_properties_non_virtual = lambda p: not any(a.tokentype in [
        TokenType.Virtual,
    ] for a in p.attrs)

    filter_properties_cb = lambda p: any(a.tokentype in [
        TokenType.ReadCallback,
        TokenType.WriteCallback
    ] for a in p.attrs)

    filter_properties_non_private = lambda p: not any(a.tokentype in [
        TokenType.Private
    ] for a in p.attrs)

    filter_properties_private = lambda p: any(a.tokentype in [
        TokenType.Private
    ] for a in p.attrs)

    properties_cb = list(filter(filter_properties_cb, clss.properties))
    properties_non_private = list(filter(filter_properties_non_private, properties_cb))
    properties_private = list(filter(filter_properties_private, properties_cb))

    emit_property_callbacks(properties_non_private, 'protected', builder)
    emit_property_callbacks(properties_private, 'private', builder)

    properties_non_virtual = list(filter(filter_properties_non_virtual, clss.properties))
    properties_non_private = list(filter(filter_properties_non_private, properties_non_virtual))
    properties_private = list(filter(filter_properties_private, properties_non_virtual))

    emit_properties(properties_non_private, 'protected', builder)
    emit_properties(properties_private, 'private', builder)

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

    builder.line(f'void {clss.name}::Serialization(json_t& json)')
    builder.line('{')
    builder.tab()
    builder.line('super::Serialization(json);')
    builder.line_empty()

    for p in clss.properties:

        if not any(a.tokentype == TokenType.Transient for a in p.attrs):
            builder.line(f'epiSerialize({p.name}, json);')

    builder.tab(-1)
    builder.line('}')
    builder.line_empty()

    builder.line(f'void {clss.name}::Deserialization(const json_t& json)')
    builder.line('{')
    builder.tab()
    builder.line('super::Deserialization(json);')
    builder.line_empty()

    for p in clss.properties:

        if not any(a.tokentype == TokenType.Transient for a in p.attrs):
            builder.line(f'epiDeserialize({p.name}, json);')

    builder.tab(-1)
    builder.line('}')
    builder.line_empty()

    return builder

def emit_class_meta(clss: EpiClass, builder: Builder = Builder()) -> Builder:

    # TODO: make it constexpr
    builder.line(f'MetaClass {clss.name}::EmitMetaClass()')
    builder.line('{')
    builder.tab()
    builder.line('MetaClassData data;')
    builder.line_empty()

    for p in clss.properties:

        hash_typenested = '0'
        if p.form == EpiProperty.Form.Template:
            hash_typenested = f'epiHashCompileTime({p.nestedtokentype.text})'

        hash_type = f'epiHashCompileTime({p.tokentype_basename()})'

        flags = []

        attr_readcallback = p.find_attr(TokenType.ReadCallback)
        attr_writecallback = p.find_attr(TokenType.WriteCallback)
        attr_readonly = p.find_attr(TokenType.ReadOnly)
        attr_writeonly = p.find_attr(TokenType.WriteOnly)

        if attr_readcallback is not None:
            flags.append('ReadCallback')
        if attr_writecallback is not None:
            flags.append('WriteCallback')
        if attr_readonly is not None:
            flags.append('ReadOnly')
        if attr_writeonly is not None:
            flags.append('WriteOnly')

        builder.line('{')
        builder.tab()
        builder.line('MetaProperty m = epiMetaProperty(')
        builder.tab()
        builder.line(f'/* Name */ "{p.name}",')

        ptrread = '/* PtrRead */ nullptr,'
        if attr_writeonly is None:
            if attr_readcallback is None:
                ptrread = f'/* PtrRead */ (void*)offsetof({clss.name}, m_{p.name}),'
            elif attr_writeonly is None:
                ptrread = f'/* PtrRead */ (void*)offsetof({clss.name}, Get{p.name}_FuncPtr),'

        builder.line(ptrread)

        ptrwrite = '/* PtrWrite */ nullptr,'
        if attr_readonly is None:
            if attr_writecallback is None:
                ptrwrite = f'/* PtrWrite */ (void*)offsetof({clss.name}, m_{p.name}),'
            else:
                ptrwrite = f'/* PtrWrite */ (void*)offsetof({clss.name}, Set{p.name}_FuncPtr),'

        builder.line(ptrwrite)

        flags = [f'MetaProperty::Flags::Mask{f}' for f in flags]
        builder.line(f'/* Flags */ {{{ " | ".join(flags) }}},')
        builder.line(f'/* typeID */ {hash_type},')
        builder.line(f'/* nestedTypeID */ {hash_typenested}')
        builder.tab(-1)
        builder.line(');')
        builder.line(f'data.AddProperty(epiHashCompileTime({p.name}), std::move(m));')
        builder.tab(-1)
        builder.line('}')

    builder.line_empty()

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    hash_parent = f'epiHashCompileTime({clss_parent})'
    hash_clss = f'epiHashCompileTime({clss.name})'
    builder.line(f'return MetaClass(std::move(data), {hash_clss}, {hash_parent}, sizeof({clss.name}), "{clss.name}");')

    builder.tab(-1)
    builder.line('}')
    builder.line_empty()

    return builder

def emit_class_declaration_hidden(clss: EpiClass, builder: Builder = Builder()) -> Builder:

    clss_parent = clss.parent if clss.parent is not None else 'Object'
    builder.line(f'#define EPI_GENHIDDEN_{clss.name}() \\')
    builder.line('public: \\')

    content = \
f'''

using super = {clss_parent};

static MetaClass EmitMetaClass();

const MetaClass& GetMetaClass() const override
{{
super::GetMetaClass();
return ClassRegistry_GetMetaClass<{clss.name}>();
}}

epiBool Is(MetaTypeID rhs) const override
{{
return rhs == {clss.name}::TypeID || super::Is(rhs);
}}

void Serialization(json_t& json) override;
void Deserialization(const json_t& json) override;

'''
    builder.line(' \\\n'.join(content.strip().split('\n')) + ' \\')
    builder.line('\\')

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

                attr_readcallback = p.find_attr(TokenType.ReadCallback)
                if not attr_readcallback or attr_readcallback.find_param('"SuppressRef"') is None:

                    if not attr_readcallback:
                        builder.line(f'{pptype}& Get{p.name}() {{ {body_get} }} \\')

                    pptype = f'const {pptype}&'

            builder.line(f'{pptype} Get{p.name}() const {{ {body_get} }} \\')

        if not any(a.tokentype == TokenType.ReadOnly for a in p.attrs):

            pptype = ptype
            if ptype not in Tokenizer.BUILTIN_PRIMITIVE_TYPES and p.form != EpiProperty.Form.Pointer:

                attr_writecallback = p.find_attr(TokenType.WriteCallback)
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

        attr_readcallback = p.find_attr(TokenType.ReadCallback)
        attr_writecallback = p.find_attr(TokenType.WriteCallback)
        attr_readonly = p.find_attr(TokenType.ReadOnly)
        attr_writeonly = p.find_attr(TokenType.WriteOnly)

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

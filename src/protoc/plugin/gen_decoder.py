import gen_util as util

def gen_main_decoder(msg, parent_struct_name):
    return (
        "  function decode(bytes bs) internal constant returns ({name}) {{\n"
        "    var (x,) = _decode(32, bs, bs.length);                       \n"
        "    return x;                                                    \n"
        "  }}"
    ).format(
        name = util.gen_internal_struct_name(msg, parent_struct_name)
    )

def gen_inner_field_decoder(field, parent_struct_name, first_pass):
    args = ""
    repeated = util.field_is_repeated(field)
    if repeated:
        if first_pass:
            args = "p, bs, nil(), counters"
        else:
            args = "p, bs, r, counters"
    else:
        if first_pass:
            args = "p, bs, r, counters"
        else:
            args = "p, bs, nil(), counters"

    return (
        "      else if(fieldId == {id})       \n"
        "          p += _read_{field}({args});\n"
    ).format(
        id = field.number,
        field = field.name,
        args = args,
    )

def gen_inner_fields_decoder(msg, parent_struct_name, first_pass):
    return (
        "if (false) {{}}\n"
        "{codes}"
        "      else revert();"
    ).format(
        codes = ''.join(list(map((lambda f: gen_inner_field_decoder(f, parent_struct_name, first_pass)), msg.field))),
    )

def gen_inner_array_allocator(f, parent_struct_name):
    return (
        "    r.{field} = new {t}(counters[{i}]);\n"
    ).format(
        t = util.gen_global_type_from_field(f),
        field = f.name,
        i = f.number,
    )

def gen_inner_arraty_allocators(msg, parent_struct_name):
    return ''.join(list(map(
        (lambda f: gen_inner_array_allocator(f, parent_struct_name) if util.field_is_repeated(f) else ""), msg.field)))

def gen_inner_decoder(msg, parent_struct_name):
    return (
        "  function _decode(uint p, bytes bs, uint sz)                   \n"
        "      internal constant returns ({struct}, uint) {{             \n"
        "    {struct} memory r;                                          \n"
        "    uint[{n}] memory counters;                                  \n"
        "    uint fieldId;                                               \n"
        "    _pb.WireType wireType;                                      \n"
        "    uint bytesRead;                                             \n"
        "    uint offset = p;                                            \n"
        "    while(p < offset+sz) {{                                     \n"
        "      (fieldId, wireType, bytesRead) = _pb._decode_key(p, bs);  \n"
        "      p += bytesRead;                                           \n"
        "      {first_pass}                                              \n"
        "    }}                                                          \n"
        "    p = offset;                                                 \n"
        "{allocators}                                                    \n"
        "    while(p < offset+sz) {{                                     \n"
        "      (fieldId, wireType, bytesRead) = _pb._decode_key(p, bs);  \n"
        "      p += bytesRead;                                           \n"
        "      {second_pass}                                             \n"
        "    }}                                                          \n"
        "    return (r, sz);                                             \n"
        "  }}                                                            \n"
    ).format(
        struct=util.gen_internal_struct_name(msg, parent_struct_name),
        n=len(msg.field) + 1,
        first_pass=gen_inner_fields_decoder(msg, parent_struct_name, True),
        allocators=gen_inner_arraty_allocators(msg, parent_struct_name),
        second_pass=gen_inner_fields_decoder(msg, parent_struct_name, False),
    )


def gen_field_reader(f, parent_struct_name, msg):
    suffix = ("[ r.{field}.length - counters[{i}] ]").format(field = f.name, i = f.number) if util.field_is_repeated(f) else ""
    return (
        "  function _read_{field}(uint p, bytes bs, {t} r, uint[{n}] counters) internal constant returns (uint) {{                            \n"
        "    var (x, sz) = {decoder}(p, bs);                                  \n"
        "    if(isNil(r)) {{                                                  \n" 
        "      counters[{i}] += 1;                                            \n"
        "    }} else {{                                                         \n"
        "      r.{field}{suffix} = x;                                         \n"
        "      if(counters[{i}] > 0) counters[{i}] -= 1;                      \n"
        "    }}                                                                \n"
        "    return sz;                                                       \n"
        "  }}                                                                 \n"
    ).format(
        field = f.name,
        decoder = util.gen_decoder_name(f),
        t = util.gen_internal_struct_name(msg, parent_struct_name),
        i = f.number,
        n = len(msg.field) + 1,
        suffix = suffix,
    )


def gen_field_readers(msg, parent_struct_name):
    return ''.join(list(map(lambda f: gen_field_reader(f, parent_struct_name, msg), msg.field)))

def gen_struct_decoder(f, msg, parent_struct_name):
    return (
        "  function {name}(uint p, bytes bs)            \n"
        "      internal constant returns ({struct}, uint) {{    \n"
        "    var (sz, bytesRead) = _pb._decode_varint(p, bs);   \n"
        "    p += bytesRead;                                    \n"
        "    var (r,) = {lib}._decode(p, bs, sz);               \n"
        "    return (r, sz + bytesRead);                        \n"
        "  }}      \n"
    ).format(
        struct = util.gen_global_type_name_from_field(f),
        name = util.gen_struct_decoder_name_from_field(f),
        lib = util.gen_struct_codec_lib_name_from_field(f)
    )

def gen_struct_decoders(msg, parent_struct_name):
    return ''.join(list(map(
        (lambda f: gen_struct_decoder(f, msg, parent_struct_name) if util.field_is_message(f) else ""), msg.field)))


def gen_decoder_section(msg, parent_struct_name):
    return (
        "  // Decoder section                       \n"
        "{main_decoder}                             \n"
        "  // innter decoder                       \n"
        "{inner_decoder}                            \n"
        "  // field readers                       \n"
        "{field_readers}                            \n"
        "  // struct decoder                       \n"
        "{struct_decoders}                          "
    ).format(
        main_decoder = gen_main_decoder(msg, parent_struct_name),
        inner_decoder = gen_inner_decoder(msg, parent_struct_name),
        field_readers = gen_field_readers(msg, parent_struct_name),
        struct_decoders = gen_struct_decoders(msg, parent_struct_name),
    )
#!/usr/bin/env python

import os, sys

import pprint
pp = pprint.PrettyPrinter(indent=4, stream=sys.stderr)

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf.descriptor_pb2 import DescriptorProto, EnumDescriptorProto

from gen_decoder import gen_decoder_section
from gen_encoder import gen_encoder_section
import gen_util as util

def gen_fields(msg):
    return '\n'.join(list(map((lambda f: ("    {type} {name};").format(type=util.gen_fieldtype(f), name=f.name)), msg.field)))


def gen_map_fields_decl_for_field(f, nested_type):
    return ("    mapping({key_type} => uint) _{name}_map;").format(
        name=f.name,
        key_type=util.gen_global_type_name_from_field(nested_type.field[0]),
        container_type=util.gen_global_type_name_from_field(f)
    );

def gen_nested_struct_name(nested_type, parent_msg, parent_struct_name):
    flagments = [util.current_package_name(), parent_struct_name, parent_msg.name, nested_type.name] if parent_struct_name else [util.current_package_name(), parent_msg.name, nested_type.name]
    pb_nested_struct_name = "_".join(flagments)
    if pb_nested_struct_name[0] == '_':
        pb_nested_struct_name = pb_nested_struct_name[1:]
    return pb_nested_struct_name    

def gen_map_fields_helper(nested_type, parent_msg, parent_struct_name):
    if nested_type.options and nested_type.options.map_entry:
        pb_nested_struct_name = gen_nested_struct_name(nested_type, parent_msg, parent_struct_name)
        map_fields = list(filter(
            lambda f: util.gen_struct_name_from_field(f) == pb_nested_struct_name, 
            parent_msg.field))
        return '\n'.join(list(map(lambda f: gen_map_fields_decl_for_field(f, nested_type), map_fields)))
    else:
        return ''

def gen_map_fields(msg, parent_struct_name):
    return '\n'.join(list(map((lambda nt: gen_map_fields_helper(nt, msg, parent_struct_name)), msg.nested_type)))

# below gen_* codes for generating external library
def gen_struct_definition(msg, parent_struct_name):
    return (
        "  //struct definition\n"
        "  struct Data {{     \n"
        "{fields}             \n" # TODO. add indent for 2nd+ field
        "    //non serialized field for map\n"
        "{map_fields}         \n"
        "  }}                 "
    ).format(
        fields=gen_fields(msg),
        map_fields=gen_map_fields(msg, parent_struct_name)
    )

def gen_enums(msg):
    return '\n'.join(list(map(util.gen_enumtype, msg.enum_type)))

# below gen_* codes for generating internal library
def gen_enum_definition(msg, parent_struct_name):
    return (
        "  //enum definition\n"
        "  {enums}"
    ).format(
        enums=gen_enums(msg)
    )

# below gen_* codes for generating internal library
def gen_utility_functions(msg, parent_struct_name):
    return (
        "  //utility functions                                           \n"
        "  function nil() internal pure returns ({name} r) {{        \n"
        "    assembly {{ r := 0 }}                                       \n"
        "  }}                                                            \n"
        "  function isNil({name} x) internal pure returns (bool r) {{\n"
        "    assembly {{ r := iszero(x) }}                               \n"
        "  }}                                                            \n"
    ).format(
        name=util.gen_internal_struct_name(msg, parent_struct_name)
    );

def gen_map_insert_on_store(f, parent_msg, parent_struct_name):
    for nt in parent_msg.nested_type:
        if nt.options and nt.options.map_entry:
            pb_nested_struct_name = gen_nested_struct_name(nt, parent_msg, parent_struct_name)
            if util.gen_struct_name_from_field(f) == pb_nested_struct_name:
                return ('output._{name}_map[input.{name}[i{i}].key] = uint32(i{i}+1);\n').format(
                    name = f.name,
                    i = f.number,
                )
    return ''

def gen_store_code_for_field(f, msg, parent_struct_name):
    tmpl = ""
    if util.field_is_message(f) and util.field_is_repeated(f):
        tmpl = (
            "    output.{field}.length = input.{field}.length;             \n"
            "    for(uint i{i}=0; i{i}<input.{field}.length; i{i}++) {{    \n"
            "      {lib}.store(input.{field}[i{i}], output.{field}[i{i}]); \n"
            "      {map_insert_code}"
            "    }}"
        )
    elif util.field_is_message(f):
        tmpl = (
            "    {lib}.store(input.{field}, output.{field});               \n"
        )
    else:
        return (
            "    output.{field} = input.{field};                           \n" 
        ).format(
            field = f.name,
        )

    libname = util.gen_struct_codec_lib_name_from_field(f)

    return tmpl.format(
        i = f.number,
        field = f.name,
        lib = libname,
        map_insert_code = gen_map_insert_on_store(f, msg, parent_struct_name)
    )

def gen_store_codes(msg, parent_struct_name):
    return ''.join(list(map((lambda f: gen_store_code_for_field(f, msg, parent_struct_name)), msg.field)))

def gen_store_function(msg, parent_struct_name):
    return (
        "  //store function                                                     \n"
        "  function store({name} memory input, {name} storage output) internal{{\n"
        "{store_codes}\n"
        "  }}                                                                   \n"
    ).format(
        name=util.gen_internal_struct_name(msg, parent_struct_name),
        store_codes=gen_store_codes(msg, parent_struct_name)
    );

def gen_value_copy_code(value_field, dst_flagment):
    if util.field_is_message(value_field):
        return ("{struct_name}.store(value, {dst}.value);").format(
            struct_name = util.gen_struct_codec_lib_name_from_field(value_field),
            dst = dst_flagment,
        )
    else:
        return ("{dst}.value = value;").format(dst = dst_flagment)

def gen_map_helper_codes_for_field(f, nested_type):
    kf = nested_type.field[0]
    vf = nested_type.field[1]
    return ("""  //map helpers for {name}
  function get_{name}(Data storage self, {key_type} key) internal view returns ({value_type} {storage_type}) {{
    return {val_name}[{map_name}[key] - 1].value;
  }}
  function search_{name}(Data storage self, {key_type} key) internal view returns (bool, {value_type} {storage_type}) {{
    if ({map_name}[key] <= 0) {{ return (false, {val_name}[0].value); }}
    return (true, {val_name}[{map_name}[key] - 1].value);
  }}                                                                  
  function add_{name}(Data storage self, {key_type} key, {value_type} value) internal {{
    if ({map_name}[key] != 0) {{
      {copy_value_exists}
    }} else {{
      {val_name}.length++;
      {val_name}[{val_name}.length - 1].key = key;
      {copy_value_new}
      {map_name}[key] = {val_name}.length;
    }}
  }}
  function rm_{name}(Data storage self, {key_type} key) internal {{
    uint pos = {map_name}[key];
    if (pos == 0) {{
      return;
    }}
    {val_name}[pos - 1] = {val_name}[{val_name}.length - 1];
    {val_name}.length--;
    delete {map_name}[key];
  }}
"""
    ).format(
        name = f.name,
        val_name="self.{0}".format(f.name),
        map_name = "self._{0}_map".format(f.name),
        key_type=util.gen_global_type_name_from_field(kf),
        value_type=util.gen_global_type_name_from_field(vf),
        storage_type="storage" if (util.field_is_repeated(vf) or util.field_is_message(vf)) else "",
        container_type=util.gen_global_type_name_from_field(f),
        copy_value_exists=gen_value_copy_code(vf, ("self.{0}[self._{0}_map[key] - 1]").format(f.name)),
        copy_value_new=gen_value_copy_code(vf, ("self.{0}[self.{0}.length - 1]").format(f.name)),
    );

def gen_map_helper(nested_type, parent_msg, parent_struct_name):
    if nested_type.options and nested_type.options.map_entry:
        pb_nested_struct_name = gen_nested_struct_name(nested_type, parent_msg, parent_struct_name)
        map_fields = list(filter(
            lambda f: util.gen_struct_name_from_field(f) == pb_nested_struct_name, 
            parent_msg.field))
        return''.join(list(map(lambda f: gen_map_helper_codes_for_field(f, nested_type), map_fields)));
    else:
        return ''

def gen_map_helpers(msg, parent_struct_name):
    return ''.join(list(map((lambda nt: gen_map_helper(nt, msg, parent_struct_name)), msg.nested_type)))


def gen_codec(msg, main_codecs, delegate_codecs, parent_struct_name = None):
    #sys.stderr.write(('----------------------- get codec ({0}) --------------------------').format(parent_struct_name))
    #pp.pprint(msg)
    #codes = gen_map_helpers(msg, parent_struct_name)
    #pp.pprint('helper_codes = {0}'.format(codes))

    delegate_lib_name = util.gen_delegate_lib_name(msg, parent_struct_name)

    # delegate codec
    delegate_codecs.append((
        "library {delegate_lib_name}{{\n"
        "{enum_definition}            \n"
        "{struct_definition}          \n"
        "{decoder_section}            \n"
        "{encoder_section}            \n"
        "{store_function}             \n"
        "{map_helper}                 \n"
        "{utility_functions}"
        "}} //library {delegate_lib_name}\n"
    ).format(
        delegate_lib_name=delegate_lib_name, 
        enum_definition=gen_enum_definition(msg, parent_struct_name),
        struct_definition=gen_struct_definition(msg, parent_struct_name),
        decoder_section=gen_decoder_section(msg, parent_struct_name),
        encoder_section=gen_encoder_section(msg, parent_struct_name),
        store_function=gen_store_function(msg, parent_struct_name),
        map_helper = gen_map_helpers(msg, parent_struct_name),
        utility_functions=gen_utility_functions(msg, parent_struct_name)
    ))

    for nested in msg.nested_type:
        gen_codec(nested, main_codecs, delegate_codecs, util.add_prefix(parent_struct_name, msg.name))



SOLIDITY_NATIVE_TYPEDEFS = "Solidity.proto"
RUNTIME_FILE_NAME = "runtime.sol"
GEN_RUNTIME = False
COMPILE_META_SCHEMA = False
def apply_options(params_string):
    params = util.parse_urllike_parameter(params_string)
    if "gen_runtime" in params:
        global GEN_RUNTIME
        GEN_RUNTIME = True
        name = params["gen_runtime"]
        if name.endswith(".sol"):
            global RUNTIME_FILE_NAME
            RUNTIME_FILE_NAME = name
    if "pb_libname" in params:
        util.change_pb_libname_prefix(params["pb_libname"])
    if "for_linking" in params:
        sys.stderr.write("warning: for_linking option is still under experiment due to slow-pace of solidity development\n")
        util.set_library_linking_mode()
    if "gen_internal_lib" in params:
        util.set_internal_linking_mode()
    if "use_builtin_enum" in params:
        sys.stderr.write("warning: use_builtin_enum option is still under experiment because we cannot set value to solidity's enum\n")
        util.set_enum_as_constant(True)
    if "compile_meta_schema" in params:
        global COMPILE_META_SCHEMA
        COMPILE_META_SCHEMA = True

def generate_code(request, response):
    generated = 0

    apply_options(request.parameter)
    
    for proto_file in request.proto_file:
        # skip google.protobuf namespace
        if (proto_file.package == "google.protobuf") and (not COMPILE_META_SCHEMA):
            continue
        # skip native solidity type definition
        if SOLIDITY_NATIVE_TYPEDEFS in proto_file.name:
            continue
        # main output
        output = []

        # set package name if any
        util.change_package_name(proto_file.package)

        # generate sol library
        # prologue
        output.append('pragma solidity ^{0};'.format(util.SOLIDITY_VERSION))
        for pragma in util.SOLIDITY_PRAGMAS:
            output.append('{0};'.format(pragma))
        output.append('import "./{0}";'.format(RUNTIME_FILE_NAME))
        for dep in proto_file.dependency:
            if SOLIDITY_NATIVE_TYPEDEFS in dep:
                continue
            if ("google/protobuf" in dep) and (not COMPILE_META_SCHEMA):
                continue
            output.append('import "./{0}";'.format(dep.replace('.proto', '_pb.sol')))

        # generate per message codes
        main_codecs = []
        delegate_codecs = []
        for msg in proto_file.message_type:
            gen_codec(msg, main_codecs, delegate_codecs)
        
        # epilogue
        output = output + delegate_codecs
      

        if len(delegate_codecs) > 0: # if it has any contents, output pb.sol file
            # Fill response
            basepath = os.path.basename(proto_file.name)
            f = response.file.add()
            f.name = basepath.replace('.proto', '_pb.sol')
            f.content = '\n'.join(output)
            # increase generated file count
            generated = generated + 1

    if generated > 0 and GEN_RUNTIME:
        try:
            with open('/protoc/plugin/runtime/runtime.sol', 'r') as runtime:
                rf = response.file.add()
                rf.name = RUNTIME_FILE_NAME
                rf.content = runtime.read()
        except Exception as e:
            sys.stderr.write(
                "required to generate solidity runtime at {} but cannot open runtime with error {}\n".format(
                    RUNTIME_FILE_NAME, e
                )
            )

if __name__ == '__main__':
    # Read request message from stdin
    data = sys.stdin.read()

    # Parse request
    request = plugin.CodeGeneratorRequest()
    request.ParseFromString(data)

    # pp.pprint(request)

    # Create response
    response = plugin.CodeGeneratorResponse()

    # Generate code
    generate_code(request, response)

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    sys.stdout.write(output)
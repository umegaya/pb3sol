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

# below gen_* codes for generating external library
def gen_struct_definition(msg, parent_struct_name):
    return (
        "  //struct definition\n"
        "  struct Data {{   \n"
        "{fields}             \n" # TODO. add indent for 2nd+ field
        "  }}                 "
    ).format(
        fields=gen_fields(msg)
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

def gen_store_code_for_field(f, parent_struct_name):
    tmpl = ""
    if util.field_is_message(f) and util.field_is_repeated(f):
        tmpl = (
            "    output.{field}.length = input.{field}.length;             \n"
            "    for(uint i{i}=0; i{i}<input.{field}.length; i{i}++)       \n"
            "      {lib}.store(input.{field}[i{i}], output.{field}[i{i}]); \n"
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
    )

def gen_store_codes(msg, parent_struct_name):
    return ''.join(list(map((lambda f: gen_store_code_for_field(f, parent_struct_name)), msg.field)))

def gen_store_function(msg, parent_struct_name):
    return (
        "  //store function                                                     \n"
        "  function store({name} memory input, {name} storage output) internal{{\n"
        "{store_codes}"
        "  }}                                                                   \n"
    ).format(
        name=util.gen_internal_struct_name(msg, parent_struct_name),
        store_codes=gen_store_codes(msg, parent_struct_name)
    );

def gen_codec(msg, main_codecs, delegate_codecs, parent_struct_name = None):
    #sys.stderr.write(('----------------------- get codec ({0}) --------------------------').format(parent_struct_name))
    #pp.pprint(msg)

    delegate_lib_name = util.gen_delegate_lib_name(msg, parent_struct_name)

    # delegate codec
    delegate_codecs.append((
        "library {delegate_lib_name}{{\n"
        "{struct_definition}          \n"
        "{decoder_section}            \n"
        "{encoder_section}            \n"
        "{store_function}             \n"
        "{utility_functions}"
        "}} //library {delegate_lib_name}\n"
    ).format(
        delegate_lib_name=delegate_lib_name, 
        struct_definition=gen_struct_definition(msg, parent_struct_name),
        decoder_section=gen_decoder_section(msg, parent_struct_name),
        encoder_section=gen_encoder_section(msg, parent_struct_name),
        store_function=gen_store_function(msg, parent_struct_name),
        utility_functions=gen_utility_functions(msg, parent_struct_name)
    ))

    for nested in msg.nested_type:
        gen_codec(nested, main_codecs, delegate_codecs, util.add_prefix(parent_struct_name, msg.name))



SOLIDITY_NATIVE_TYPEDEFS = "Solidity.proto"
RUNTIME_FILE_NAME = "runtime.sol"
GEN_RUNTIME = False
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
        util.set_lib_linking_mode()

def generate_code(request, response):
    generated = 0

    apply_options(request.parameter)
    
    for proto_file in request.proto_file:
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
        output.append('import "./{0}";'.format(RUNTIME_FILE_NAME))
        for dep in proto_file.dependency:
            if SOLIDITY_NATIVE_TYPEDEFS in dep:
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
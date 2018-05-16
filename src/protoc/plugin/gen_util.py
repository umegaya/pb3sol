import re, sys
import pprint
pp = pprint.PrettyPrinter(indent=4, stream=sys.stderr)


Label2Value = {
    "LABEL_OPTIONAL": 1,
    "LABEL_REQUIRED": 2,
    "LABEL_REPEATED": 3,
}

Num2Type = {
    1: "double",
    2: "float",
    3: "int64",    # not zigzag (proto3 compiler does not seem to use it)
    4: "uint64",
    5: "int32",    # not zigzag (proto3 compiler does not seem to use it)
    6: "uint64", 
    7: "uint32",
    8: "bool",
    9: "string",
    10: None, #"group",   # group (deprecated in proto3)
    11: None, #"message", # another messsage
    12: "bytes",   # bytes
    13: "uint32",
    14: "enum",
    15: "int32", 
    16: "int64",
    17: "int32", # Uses ZigZag encoding.
    18: "int64", # Uses ZigZag encoding.
}

Num2PbType = {
    1: "double",
    2: "float",
    3: "int64",    # not zigzag (proto3 compiler does not seem to use it)
    4: "uint64",
    5: "int32",    # not zigzag (proto3 compiler does not seem to use it)
    6: "fixed64", 
    7: "fixed32",
    8: "bool",
    9: "string",
    10: None, #"group",   # group (deprecated in proto3)
    11: None, #"message", # another messsage
    12: "bytes",   # bytes
    13: "uint32",
    14: "enum",
    15: "sfixed32", 
    16: "sfixed64",
    17: "sint32", # Uses ZigZag encoding.
    18: "sint64", # Uses ZigZag encoding.
}

Num2WireType = {
    1: "Fixed64",
    2: "Fixed32",
    3: "Varint",
    4: "Varint",
    5: "Varint",
    6: "Fixed64",
    7: "Fixed32",
    8: "Varint",
    9: "LengthDelim",
    10: None,
    11: "LengthDelim", 
    12: "LengthDelim", 
    13: "Varint",
    14: "Varint",
    15: "Fixed32",
    16: "Fixed64",
    17: "Varint",
    18: "Varint",    
}

SolType2BodyLen = {
    "address": 20,
    "uint"   : 32,
    "uint8"  : 1,
    "uint16" : 2,
    "uint32" : 4,
    "uint64" : 8,
    "uint128": 16,
    "uint256": 32,
    "int"    : 32,
    "int8"   : 1,
    "int16"  : 2,
    "int32"  : 4,
    "int64"  : 8,
    "int128" : 16,
    "int256" : 32,
    "bytes1" : 1,
    "bytes2" : 2,
    "bytes3" : 3,
    "bytes4" : 4,
    "bytes5" : 5,
    "bytes6" : 6,
    "bytes7" : 7,
    "bytes8" : 8,
    "bytes9" : 9,
    "bytes10": 10,
    "bytes11": 11,
    "bytes12": 12,
    "bytes13": 13,
    "bytes14": 14,
    "bytes15": 15,
    "bytes16": 16,
    "bytes17": 17,
    "bytes18": 18,
    "bytes19": 19,
    "bytes20": 20,
    "bytes21": 21,
    "bytes22": 22,
    "bytes23": 23,
    "bytes24": 24,
    "bytes25": 25,
    "bytes26": 26,
    "bytes27": 27,
    "bytes28": 28,
    "bytes29": 29,
    "bytes30": 30,
    "bytes31": 31,
    "bytes32": 32,
}

TYPE_MESSAGE = 11
PB_LIB_NAME_PREFIX = "pb"
PB_CURRENT_PACKAGE = ""
LIBRARY_LINKING_MODE = False
SOLIDITY_VERSION = "0.4.0"

# utils
def add_prefix(prefix, name, sep = "_"):
    return ("" if (prefix is None) else (prefix + sep)) + name 

def parse_urllike_parameter(s):
    ret = {} #hash
    if s:
        for e in s.encode('ascii').split('&'):
            kv = e.split('=')
            ret[kv[0]] = kv[1]
    return ret


def camel2snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def field_is_message(f):
    return f.type == TYPE_MESSAGE and (not f.type_name.startswith(".solidity."))

def field_is_repeated(f):
    return f.label == Label2Value["LABEL_REPEATED"]

def field_pb_type(f):
    if f.type == TYPE_MESSAGE:
        return "message"
    return Num2PbType.get(f.type, None)

def field_sol_type(f):
    if f.type != TYPE_MESSAGE:
        return None
    elif f.type_name.startswith(".solidity."):
        return f.type_name.replace(".solidity.", "")
    else:
        return None

def prefix_lib_and_package(name):
    return PB_LIB_NAME_PREFIX + PB_CURRENT_PACKAGE + "_" + name

def prefix_lib(name):
    return PB_LIB_NAME_PREFIX + "_" + name

def gen_delegate_lib_name(msg, parent_struct_name):
    return prefix_lib_and_package(add_prefix(parent_struct_name, msg.name))

def gen_global_type_name_from_field(field):
    ftid, is_usertype = gen_field_type_id(field)
    return prefix_lib(ftid) + ".Data" if is_usertype else ftid

def gen_global_type_from_field(field):
    t = gen_global_type_name_from_field(field)
    if t is None:
        pp.pprint(field)
        pp.pprint("will die ======================================= ")
    if field_is_repeated(field):
        return t + "[]"
    else:
        return t

def gen_internal_struct_name(msg, parent_struct_name):
    return "Data"

def max_field_number(msg):
    num = 0
    for f in msg.field:
        if num < f.number:
            num = f.number
    return num

def str_contains(s, token):
    try:
        return s.index(token) >= 0
    except Exception as e:
        return False

def gen_field_type_id(field):
    val = Num2Type.get(field.type, None)
    if val != None:
        return (val, False)
    val = field_sol_type(field)
    if val != None:
        return (val, False)
    return (field.type_name[1:].replace(".", "_"), True)

def gen_fieldtype(field):
    t = gen_global_type_name_from_field(field)
    if field_is_repeated(field):
        return t + "[]"
    else:
        return t

def gen_struct_decoder_name_from_field(field):
    ftid, _ = gen_field_type_id(field)
    return "_decode_" + ftid

def gen_struct_codec_lib_name_from_field(field):
    ftid, is_usertype = gen_field_type_id(field)
    if not is_usertype:
        "___{} is not user type ({})___".format(field.name, ftid)
    return prefix_lib(ftid)

def gen_decoder_name(field):
    val = Num2PbType.get(field.type, None)
    if val != None:
        return "_pb._decode_" + val
    else:
        val = field_sol_type(field)
        if val != None:
            return "_pb._decode_sol_" + val
        return "_decode" + field.type_name.replace(".", "_")

def gen_encoder_name(field):
    val = Num2PbType.get(field.type, None)
    if val != None:
        return "_pb._encode_" + val
    else:
        val = field_sol_type(field)
        if val != None:
            return "_pb._encode_sol_" + val
        return gen_struct_codec_lib_name_from_field(field) + "._encode_nested"

def gen_wire_type(field):
    return Num2WireType.get(field.type, None)

def gen_soltype_estimate_len(sol_type):
    val = SolType2BodyLen.get(sol_type, 0)
    return val + 3

def change_pb_libname_prefix(new_name):
    global PB_LIB_NAME_PREFIX
    PB_LIB_NAME_PREFIX = new_name

def change_package_name(new_name):
    if new_name:
        global PB_CURRENT_PACKAGE
        PB_CURRENT_PACKAGE = "_" + new_name.replace(".", "_")
    else:
        PB_CURRENT_PACKAGE = ""

def is_lib_linking_mode():
    global LIBRARY_LINKING_MODE
    return LIBRARY_LINKING_MODE

def set_lib_linking_mode():
    global LIBRARY_LINKING_MODE
    # disable for now because cannot return arbiter struct and 
    # dynamic length bytes array until solidity 0.4.21
    # LIBRARY_LINKING_MODE = True
    LIBRARY_LINKING_MODE = False

def gen_visibility(is_decoder):
    if not LIBRARY_LINKING_MODE:
        return "internal"
    return "internal" if is_decoder else ""

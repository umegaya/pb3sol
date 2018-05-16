import sys
import gen_util as util

def gen_main_encoder(msg, parent_struct_name):
	return (
		"  function encode({struct} r) {visibility} constant returns (bytes) {{\n"
		"    bytes memory bs = new bytes(_estimate(r));					   \n"
		"    uint sz = _encode(r, 32, bs);                                 \n"
		"    assembly {{ mstore(bs, sz) }}                                 \n"
		"    return bs;                                                    \n"
		"  }}                                                              \n"
	).format(
		visibility = util.gen_visibility(False),
		struct = util.gen_internal_struct_name(msg, parent_struct_name),
	)

def has_repeated_field(fields):
	for f in fields:
		if util.field_is_repeated(f):
			return True
	return False

def gen_inner_field_encoder(f):
	#sys.stderr.write("fname={}, type={}\n".format(f.name, f.type))
	return ((
		"    for(i=0; i<r.{field}.length; i++) {{               \n"
		"      p += _pb._encode_key({key}, _pb.WireType.{wiretype}, p, bs); \n"
		"      p += {encoder}(r.{field}[i], p, bs);             \n"
		"    }}                                                 \n"
	) if util.field_is_repeated(f) else (
		"    p += _pb._encode_key({key}, _pb.WireType.{wiretype}, p, bs);     \n"
		"    p += {encoder}(r.{field}, p, bs);                   \n"
	)).format(
		field = f.name,
		key = f.number,
		wiretype = util.gen_wire_type(f),
		encoder = util.gen_encoder_name(f),
	)

def gen_inner_field_encoders(msg, parent_struct_name):
	return ''.join(list(map((lambda f: gen_inner_field_encoder(f)), msg.field)))

def gen_inner_encoder(msg, parent_struct_name):
	return (
		"  function _encode({struct} r, uint p, bytes bs)        \n"
		"      internal constant returns (uint) {{               \n"
		"    uint offset = p;                                   \n"
		"{counter}\n"
		"{encoders}\n"
		"    return p - offset;                                 \n"
		"  }}                                                    \n"
	).format(
		struct = util.gen_internal_struct_name(msg, parent_struct_name),
		counter = "uint i;" if has_repeated_field(msg.field) else "",
		encoders = gen_inner_field_encoders(msg, parent_struct_name),
	)

def gen_nested_encoder(msg, parent_struct_name):
	return (
		"  function _encode_nested({struct} r, uint p, bytes bs)        \n"
		"      internal constant returns (uint) {{                       \n"
		"    uint offset = p;                                           \n"
		"    p += _pb._encode_varint(_estimate(r), p, bs);              \n"
		"    p += _encode(r, p, bs);                                    \n"
		"    return p - offset;                                         \n"
		"  }}                                                            \n"
	).format(
		struct = util.gen_internal_struct_name(msg, parent_struct_name)
	)

def gen_field_scalar_size(f):
	wt = util.gen_wire_type(f)
	vt = util.field_pb_type(f)
	fname = f.name + ("[i]" if util.field_is_repeated(f) else "")
	if wt == "Varint":
		if vt == "bool":
			return "1"
		else: 
			return ("_pb._sz_{valtype}(r.{field})").format(
				valtype = vt,
				field = fname,
			)
	elif wt == "Fixed64":
		return "8"
	elif wt == "Fixed32":
		return "4"
	elif wt == "LengthDelim":
		if vt == "bytes":
			return ("_pb._sz_lendelim(r.{field}.length)").format(
				field = fname
			)
		elif vt == "string":
			return ("_pb._sz_lendelim(bytes(r.{field}).length)").format(
				field = fname
			)
		elif vt == "message":
			st = util.field_sol_type(f)
			if st is None:
				return ("_pb._sz_lendelim({lib}._estimate(r.{field}))").format(
					lib = util.gen_struct_codec_lib_name_from_field(f),
					field = fname,
				)
			else:
				return "{}".format(util.gen_soltype_estimate_len(st))
		else:
			return ("__does not support pb type {t}__").format(t = vt)
	else:
		return ("__does not support wire type {t}__").format(t = wt)

def gen_field_estimator(f):
    return ((
    	"    for(i=0; i<r.{field}.length; i++) e+= {szKey} + {szItem}; \n"
    ) if util.field_is_repeated(f) else (
		"    e += {szKey} + {szItem}; \n"
    )).format(
    	field = f.name,
    	szKey = (1 if f.number < 16 else 2),
    	szItem = gen_field_scalar_size(f)
    )

def gen_field_estimators(msg, parent_struct_name):
	return ''.join(list(map((lambda f: gen_field_estimator(f)), msg.field)))

def gen_estimator(msg, parent_struct_name):
	est = gen_field_estimators(msg, parent_struct_name)
	not_pure = util.str_contains(est, "r.")
	return (
		"  function _estimate({struct} {varname}) internal {mutability} returns (uint) {{ \n"
		"    uint e;                                                        \n"
		"{counter}\n"
		"{estimators}\n"
		"    return e;                                                      \n"
		"  }}                                                                \n"
	).format(
		struct = util.gen_internal_struct_name(msg, parent_struct_name),
		varname = "r" if not_pure else "/* r */",
		mutability = "constant" if not_pure else "pure",
		counter = "uint i;" if has_repeated_field(msg.field) else "",
		estimators = est,
	)

def gen_encoder_section(msg, parent_struct_name):
	return (
		"  // Encoder section                 \n"
		"{main_encoder}                     \n"
		"  // inner encoder                  \n"
		"{inner_encoder}                    \n"
		"  // nested encoder                 \n"
		"{nested_encoder}                   \n"
		"  // estimator                 \n"
		"{estimator}                        \n"
	).format(
		main_encoder = gen_main_encoder(msg, parent_struct_name),
		inner_encoder = gen_inner_encoder(msg, parent_struct_name),
		nested_encoder = gen_nested_encoder(msg, parent_struct_name),
		estimator = gen_estimator(msg, parent_struct_name),
	)
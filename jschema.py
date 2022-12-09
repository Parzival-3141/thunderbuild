from typing import Any
from types import GenericAlias

# check if key in schema is in json
# check value in schema is same in json
# Schema format:
#	You can use UnionType to show a key may contain multiple types.
# 	Lists store the types they contain. 
# 	e.g. "schema_list": [str | bool] -> "valid_json_list": ["Hello ", True, " Sailor"]
# 	If a list contains multiple elements, it treats them as positonal arguments
#	e.g. "schema_list": [str, str, bool] -> "valid_json_list": ["Hello", " Sailor", False]
	
# 	Dictionaries act normally. If you leave the fields blank ("dict": {}) then it
#	assumes all potential children are valid.
	
# 	You can make optional keys by tagging them with "_OPTIONAL" ("key_name_OPTIONAL")

def parse_list(mlist: list[Any], schema: GenericAlias, json_name: list[str], list_depth=0) -> bool:
	
	def defer_return(value: bool, json_name: list[str], depth: int) -> bool:
		if depth > 0:
			json_name.pop()
		return value
	
	# finish adding [i] things to json_name in loops
	# fix popping all values
	
	args = schema.__args__
	print(get_name(json_name), mlist, args)
	
	match len(args):
		case 0:
			return defer_return(True, json_name, list_depth)
		
		case 1:
			arg = args[0]
			if type(arg) is GenericAlias:
				arg = arg.__origin__
			
			for i, v in enumerate(mlist):
				if type(v) is arg:
					if arg is list:
						if not parse_list(v, args[0], json_name, list_depth + 1):
							return defer_return(False, json_name, list_depth)
				else:
					print("Key %s[%d] is invalid type \nExpected: %s \nGot: %s" % (get_name(json_name), i, args[0], type(v)))
					return defer_return(False, json_name, list_depth)
		
		case _ as len_args:
			if len(mlist) == len_args:
				for i, v in enumerate(mlist):
					#json_name[-1] = "[%d]" % i
					arg = args[i]
					
					print(get_name(json_name), v, arg)
										
					if type(arg) is GenericAlias:
						arg = arg.__origin__
					
					if type(v) is arg:
						if arg is list:
							if not parse_list(v, args[0], json_name, list_depth + 1):
								return defer_return(False, json_name, list_depth)
					else:
						print("Key %s[%d] is invalid type \nExpected: %s \nGot: %s" % (get_name(json_name), i, args[0], type(v)))
						return defer_return(False, json_name, list_depth)
						
					#json_name.removesuffix("[%d]" % i)
			else:
				print("Key %s[%d] contains too many elements \nExpected: %d \nGot: %d" % (get_name(json_name), i, len_args, len(mlist)))
				return defer_return(False, json_name, list_depth)
				
	
	return defer_return(True, json_name, list_depth)


def get_name(names: list[str]) -> str:
	return ":".join(names)
	
	
def validate(json: dict[str, Any], schema: dict[str, dict | type], json_name="") -> bool:
	if json is None or schema is None:
		return False
	
	if type(json_name) != list:
		if json_name == "":
			json_name = []
		else:
			json_name = [json_name]
	
	success = True

	for key, value in schema.items():
		name = key.replace("_OPTIONAL", "")
		json_name.append(name)
		
		if not name in json:
			success = False
			print("Missing key '%s'" % get_name(json_name))
			continue
		
		# print(key, type(value))
		
		json_type = type(json[name])
		
		match type(value):
			case t if t is GenericAlias:
			
				if json_type is value.__origin__:
					#print("%s is of type %s%s" % (get_name(json_name), value.__origin__, value.__args__))
					match value.__origin__:
						case _t if _t is list:
							if not parse_list(json[name], value, json_name):
								success = False
														
						case _t if _t is dict:
							if len(value.__args__) > 0:
								print("Schema key '%s' of type %s cannot accept type arguments" % (get_name(json_name), dict))
								success = False
							
						case _ as _t:
							success = False
							print("Schema key '%s' of type %s is not supported" % (get_name(json_name), _t))
				else:
					print("Key '%s' contains invalid type \nExpected: %s \nGot: %s" % (get_name(json_name), value.__origin__, json_type))
					
				
			case t if t is dict:
				#print(get_name(json_name), "is type", t)
				
				if not validate(json[name], schema[key], json_name):
					success = False
				
			case t if t is type:
				#print(get_name(json_name), "is type", value)
				if not type(json[name]) is value:
					success = False
					print("Key '%s' contains invalid type \nExpected: %s \nGot: %s" % (get_name(json_name), value, type(json[name])))
			
			case _:
				print("Key '%s' of type %s is not supported" % (get_name(json_name), t))
		
		json_name.pop()
	
	return success
	
	
if __name__ == "__main__":
	import json
	
	file = open("example_thunder_info.json")
	j = json.load(file)
	file.close()
	
	schema = {
		"version_file_OPTIONAL": str,
		"version_regex_OPTIONAL": str,
		"output_OPTIONAL": str,
		"icon": str,
		"readme": str,
		"mod_files": list[list[str, str]],
		"manifest": {
			"name": str,
			"version_number_OPTIONAL": str,
			"website_url": str,
			"description": str,
			"dependencies": list[str]
		}
	}
	
	print("Success:", validate(j, schema))
	
	
# You can define by type or by value.

# Define by value means you always expect this exact value.
# e.g. "language": "python", "operating_systems": ["windows", "linux"]

# Define by type means you expect a value of said type.
# e.g. "stuff": list, "paths": list[str], "objects": list[dict]
#
# Note how you cannot specify the layout of dicts inside of lists. You
# can iterate through and call validate each dict yourself if you want.

# Using types means you can use Union types for optional typing
# e.g. "number": int | float, "numbers": list[int] | list[float]

# Dicts defined by value are parsed as keys which contain more keys, just like json.

# Lists can be defined by what values they contain or by positional arguments
#
# You can use Unions to say a list can contain any of these types
# e.g. "numbers": list[int | float]
#
# You can seperate types with a comma to say the list must follow a positional format
# e.g. "vector": list[float, float], "version": list[int, int, int]
# 
# This also works for nesting, "versions": list[list[int, int, int]]

# Any keys not covered by the schema are ignored
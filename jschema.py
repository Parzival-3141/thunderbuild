from typing import Any

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

def validate_dict(json: dict[str, Any], schema: dict[str, dict | type], stack: list[str]) -> (bool):
	if json is None or schema is None:
		return False
	
	success = True
	
	new_stack = stack
	new_stack.append("")
	
	for key, value in schema.items():
		name = key.replace("_OPTIONAL", "")
		
		new_stack[-1] = name
		name_path = ":".join(new_stack)
		
		if name in json:
			jsType = type(json[name])
			
			if type(value) is list:
				print(name_path, value)
				pass # Todo: verify list follows schema guidelines
				
			elif type(value) is dict:
				print(name_path, type(value))
				if len(value) == 0:
					continue
				
				if not validate_dict(json[name], schema[key], new_stack):
					success = False
				new_stack.pop() # apparently new_stack is like a static variable for the function???
				
			elif jsType is value:
				print(name_path, value)
				continue
				
			else:
				print("Key '%s' contains invalid type \nExpected: %s \nGot: %s\n" % (name_path, value, jsType))
				success = False
				
		elif not "_OPTIONAL" in key:
			print("Missing key: '%s'\n" % name_path)
			success = False
		
		
	return success
	

def validate(json: dict[str, Any], schema: dict[str, dict | type]) -> bool:
	return validate_dict(json, schema, [])
	
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
		"mod_files": [[str, str]],
		"manifest": {
			"name": str,
			"version_number_OPTIONAL": str,
			"website_url": str,
			"description": str,
			"dependencies": [str]
		}
	}
	
	print("Success:", validate(j, schema))
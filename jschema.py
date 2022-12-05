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

def validate(json: dict[str, Any], schema: dict[str, dict | type]) -> bool:
	if json is None or schema is None:
		return False
	
	for k, v in schema.items():
		if type(v) is dict:
			print(k, "{")
			
			validate(v, v)
				
			print("}")
			continue
		
		#if type(v) is list:
		
			
		print(k, ":", v)
			

if __name__ == "__main__":
	import sys, json
	
	file = open(sys.argv[1])
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
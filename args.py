### A Type-based Argument Parser for Python
# Usage:
#
# import sys
# from dataclasses import dataclass
# from args import parse_arguments
#
# @dataclass
# class MyArgs:
#     string: str
#	  boolean: bool # bool values default to False
#	  integer: int
#	  floating: float = 10.5
#
# success, args = parse_arguments(sys.argv[1:], MyArgs)
# if not success:
#     exit()
#
# print(args)


from dataclasses import dataclass, fields, MISSING

def get_argument_value(args: list[str], arg: str, cursor: int, strict_hyphen: bool, data_args: list[str]) -> (bool, str, int):
	if cursor >= len(args) - 1:
		print("Argument %d (%s) is missing a value." % (cursor, arg))
		return False, "", cursor
	else:
		if strict_hyphen and args[cursor + 1][0] == '-':
			if args[cursor + 1][1:] in data_args:
				print("Argument %d (%s) is missing a value." % (cursor, arg))
			else:
				print("Argument %d (%s) has an invalid value (%s). Value's cannot start with '-'."\
				% (cursor, arg, args[cursor + 1]))
				cursor += 1
			return False, "", cursor
		else:
			cursor += 1
			return True, args[cursor], cursor
		

def instantiate_default_data(data: type[dataclass]) -> dataclass:
	defaults = {}
	for name, field in data.__dataclass_fields__.items():
		if field.type is bool:
			defaults[name] = False if field.default == MISSING else field.default
		else:
			defaults[name] = None if field.default == MISSING else field.default
			
	return data(**defaults)
			

def parse_arguments(args: list[str], args_data: type[dataclass], strict_hyphen=True) -> (bool, dataclass):
	result = instantiate_default_data(args_data)
	
	success = True
	cursor = 0
	while cursor < len(args):
		arg = args[cursor]
		if arg[0] != '-':
			print("Argument", cursor, f"({arg})", "does not start with '-'.")
			return False, result
			
		arg = arg[1:]
		#print("- Looking for argument named", arg)
		
		found_arg = False
		for name, typpe in args_data.__annotations__.items():
			if name != arg:
				continue
			
			match typpe:
				case t if t is str:
					value_success, value, cursor = get_argument_value(args, arg, cursor, strict_hyphen, args_data.__match_args__)
					if value_success:
						result.__dict__[name] = value
					else:
						success = False
					
				case t if t is bool:
					result.__dict__[name] = True
					
				case t if t is int:
					value_success, value, cursor = get_argument_value(args, arg, cursor, strict_hyphen, args_data.__match_args__)
					if value_success:
						try:
							result.__dict__[name] = int(value)
						except:
							pass
					else:
						success = False
					
				case t if t is float:
					value_success, value, cursor = get_argument_value(args, arg, cursor, strict_hyphen, args_data.__match_args__)
					if value_success:
						result.__dict__[name] = float(value)
					else:
						success = False	
						
				#case t if t is list:
				case _:
					print("Argument %d (%s) is of unsupported type %s." % (cursor, arg, typpe.__name__))
					success = False
			
			found_arg = True
		
		if not found_arg:
			print("Argument %d (%s) is not valid." % (cursor, arg))
			success = False
		
		cursor += 1
	
	return success, result
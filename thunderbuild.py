import re
from zipfile import ZipFile, ZIP_DEFLATED
import json
from os.path import exists

from args import parse_arguments
from dataclasses import dataclass
from typing import NamedTuple


# I don't think people will want to mass build multiple mods in one go, so we should only
# accept one info file. They can make a script to automate that if they want to.

# If it's run without passing a info file, we search the current working
# directory and error if it doesn't contain a "thunder_info.json"
# file. Can pass a path to specify one.

# Version can be specified in 3 different ways: by CLI, by Python Regex, and by manifest. 
# They are also evaluated in that order. The program errors if no 
# version can be found.

# Output directory can also be specified in multiple ways: by CLI and by thunder_info. 
# It defaults to 'thunder_builds/` in the current working directory.

# Full command input
# thunderbuild -version 1.2.3 -overwrite -output ./builds/ ./thunder_info.json

@dataclass
class ThunderBuildArgs:
	version: str
	overwrite: bool = False
	output_dir: str = "./thunder_builds/"
	info_file: str = "./thunder_info.json"
	help: bool = False

helptxt = \
"""
Usage: thunderbuild [OPTIONS]

OPTIONS:
    -version    <string>   Version to mark the build as. Overrides versioning in the Thunder Info file. 
                           Follows Semantic Versioning (major.minor.patch).
    -overwrite             Overwrite a build if one with the same version already exists in output_dir.
    -output_dir <path>     Directory to output the build. Defaults to "./thunder_builds/".
    -info_file  <path>     Path to a Thunder Info file. Defaults to "./thunder_info.json".
    -help                  Display this help text.
	
Relative paths are treated as relative to the current working directory.
In Thunder Info files, paths are relative to the file location.
"""

def find_version(args: ThunderBuildArgs, info: dict) -> str:
	if args.version != None:
		return args.version
	
	# Version Regex
	if "version_file" in info and "version_regex" in info:
		if exists(info["version_file"]):
			match = re.search(info["version_regex"])
			if match:
				return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
			else:
				print("Version regex failed, searching in manifest section...")
		else:
			print("Version file at %s doesn't exist! Searching in manifest section..."\
			% info["version_file"])
			
	if "version_number" in info["manifest"]:
		return info["manifest"]["version_number"]
	
	exit("Version search failed. Check your Thunder Info file (%s) for errors." % args.info_file)


if __name__ == "__main__":
	import sys
	
	success, args = parse_arguments(sys.argv[1:], ThunderBuildArgs)
	
	if not success or args.help:
		exit(helptxt)
	
	thunderinfo = None
	if not exists(args.info_file):
		exit("Thunder Info file at %s doesn't exist!" % args.info_file)
	with open(args.info_file) as info_file:
		thunderinfo = json.load(info_file)
	
	#print(json.dumps(thunderinfo, indent=4))
	version = find_version(args, thunderinfo)
	
	print("Building", version)
	
	
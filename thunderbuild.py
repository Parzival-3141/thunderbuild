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
    -overwrite             Overwrite a build if one with the same version already exists.
    -output_dir <path>     Directory to output the build. Defaults to "./thunder_builds/".
    -info_file  <path>     Path to a Thunder Info file. Defaults to "./thunder_info.json".
    -help                  Display this help text.
	
Relative paths are treated as relative to the current working directory.
In Thunder Info files, paths are relative to the file location.
"""


if __name__ == "__main__":
	import sys
	
	success, args = parse_arguments(sys.argv[1:], ThunderBuildArgs)
	
	if not success or args.help:
		exit(helptxt)
	
	print(args)
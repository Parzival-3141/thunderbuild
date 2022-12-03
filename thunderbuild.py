import re
from zipfile import ZipFile, ZIP_DEFLATED
import json
from os.path import exists


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


def find_version(info) -> str:
	version = ""
	
	# Set version from args
	
	if "version_file" in info and "version_regex" in info:
		with open(info["version_file"]) as ver_file:
			match = re.search(info["version_regex"])
			if match:
				version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"

	if version == "" and "version_number" in info["manifest"]:
		version = info["manifest"]["version_number"]
	
	if version == "":
		# print("Cannot find version info")
		exit("Cannot find version info")
	
	return version



if __name__ == "__main__":
	import sys
	print(sys.argv)

# thunder_info = None
# with open("thunder_info.json") as info_file:
# 	thunder_info = json.load(info_file)


# filename = f"{thunder_info["manifest"]["name"]}-v{version}.zip"
# buildpath = "thunder_builds/" + filename
# 
# if exists(buildpath) and "-overwrite" not in args:
# 	exit(f"Build {buildpath} already exists! Use -overwrite to replace an existing build.")
# 
# manifest = thunder_info["manifest"]
# manifest["version_number"] = version
# 
# with ZipFile(buildpath, mode="w", compression=ZIP_DEFLATED) as zfile:
# 	zfile.write(thunder_info["readme"], arcname="README.md")
# 	zfile.write(thunder_info["icon"], arcname="icon.png")
# 	zfile.writestr("manifest.json", json.dumps(manifest, indent="\t"))
# 	
# 	for mod_filepath, mod_arcname in thunder_info["mod_files"].items():
# 		zfile.write(mod_filepath, arcname=mod_arcname)
		
		
		
		
import re
from zipfile import ZipFile, ZIP_DEFLATED
import json
from os.path import exists

# CLI tool that builds mods for thunderstore
# Parses a build info file to find and include all files in a build zip

# Usage Needs:
#  - Specify paths for icon, readme, and manifest
#  - Specify file structure and what files to include
#  - Input version number
#  - Set output folder
#  - Option to overwrite existing build

# Implementation:
# Json file that contains build info.
#  - Can specify paths for files (icon, readme, mod-files), and where they go in the zip
#  - Write the manifest right in the json file
#  - Set whether to look at the dll's product version, or a file containing a BuildInfo class (dll version seems like a better idea)
#  - Set output folder, or leave as default './mod_builds/'
#  - CLI arg to overwrite when building

buildInfoPath = "src/Main.cs"
version = ""

with open(buildInfoPath, "r") as file:
	for line in file:
		match = re.search("(?<=public const string Version = \")(\d+\.\d+\.\d+)", line)
		if match:
			version = match.group(1)
		
if version == "":
	print("Cannot find version number in " + buildInfoPath)
	exit()

filename = f"SpiderLab-v{version}.zip"
buildpath = f"builds/{filename}"

if exists(buildpath):
	print(f"Build '{filename}' already exists!") # @Todo: use '-overwrite' to overwrite existing builds
	exit()

manifest = {
    "name": "SpiderLab",
    "version_number": version,
    "website_url": "",
    "description": "A Spider-Man mod for BONELAB",
    "dependencies": [
        "gnonme-BoneLib-1.4.0"
    ]
}

# @Todo: validate files exist before creating zipfile
with ZipFile(buildpath, mode="w", compression=ZIP_DEFLATED) as zfile:
	zfile.write("README.md")
	zfile.write("media/icon.png", arcname="icon.png")
	zfile.write("bin/Release/SpiderLab.dll", arcname="Mods/SpiderLab.dll")
	zfile.writestr("manifest.json", json.dumps(manifest, indent="\t"))
	print("Built mod at " + buildpath)
	zfile.printdir()
# based on the javascript mermaid filter here: https://github.com/raghur/mermaid-filter/blob/master/index.js
# but this should be compatable with panflute 

# 20jun2022

# db: elem:<light-blue> b"RawBlock(\\part{another top level heading}; format='latex')" </light-blue>, parent:<light-green>b'None'</light-green>, children:<light-yellow>[]</light-yellow> 
# db: elem:<light-blue> b'CodeBlock(def mainko(bozo):\n    return "hungry"; classes=[\'python\'])' </light-blue>, parent:<light-green>b'Doc'</light-green>, children:<light-yellow>[]</light-yellow> 
# db: elem:<light-blue> b"CodeBlock(int mainko(int bozo){\n    return ERROR_UNDEF;\n}; classes=['c'])" </light-blue>, parent:<light-green>b'Doc'</light-green>, children:<light-yellow>[]</light-yellow> 
# db: elem:<light-blue> b"CodeBlock(sequenceDiagram\n    Alice->>John: Hello John, how are you?\n    John-->>Alice: Great!; classes=['mermaid'])" </light-blue>, parent:<light-green>b"Div(Header(Str(Heading) Space Str(level) Space Str(1) Space Str((should) Space Str(become) Space Str(2)) Space Str(in) Space Str(content/a_outerfolder/main.md); level=1, identifier='heading-level-1-should-become-2-in-contenta_outerfoldermain.md') Para(Str(Content) Space Str(below) Space Str(that) Space Str(heading) Space Str(in) Space Str(the) Space Str(markdown) Space Str(file)) Para(Str(xxx) Space Str(change)) Para(Str(let\xe2\x80\x99s) Space Str(see) Space Str(if) Space Str(this) Space Emph(Str(mermaid)) Space Str(filter) Space Str(works.) Space Str(Should) Space Str(look) Space Str(like) Space Str(the) Space Str(example) Space Str(from) Space Str(https://github.com/raghur/mermaid-filter)) CodeBlock(sequenceDiagram\n    Alice->>John: Hello John, how are you?\n    John-->>Alice: Great!; classes=['mermaid']); attributes={'source': '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/demos/demo_report/doc/content/a_outerfolder/main.md'})"</light-green>, children:<light-yellow>[]</light-yellow> 

import panflute as pf
import tempfile

import argparse, os, subprocess, textwrap
from glob import glob
import subprocess
import pathlib

# copied from lxdev.run_local_cmd, and build_default_report.py
# this should be imported from somewhere, not copied like this
from pandown import run_local_cmd



def debug_elem(elem):
	def preview_func(obj):
		return str(obj).encode()

	for debug_line in [
		"db: ",
		f"elem:<light-blue> {preview_func(elem)} </light-blue>, ",
		f"parent:<light-green>{preview_func(elem.parent)}</light-green>, ",
		f"children:<light-yellow>{[preview_func(getattr(elem, child)) for child in elem._children]}</light-yellow> \n"
		]:
		pf.debug(debug_line, end="")

def prepare(doc):
	pass

def handle_mermaid_charts(options, data, element, doc):
	""" 
	20jun2022

	In markdown files, this replaces mermaid code blocks with an image
	generated using the mermaid cli. 

	Implementation details:
	- The image is saved as an external file
	- ...
	"""

	assert isinstance(element, pf.CodeBlock) & ("mermaid" in element.classes), "Assuming mermaid code blocks"

	# make a temporary file with the content of the mermaid codeblock
	# call mmdc such that a corresponding .svg image is generated
	# save this .svg file to a location
	# then return an image element that displays the new image

	dest_format = options.get("format", "pdf" if doc.format=="latex" else "svg")
	width = options.get("width", 800)
	scale = options.get("scale", 1)
	theme = options.get("theme", "default")
	background = options.get("background", "transparent")

	# needed windows-compatible tempfile structure
	# from https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile
	# tempSrcFile = tempfile.NamedTemporaryFile()
	# tempSrcFile.write(data.encode())
	# tempSrcFile.close()

	with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
			
		temp_src_file = pathlib.Path(tmpdir) / "temp_src_file.xxx"
		with open(temp_src_file, "w") as f:
			f.write(data)

		# pf.debug("file ----------------")
		# with open(tempSrcFile.name, 'r') as f:
		# 	pf.debug(f.readlines())
		# pf.debug("End file ---------------")


		# for the dest name, store an attribute in the doc object, so we can use incrementing identifiers
		if hasattr(doc, "mermaid_chart_index"):
			doc.mermaid_chart_index += 1
		else:
			doc.mermaid_chart_index = 0
		destFilename = f'mermaid_chart_{doc.mermaid_chart_index}.{dest_format}'
		destFilePath = os.path.join(doc.get_metadata("generated_intermediate_files_dir"), destFilename)

		# mmdc_cmd = "mmdc"
		mmdc_cmd_location = pathlib.Path().home() / "node_modules" / ".bin" / "mmdc"
		assert mmdc_cmd_location.exists(),  "mermaid-cli has not been installed. Follow the installation guide or remove this filter from your main.md"

		# mmdc_cmd = os.path.expanduser("~/node_modules/.bin/mmdc") to the ~ directory
		mmdc_cmd = str(mmdc_cmd_location)
		mmdc_cmd += f' -w {width}'
		mmdc_cmd += f' -s {scale}'
		mmdc_cmd += " -f" # necessary?
		mmdc_cmd += f' -i {temp_src_file}'#{tempSrcFile.name}'
		mmdc_cmd += f' -t {theme}'
		mmdc_cmd += f' -b {background}'
		mmdc_cmd += f' -o {destFilePath}'

		result, error = run_local_cmd(mmdc_cmd)
	
	if dest_format == "svg":
		if doc.format == "latex":
			assert 0, "this doesn't work yet, some latex issue"
			# this assumes that a latex document will be produced
			# or, hardcode the use of includesvg as in here https://tex.stackexchange.com/questions/122871/include-svg-images-with-the-svg-package
			new_elem = pf.RawBlock(f'\\includesvg{{{destFilePath}}}', format="tex")
		
		else:
			# relative path is important for html mainly, but useful for other output formats too
			relative_path = os.path.relpath(destFilePath, doc.get_metadata("output_dir"))
			new_elem = pf.Para(pf.Image(url=relative_path, title=options.get("title", "")))

	else:
		new_elem = pf.Para(pf.Image(url=destFilePath, title=options.get("title", "")))

	
	return new_elem

def finalize(doc):
	pass

	

def main(doc=None):
	return pf.run_filter(pf.yaml_filter, prepare=prepare, finalize=finalize,
		tag='mermaid', function=handle_mermaid_charts, doc=doc, strict_yaml=True)  
		# note - the use of 'strict yaml' here allows live markdown previews to work,
		# in the source files, but may have other impacts

if __name__ == '__main__':
	main()


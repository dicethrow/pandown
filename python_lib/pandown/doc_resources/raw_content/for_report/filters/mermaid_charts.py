# based on the javascript mermaid filter here: https://github.com/raghur/mermaid-filter/blob/master/index.js
# but this should be compatable with panflute 

# 20jun2022

# db: elem:<light-blue> b"RawBlock(\\part{another top level heading}; format='latex')" </light-blue>, parent:<light-green>b'None'</light-green>, children:<light-yellow>[]</light-yellow> 
# db: elem:<light-blue> b'CodeBlock(def mainko(bozo):\n    return "hungry"; classes=[\'python\'])' </light-blue>, parent:<light-green>b'Doc'</light-green>, children:<light-yellow>[]</light-yellow> 
# db: elem:<light-blue> b"CodeBlock(int mainko(int bozo){\n    return ERROR_UNDEF;\n}; classes=['c'])" </light-blue>, parent:<light-green>b'Doc'</light-green>, children:<light-yellow>[]</light-yellow> 
# db: elem:<light-blue> b"CodeBlock(sequenceDiagram\n    Alice->>John: Hello John, how are you?\n    John-->>Alice: Great!; classes=['mermaid'])" </light-blue>, parent:<light-green>b"Div(Header(Str(Heading) Space Str(level) Space Str(1) Space Str((should) Space Str(become) Space Str(2)) Space Str(in) Space Str(content/a_outerfolder/main.md); level=1, identifier='heading-level-1-should-become-2-in-contenta_outerfoldermain.md') Para(Str(Content) Space Str(below) Space Str(that) Space Str(heading) Space Str(in) Space Str(the) Space Str(markdown) Space Str(file)) Para(Str(xxx) Space Str(change)) Para(Str(let\xe2\x80\x99s) Space Str(see) Space Str(if) Space Str(this) Space Emph(Str(mermaid)) Space Str(filter) Space Str(works.) Space Str(Should) Space Str(look) Space Str(like) Space Str(the) Space Str(example) Space Str(from) Space Str(https://github.com/raghur/mermaid-filter)) CodeBlock(sequenceDiagram\n    Alice->>John: Hello John, how are you?\n    John-->>Alice: Great!; classes=['mermaid']); attributes={'source': '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/demos/demo_report/doc/content/a_outerfolder/main.md'})"</light-green>, children:<light-yellow>[]</light-yellow> 

import panflute as pf

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

	assert isinstance(element, pf.CodeBlock) | isinstance(element, pf.Code), "Assuming mermaid code blocks"
	if "mermaid" in element.classes:
		pf.debug("Found!!!!")
		return [] # remove it?

	# # language = elem.classes[0]
	# try:
	# 	language = elem.classes[0]
	# except:
	# 	language = "" # if not given
	# if language != "mermaid":
	# 	return elem # return unmodified
	# else:
	# 	# debug_elem(elem)
	# 	return []

	# as_text = pf.stringify(elem)
	# # as_text = as_text.replace("#", "\#")
	# # as_text = as_text.replace("$", "\$")
	# # as_text = as_text.replace("_", "\_")

	# if isinstance(elem, pf.CodeBlock):
	# 	# src = f"\\begin{{minted}}{{{language}}}\n{as_text}\n\\end{{minted}}"
	# 	src = f"\\begin{{verbatim}}\n{as_text}\n\\end{{verbatim}}"


		
	# 	# src = "\\begin{listing}" + src + "\\end{listing}"
	# 	elem = pf.RawBlock(src, format="tex")
	# elif isinstance(elem, pf.Code):
	# 	# elem = pf.RawInline(f"\\mintinline{{{language}}}\\{{{as_text}}}", format="tex")
	# 	# elem = pf.RawInline(f"\\begin{{verbatim}}{as_text}\\end{{verbatim}}", format="tex")
	# 	elem = pf.RawInline(f"\\verb|{as_text}|", format="tex")


	# # as_text2 = pf.stringify(elem)	

	
	# 	# elem = [] # remove for now
	# # debug_elem(elem)

	# return elem

def finalize(doc):
	pass

	

def main(doc=None):
	return pf.run_filter(pf.yaml_filter, prepare=prepare, finalize=finalize,
		tag='mermaid', function=handle_mermaid_charts, doc=doc)

if __name__ == '__main__':
	main()


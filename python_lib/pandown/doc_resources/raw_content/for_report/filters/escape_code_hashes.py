"""
Pandoc filter using panflute.

When using code blocks, often hashes are used. However these are reserved in latex,
so they need to be excaped with a backslash beforehand. This filter implements that.
"""

import panflute as pf

import panflute as pf
import subprocess, os, yaml, re, pprint, copy

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


# def fenced_action(options, data, element, doc):
# 	# return None -> element unchanged
#  	# return [] -> delete element
# 	return []

def escape_code_hashes(elem, doc):
	assert doc.format == "latex", "the minted filter only works when generating latex"
	
	if isinstance(elem, pf.CodeBlock) | isinstance(elem, pf.Code):
	
		# debug_elem(elem)
		# pf.debug("xxx, ", elem.classes)
		
		# if len(elem.classes) == 0:
		# 	pf.debug("Error: No language specified for this code block, will apply hash fix")
		# 	# debug_elem(elem)
		# 	# assert 0
		# 	language = "bash" # for now
		
		# language = elem.classes[0]

		try:
			language = elem.classes[0]
		except:
			language = "bash"


		if language == "bash":
			stringitem = pf.stringify(elem)

			# stringitem = stringitem.replace("\\", "\\symbol{92}")
			stringitem = stringitem.replace("#", "\\#")
			modified_codeblock = type(elem)(stringitem)
			return modified_codeblock

		# if isinstance(elem, pf.CodeBlock):
		# 	elem = pf.RawBlock(f"\\begin{{minted}}{{{language}}}\n{pf.stringify(elem)}\n\\end{{minted}}", format="latex")
		# elif isinstance(elem, pf.Code):
		# 	elem = pf.RawBlock(f"\\mintinline{{{language}}}\n{{{pf.stringify(elem)}}}", format="latex")
			
		# return elem



def main(doc=None):
	return pf.run_filter(escape_code_hashes, doc=doc) 
	# Alternatively:
	# tags = {'sometag': fenced_action, 'another_tag': another_action}
	# return pf.run_filter(... , tags=tags, doc=doc)


if __name__ == '__main__':
	main()


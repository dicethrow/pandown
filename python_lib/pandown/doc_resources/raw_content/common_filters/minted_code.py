# to use the minted+pygments code colouring technique
# based on https://github.com/nick-ulle/pandoc-minted/blob/master/pandoc-minted.py

"""
Pandoc filter using panflute, for fenced code blocks
"""

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

def generate_latex_minted_formatting(elem, doc):
	""" 
	
	8feb2022
	- I can get minted to work, but
		- it needs characters escaped, e.g. replace # with \#, so some errors don't occur
		- but it renders the escaped characters... which isn't great
	- so instead I have 'verbatim' used, the main problem is it doesn't have colour formatting
		
	- perhaps I could use 'verbatim' for bash, and 'minted' for other languages?
		- I'll stick to verbatim for now though. ugh!
	- verbatim is also much faster


	https://blog.wotw.pro/syntax-highlighting-in-latex-with-minted/
	"""	

	if (isinstance(elem, pf.CodeBlock) | isinstance(elem, pf.Code)) and (doc.format == "latex"):
		# the minted filter only works when generating latex
		
		# debug_elem(elem)
		# language = elem.classes[0]
		try:
			language = elem.classes[0]
		except:
			language = "bash" # if not given

		as_text = pf.stringify(elem)
		# as_text = as_text.replace("#", "\#")
		# as_text = as_text.replace("$", "\$")
		# as_text = as_text.replace("_", "\_")

		if isinstance(elem, pf.CodeBlock):
			# src = f"\\begin{{minted}}{{{language}}}\n{as_text}\n\\end{{minted}}"
			src = f"\\begin{{verbatim}}\n{as_text}\n\\end{{verbatim}}"


			
			# src = "\\begin{listing}" + src + "\\end{listing}"
			elem = pf.RawBlock(src, format="tex")
		elif isinstance(elem, pf.Code):
			# elem = pf.RawInline(f"\\mintinline{{{language}}}\\{{{as_text}}}", format="tex")
			# elem = pf.RawInline(f"\\begin{{verbatim}}{as_text}\\end{{verbatim}}", format="tex")
			elem = pf.RawInline(f"\\verb|{as_text}|", format="tex")


		# as_text2 = pf.stringify(elem)	

		
			# elem = [] # remove for now
		# debug_elem(elem)

		return elem

	


# def increase_header_level(elem, doc):
#     if type(elem) == Header:
#         if elem.level < 6:
#             elem.level += 1
#         else:
#             return [] #  Delete headers already in level 6


# def minted(key, value, format, meta):
#     ''' Use minted for code in LaTeX.
#     Args:
#         key     type of pandoc object
#         value   contents of pandoc object
#         format  target output format
#         meta    document metadata
#     '''
#     if format != 'latex':
#         return

#     # Determine what kind of code object this is.
#     if key == 'CodeBlock':
#         template = Template(
#             '\\begin{minted}[$attributes]{$language}\n$contents\n\end{minted}'
#         )
#         Element = RawBlock
#     elif key == 'Code':
#         template = Template('\\mintinline[$attributes]{$language}{$contents}')
#         Element = RawInline
#     else:
#         return

#     settings = unpack_metadata(meta)

#     code = unpack_code(value, settings['language'])

#     return [Element(format, template.substitute(code))]


def main(doc=None):
	return pf.run_filter(generate_latex_minted_formatting, doc=doc)

if __name__ == '__main__':
	main()


# to use the minted+pygments code colouring technique
# based on https://github.com/nick-ulle/pandoc-minted/blob/master/pandoc-minted.py

"""
Pandoc filter using panflute, for fenced code blocks
"""

import panflute as pf
import re

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

# from https://stackoverflow.com/questions/16259923/how-can-i-escape-latex-special-characters-inside-django-templates
# https://www.cespedes.org/blog/85/how-to-escape-latex-special-characters
tex_escaped = {
	'&': r'\&',
	'%': r'\%',
	'$': r'\$',
	'#': r'\#',
	'_': r'\_',
	'{': r'\{',
	'}': r'\}',
	'~': r'\~{}', #r'\textasciitilde{}',
	'^': r'\^{}',
	'\\': r'\\', #r'\textbackslash{}', # note: two so it is escaped for python, then two to re-escape in latex?
	'<': r'\textless{}',
	'>': r'\textgreater{}',
}

def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
   
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(tex_escaped.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: tex_escaped[match.group()], text)

def assert_elem_tex_escaped(elem):
	text = elem.text

	if text.startswith("<!--"):
		return # then it's a comment, so ignore it, pandoc will soon remove it.

	matches = [c for c in text if c in tex_escaped.keys()]

	if len(matches) > 0:
		# now do a detailed check
		for illegal_sequence in tex_escaped.keys():
			text = text.replace(tex_escaped[illegal_sequence], illegal_sequence)
		unescaped_text = text

		# note, stuff between two dollarsigns (e.g. multiple lines of a bash prompt copied in text) will trigger a math thing, so try to put those in code blocks beforehand?

		original_text = elem.text
		if tex_escape(unescaped_text) != elem.text:
			info = f"Possible tex escape issue, try putting in code box? \nchar len={len(elem.text)}\ntype(elem)={type(elem)}\nelem.text={elem.text}\nstringify(elem.parent)={pf.stringify(elem.parent)}"
			assert False, info


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

	if doc.format == "latex":
		if (isinstance(elem, pf.CodeBlock) | isinstance(elem, pf.Code)):
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

				# we need to pick a delimiter that is not in the string
				# so iteratively find one
				delimiters = ["|", "!", "*", "@"] # etc, apparently any character can be used? for now error if this is not enough, deal with it later
				found = False
				for d in delimiters:
					if d in as_text:
						continue
					else:
						found = True
						elem = pf.RawInline(f"\\verb{d}{as_text}{d}", format="tex")
						break
				assert found, "need new delimiter, see above code"


			# as_text2 = pf.stringify(elem)	

			
				# elem = [] # remove for now
			# debug_elem(elem)

			# return elem

		elif hasattr(elem, "text"): # ensure that no forbidden code sequences will get through unetected
			if isinstance(elem, pf.Str):
				elem.text = tex_escape(elem.text) # used to fix # in a url in text
				# pf.debug("xxx here")
			
			# now do a check
			# todo: how to do this? do the excaping backwards? for now, just let it go to latex and fail there
			assert_elem_tex_escaped(elem)
			# if elem.text != tex_escape(elem.text):
				# debug_elem(elem)
				# assert False, f"Illegal symbols detected, try putting in code box. \nlen={len(elem.text)}\ntype(elem)={type(elem)}\nelem.text={elem.text}\nstringify(elem.parent)={pf.stringify(elem.parent)}"

		return elem
	# if (isinstance(elem, pf.CodeBlock) | isinstance(elem, pf.Code)) and (doc.format == "latex"):
		

	


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


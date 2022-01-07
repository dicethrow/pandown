"""
Pandoc filter using panflute
"""

import panflute as pf
import subprocess, os


def prepare(doc):
	pass

# def action(elem, doc):
# 	if isinstance(elem, pf.Element) and doc.format == 'latex':
# 		pass
# 		# return None -> element unchanged
# 		# return [] -> delete element

def action(elem, doc):
	if isinstance(elem, pf.Emph):
		return pf.Strikeout(*elem.content)
		
	if isinstance(elem, pf.Header):
		elem.level = 1

	# copy over images
	if isinstance(elem, pf.Image):
		# elem = pf.convert_text(f"image!")
		# src = elem.url
		pf.shell(f"cp Documents/Uploads/content/{elem.url} Documents/Outputs/{elem.url}")
		
		# pf.debug(f"elem is: {elem}")


def finalize(doc):
	pass


def main(doc=None):
	return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 

if __name__ == '__main__':
	main()
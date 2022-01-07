"""
Pandoc filter using panflute
"""

import panflute as pf
import subprocess, os, yaml, re

elements_so_far = []



# def action(elem, doc):
# 	if isinstance(elem, pf.Element) and doc.format == 'latex':
# 		pass
# 		# return None -> element unchanged
# 		# return [] -> delete element

def decode_yaml_content(element):
	# Split YAML and data parts (separated by ... or ---)
	raw = re.split("^([.]{3,}|[-]{3,})$",
					element.text, 1, re.MULTILINE)
	data = raw[2] if len(raw) > 2 else ''
	data = data.lstrip('\n')
	raw = raw[0]
	try:
		options = yaml.safe_load(raw)
	except yaml.scanner.ScannerError:
		debug("panflute: malformed YAML block")
		return
	if options is None:
		options = {}
	return options, data

# def prepare(doc):
# 	pf.debug("content: ")
# 	pf.debug(doc.content)

def action(elem, doc):
	""" 
	1. Modify header index by recursion level
	2. change to 


	while doc contains yaml parts,
		add those parts to the doc
		restart the loop. count number of loops, indent new headings by this much
	

		
	"""
	starting_dir = doc.get_metadata("starting_dir")


	pf.debug()
	pf.debug(elem)
	pf.debug("loop counter is ", doc.loop_counter)

	new_elem_list = []
	depth = 0

	# if isinstance(elem, pf.Header):
	# 	elem.level = 1

	if isinstance(elem, pf.CodeBlock):
		if "parts" in elem.classes:
			options, data = decode_yaml_content(elem)
			
			pf.debug("found options:", options)
			pf.debug("found data: ", data)

			subfolders = data.split("\n")
			if len(subfolders) == 0:
				pass
			else:
				new_panflute_text = ""
				for subfolder in subfolders:
					pf.debug("bits: ", starting_dir, subfolder, "main.md")
					next_full_dir = os.path.join(starting_dir, subfolder, "main.md")
					pf.debug("next: ", next_full_dir)

					with open(next_full_dir) as f:
						new_src_text = f.read()
					new_panflute_text += pf.convert_text(new_src_text)

		pf.debug("new_panflute_text")
		pf.debug(new_panflute_text)

		return new_panflute_text


def main(doc=None):
	doc.loop_counter = 0
	# doc.starting_dir = doc.get_metadata("starting_dir")
	while True:
		last_doc = doc
		doc = pf.run_filter(action, doc=doc) 
		counter += 1
		if doc == last_doc:
			break
		doc.loop_counter += 1
	return doc 

if __name__ == '__main__':
	main()
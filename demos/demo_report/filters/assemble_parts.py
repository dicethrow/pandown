"""
Pandoc filter using panflute, for fenced code blocks
"""

import panflute as pf
import os

elements_so_far = []

def prepare(doc):
	pf.debug("assemble prepare")
	# pf.debug(doc.args)
	# pf.dump(doc)
	pass


def fenced_action(options, data, element, doc):
	# def get_filename(elem):
	# 	fn = pf.stringify(elem, newlines=False).split(maxsplit=1)[1]
	# 	pf.debug(fn)
	# 	if not os.path.splitext(fn)[1]:
	# 		fn += '.md'
	# 	return fn

	for d in data.split("\n"):
		pf.debug(d)
	
	pf.debug("element: ", element)
	# pf.debug("cwd: ", os.getcwd())
	
	fn = pf.stringify(element, newlines=False).split(maxsplit=1)[1]
	pf.debug("bebebe", fn)

	# with open(fn) as f:
	# 	raw = f.read()

	# new_elems = pf.convert_text(raw)
	
	# Alternative A:


	result = pf.convert_text(f"from parts filter: {options}, {data}")
	pf.debug(type(data), len(data), data)
	return result

def finalize(doc):
	pass


def main(doc=None):
	# a = pf.run_filter(pf.yaml_filter, prepare=prepare, finalize=finalize,
	# 					 tag='parts', function=fenced_action, doc=doc) 

	# pf.debug("here is:")
	# pf.debug(a)



	return pf.run_filter(pf.yaml_filter, prepare=prepare, finalize=finalize,
						 tag='parts', function=fenced_action, doc=doc) 
	# Alternatively:
	# tags = {'sometag': fenced_action, 'another_tag': another_action}
	# return pf.run_filter(... , tags=tags, doc=doc)


if __name__ == '__main__':
	main()


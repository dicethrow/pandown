"""
Pandoc filter using panflute, for fenced code blocks
"""

import panflute as pf


def prepare(doc):
	pass


def fenced_action(options, data, element, doc):
	# return None -> element unchanged
 	# return [] -> delete element
	return []

def finalize(doc):
	pass


def main(doc=None):
	return pf.run_filter(pf.yaml_filter, prepare=prepare, finalize=finalize,
						 tag='comment', function=fenced_action, doc=doc) 
	# Alternatively:
	# tags = {'sometag': fenced_action, 'another_tag': another_action}
	# return pf.run_filter(... , tags=tags, doc=doc)


if __name__ == '__main__':
	main()


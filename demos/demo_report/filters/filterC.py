"""
Pandoc filter using panflute, for fenced code blocks
"""

import panflute as pf


def prepare(doc):
	pass


def fenced_action(options, data, element, doc):
	# if doc.format == 'latex':
	# 	pass
	# 	# return None -> element unchanged
	# 	# return [] -> delete element

	result = None
	if doc.format == 'html':
		result = pf.convert_text(f"<div class = \"epigraph\">{options.get('my_key_1')}<span class = \"who\">{options.get('my_key_2')}</span></div>")

	elif doc.format == "markdown":
		# print("Got markdown block: ",options,data,element) 
		# todo - implement logging?
		# result = element

		result = pf.convert_text(f"Gooootooo in yaml filter: {options}, {data}, {element}")

	#print("Doc format was ", doc.format)

	return result


def finalize(doc):
	pass


def main(doc=None):
	return pf.run_filter(pf.yaml_filter, prepare=prepare, finalize=finalize,
						 tag='parts', function=fenced_action, doc=doc) 
	# Alternatively:
	# tags = {'sometag': fenced_action, 'another_tag': another_action}
	# return pf.run_filter(... , tags=tags, doc=doc)


if __name__ == '__main__':
	main()
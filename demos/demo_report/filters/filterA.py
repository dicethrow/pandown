import panflute as pf
import sys

def parts_yaml_filter(options, data, element, doc):

	if isinstance(element, pf.Strong):
		return pf.Emph(*element.content)

	result = []
	if doc.format == 'html':
		result = pf.convert_text(f"<div class = \"epigraph\">{options.get('my_key_1')}<span class = \"who\">{options.get('my_key_2')}</span></div>")

	elif doc.format == "markdown":
		# print("Got markdown block: ",options,data,element) 
		# todo - implement logging?
		# result = element

		result = pf.convert_text(f"Got in yaml filter: {options}, {data}, {element}")

	#print("Doc format was ", doc.format)

	return result


# def action(elem, doc):
# 	if isinstance(elem, pf.Strong):
# 		return pf.Emph(*elem.content)


	# result = pf.convert_text(f"Got in filterB: {elem}")
	# return result

if __name__ == '__main__':
	pf.toJSONFilter(pf.yaml_filter,tags = {'parts': parts_yaml_filter})
	# pf.toJSONFilter(action)
	
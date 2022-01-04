import panflute as pf

def parts_yaml_filter(options, data, element, doc):
	result = []
	if doc.format == 'html':
		result = pf.convert_text(f"<div class = \"epigraph\">{options.get('my_key_1')}<span class = \"who\">{options.get('my_key_2')}</span></div>")

	elif doc.format == "markdown":
		# print("Got markdown block: ",options,data,element) 
		# todo - implement logging?
		# result = element

		result = pf.convert_text(f"Got {options}, {data}, {element}")

	#print("Doc format was ", doc.format)

	return result

if __name__ == '__main__':
	pf.toJSONFilter(pf.yaml_filter,tags = {'parts': parts_yaml_filter})


	
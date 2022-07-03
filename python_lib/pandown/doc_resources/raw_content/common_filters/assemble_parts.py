

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

def get_depth(path):
	return path.count("/")

def decode_yaml_content(elem):
	# Split YAML and data parts (separated by ... or ---)
	raw = re.split("^([.]{3,}|[-]{3,})$",
					elem.text, 1, re.MULTILINE)
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

def get_list_of_next_content_files(starting_dir, decoded_yaml_data):
	subfolders = decoded_yaml_data.split("\n")
	return subfolders

def add_referred_content(elem, doc):
	def fix_image_path_dir_from_paragraph(para_elem, base_path):
		for elem in para_elem.content:
			if isinstance(elem, pf.Image):
				# make the image URL respect the full path
				img_path = os.path.join(base_path, elem.url)
				# pf.debug(f"new img path: {img_path}")
				elem.url = img_path

	def join_then_make_relative_image_paths(_next_foldername, _new_elem):
		for newnew_elem in _new_elem.content:
			if isinstance(newnew_elem, pf.Image):
				# make the image URL respect the full path
				img_path = os.path.join(doc.next_file_links_starting_dir, _next_foldername, newnew_elem.url)
				# pf.debug(f"new path: {img_path}")
				newnew_elem.url = img_path

				if doc.format == "html":
					# now make it relative to the output directory, if HTML
					newnew_elem.url = os.path.relpath(newnew_elem.url, doc.get_metadata("output_dir"))


	# if elem.parent == doc:
	# 	debug_elem(elem)

	if isinstance(elem, pf.CodeBlock):
		if "parts" in elem.classes:
			options, data = decode_yaml_content(elem)		

			level_offset = options["level_offset"] if "level_offset" in options	else 0
			
			outer_divs = []
			for next_foldername in get_list_of_next_content_files(doc.next_file_links_starting_dir, data):
				next_filename_full = os.path.join(doc.next_file_links_starting_dir, next_foldername, "main.md")
				with open(next_filename_full) as f:
					new_elems = pf.convert_text(f.read())

					# pf.debug(f"************ {next_filename_full} ************")
		
					for new_elem in new_elems:
						if isinstance(new_elem, pf.Header):
							new_elem.level += get_depth(os.path.join(doc.next_file_links_starting_dir, next_foldername)) - doc.initial_folder_depth + level_offset

							# # if header level is 1, make it a latex part
							# # for all other header levels, reduce them by one
							# debug_elem(new_elem)
							# pf.debug("level: ", new_elem.level)
							# if new_elem.level == 1:
							# 	# print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
							# 	# debug_elem(new_elem)
							# 	# similar to here https://stackoverflow.com/questions/62491816/how-do-i-get-pandoc-to-generate-book-parts
							# 	new_elem = pf.RawInline(f"\part{{new_elem.text}}", format="latex") # or tex?
							# 	# debug_elem(new_elem)
							# else:
							# 	new_elem.level -= 1
							# # print(new)

						if isinstance(new_elem, pf.Para):
							fix_image_path_dir_from_paragraph(para_elem=new_elem, base_path=os.path.join(doc.next_file_links_starting_dir, next_foldername))

							join_then_make_relative_image_paths(next_foldername, new_elem)

					outer_divs.append(pf.Div(*new_elems, attributes={'source': next_filename_full}))
					# outer_divs.append(new_elems)
			
			# div = pf.Div(*outer_divs, attributes={'source': doc.next_file_links_starting_dir})
			div = outer_divs
			return div
	
	if doc.initial_run:
		# if isinstance(o, t)
		if isinstance(elem, pf.Para):
			fix_image_path_dir_from_paragraph(para_elem=elem, base_path=os.path.join(doc.next_file_links_starting_dir))

			join_then_make_relative_image_paths(os.path.join(doc.next_file_links_starting_dir), elem)

	
					

def check_for_more_file_links(elem, doc):
	if isinstance(elem, pf.CodeBlock):
		if "parts" in elem.classes:
			doc.file_links_present = True
			# debug_elem(elem)

			if isinstance(elem.parent, pf.Div):
				# note that this can only handle one instance of file references,
				# but that's OK as elsewhere this will be called until all done
				markdown_file_that_contains_the_file_links = elem.parent.attributes["source"]
				folder_containing_the_data = os.path.abspath(os.path.join(markdown_file_that_contains_the_file_links, ".."))
				doc.next_file_links_starting_dir = folder_containing_the_data
			
				# pf.debug(f"Next folder: {doc.next_file_links_starting_dir}")

def make_top_level_headings_into_parts(elem, doc):
	if doc.format == "latex":
		if isinstance(elem, pf.Header):
			# if header level is 1, make it a latex part
			# for all other header levels, reduce them by one
			# debug_elem(elem)
			# pf.debug("level: ", elem.level)
			if elem.level == 1:
				# print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
				# debug_elem(new_elem)
				# similar to here https://stackoverflow.com/questions/62491816/how-do-i-get-pandoc-to-generate-book-parts
				part_title_str = pf.stringify(elem)
				part_title_str = part_title_str.replace("_", "\_") 
				elem = pf.RawBlock(f"\part{{{part_title_str}}}", format="latex") # or tex?
				# pf.debug("changed:")
				# debug_elem(elem)
			else:
				elem.level -= 1
			# print(new)
			# return [elem]
			return elem

def inspect_doc(elem, doc):
	debug_elem(elem)


def main(doc=None):
	# doc = pf.Doc(pf.Para(pf.Str("hello")))
	# doc.new_doc = copy.deepcopy(doc)

	doc.file_links_present = False
	doc = doc.walk(check_for_more_file_links)
	doc.initial_run = True
	doc.next_file_links_starting_dir = os.path.expanduser(doc.get_metadata("starting_dir"))
	doc.initial_folder_depth = get_depth(doc.next_file_links_starting_dir)
	while doc.file_links_present:
		doc = doc.walk(add_referred_content)
		# doc.walk(inspect_doc)
		doc.file_links_present = False
		doc = doc.walk(check_for_more_file_links)
		doc.initial_run = False
	doc = doc.walk(make_top_level_headings_into_parts)

	return doc

if __name__ == '__main__':
	main()

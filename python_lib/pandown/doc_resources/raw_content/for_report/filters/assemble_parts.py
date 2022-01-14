

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
				pf.debug(f"new path: {img_path}")
				elem.url = img_path


	# if elem.parent == doc:
	# 	debug_elem(elem)

	if isinstance(elem, pf.CodeBlock):
		if "parts" in elem.classes:
			options, data = decode_yaml_content(elem)			
			
			outer_divs = []
			for next_foldername in get_list_of_next_content_files(doc.next_file_links_starting_dir, data):
				next_filename_full = os.path.join(doc.next_file_links_starting_dir, next_foldername, "main.md")
				with open(next_filename_full) as f:
					new_elems = pf.convert_text(f.read())

					# pf.debug(f"************ {next_filename_full} ************")
		
					for new_elem in new_elems:
						if isinstance(new_elem, pf.Header):
							new_elem.level += get_depth(os.path.join(doc.next_file_links_starting_dir, next_foldername)) - doc.initial_folder_depth

						if isinstance(new_elem, pf.Para):
							fix_image_path_dir_from_paragraph(para_elem=new_elem, base_path=os.path.join(doc.next_file_links_starting_dir, next_foldername))
							

							for newnew_elem in new_elem.content:
								if isinstance(newnew_elem, pf.Image):
									# make the image URL respect the full path
									img_path = os.path.join(doc.next_file_links_starting_dir, next_foldername, newnew_elem.url)
									# pf.debug(f"new path: {img_path}")
									newnew_elem.url = img_path

					outer_divs.append(pf.Div(*new_elems, attributes={'source': next_filename_full}))
					# outer_divs.append(new_elems)
			
			# div = pf.Div(*outer_divs, attributes={'source': doc.next_file_links_starting_dir})
			div = outer_divs
			return div
	
	if doc.initial_run:
		# if isinstance(o, t)
		if isinstance(elem, pf.Para):
			fix_image_path_dir_from_paragraph(para_elem=elem, base_path=os.path.join(doc.next_file_links_starting_dir))

	
					

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
			
				pf.debug(f"Next folder: {doc.next_file_links_starting_dir}")

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

	return doc

if __name__ == '__main__':
	main()

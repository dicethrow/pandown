

import panflute as pf
import subprocess, os, yaml, re, pprint, copy, shutil, pathlib

import urllib 
from pandown import run_local_cmd, debug_elem 

already_added_parts = {}

from copy_linked_items import file_formats_that_link_content, file_formats_that_embed_content

# from pandown import loggerClass
# logging.setLoggerClass(loggerClass)
# log = logging.getLogger(__name__)

def get_depth(path):
	path = pathlib.Path(path)
	depth = len(path.parents)
	return depth
	# if path.startswith("./"):
		# path = path.split("./")[1:] # remove it?

	# return path.count("/")


# def decode_yaml_content(elem):
# 	# Split YAML and data parts (separated by ... or ---)
# 	raw = re.split("^([.]{3,}|[-]{3,})$",
# 					elem.text, 1, re.MULTILINE)
# 	data = raw[2] if len(raw) > 2 else ''
# 	data = data.lstrip('\n')
# 	raw = raw[0]
# 	try:
# 		options = yaml.safe_load(raw)
# 	except yaml.scanner.ScannerError:
# 		debug("panflute: malformed YAML block")
# 		return
# 	if options is None:
# 		options = {}
# 	return options, data

def get_list_of_next_content_files(starting_dir, decoded_yaml_data):
	subfolders = decoded_yaml_data.split("\n")
	return subfolders

def fix_referred_file_path_dir_from_container_element(container_elem, base_path):
	for elem in container_elem.content:
		if isinstance(elem, pf.Image):
			# make the image URL respect the full path
			url_as_local_path = urllib.parse.unquote(elem.url) # to get rid of things like %20, if present #elem.url.replace('%20', ' ')
			img_path = os.path.join(base_path, pathlib.Path(url_as_local_path))
			pf.debug(f"new img path: {img_path} from {base_path} and {elem.url}")
			assert os.path.isfile(img_path)
			elem.url = str(img_path)

		elif isinstance(elem, pf.Link):
			# only update links that refer to local files.
			# don't mess with links that might refer to online stuff
			# pf.debug("elem.url: ", elem.url)
			url_as_local_path = urllib.parse.unquote(elem.url) # to get rid of things like %20, if present #elem.url.replace('%20', ' ')
			pf.debug(f"This is url_as_local_path: {elem.url} and {url_as_local_path}")
			item_path = os.path.join(base_path, pathlib.Path(url_as_local_path))
			if os.path.isfile(item_path):
				elem.url = str(item_path)
				# pf.debug(f"This is a file: {elem.url} as {item_path}")
			# else:
				# pf.debug(f"This is not a file: {elem.url} as {item_path}")

def join_then_make_relative_file_paths_and_copy(doc, _next_foldername, _new_elem):
	for newnew_elem in _new_elem.content:

		# images and links
		if hasattr(newnew_elem, "url"):
			if os.path.isfile(newnew_elem.url):
				url = pathlib.Path(newnew_elem.url).resolve()
				# make the image URL respect the full path
	
				# HTML will only work portably if a relative path is always used.
				# latex/PDF will only work with images with absolute paths (yuck!)
				# but links to files can always be relative
				if doc.format in file_formats_that_link_content or isinstance(newnew_elem, pf.Link):
					newnew_elem.url = os.path.relpath(url, doc.get_metadata("output_dir"))
					pf.debug("> ", newnew_elem.url)

def handle_parts_block(options, data, element, doc):

	assert isinstance(element, pf.CodeBlock) & ("parts" in element.classes), "Assuming parts blocks"
	initial_level_offset = options["level_offset"] if "level_offset" in options	else 0

	elem = element
	
	outer_divs = []

	# pf.debug(f"doc.next_file_links_starting_dir: {doc.next_file_links_starting_dir}")

	# get the directory where the current parts are relative to.
	# either the document itself, or the parent file
	if elem.parent == doc:
		parts_base_path = doc.next_file_links_starting_dir
	else: # if doc
		parts_base_path = pathlib.Path(elem.parent.attributes['source']).parent

	for next_file_or_foldername in get_list_of_next_content_files(parts_base_path, data):

		full_dir_path = parts_base_path / next_file_or_foldername
		# pf.debug("full_dir_path: ", full_dir_path)

		# next_foldername = ""
		# next_filename_full = ""
		if os.path.isdir(full_dir_path):
			next_filename_full = full_dir_path / "main.md" # os.path.join(full_dir_path, "main.md")
			# next_foldername = full_dir_path
			level_offset = initial_level_offset
		else:
			next_filename_full = full_dir_path if full_dir_path.suffix == ".md" else full_dir_path.with_suffix(".md")
			# next_foldername = os.path.dirname(full_dir_path)
			level_offset = initial_level_offset + 1 # this was observed to be necessary to make the heading levels be consistent
	
		# pf.debug(f"next_filename_full: {next_filename_full}")
		# pf.debug(f"next_foldername: {next_foldername}")

		assert os.path.isfile(next_filename_full), f"Could not find file {next_filename_full}" # 
		assert os.path.isdir(next_filename_full.parent), f"Could not find folder {next_filename_full.parent}"

		with open(next_filename_full) as f:
			s = f.read()
			pf.debug(s)
			new_elems = pf.convert_text(s)

			# pf.debug(f"************ {next_filename_full.parent} ************")

			def handle_sub_elem(subelem):
				if hasattr(subelem, "content"):
					for subsubelem in subelem.content:
						handle_sub_elem(subsubelem)

				if isinstance(subelem, pf.Header):
					subelem.level += get_depth(next_filename_full.parent) - doc.initial_folder_depth + level_offset

					# # if header level is 1, make it a latex part
					# # for all other header levels, reduce them by one
					# debug_elem(subelem)
					# pf.debug("level: ", subelem.level)
					# if subelem.level == 1:
					# 	# print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
					# 	# debug_elem(subelem)
					# 	# similar to here https://stackoverflow.com/questions/62491816/how-do-i-get-pandoc-to-generate-book-parts
					# 	subelem = pf.RawInline(f"\part{{subelem.text}}", format="latex") # or tex?
					# 	# debug_elem(subelem)
					# else:
					# 	subelem.level -= 1
					# # print(new)

				if hasattr(subelem, "content"):
					fix_referred_file_path_dir_from_container_element(container_elem=subelem, base_path=next_filename_full.parent)
					join_then_make_relative_file_paths_and_copy(doc, next_filename_full.parent, subelem)

			for new_elem in new_elems:
				# debug_elem(new_elem)

				handle_sub_elem(new_elem)


				

			outer_divs.append(pf.Div(*new_elems, attributes={'source': str(next_filename_full)}))
			# outer_divs.append(new_elems)
	
	# div = pf.Div(*outer_divs, attributes={'source': doc.next_file_links_starting_dir})
	div = outer_divs
	return div
	
	# if doc.initial_run:
	# 	# if isinstance(o, t)
	# 	if isinstance(elem, pf.Para):
	# 		fix_image_path_dir_from_paragraph(container_elem=elem, base_path=os.path.join(doc.next_file_links_starting_dir))

	# 		join_then_make_relative_image_paths(os.path.join(doc.next_file_links_starting_dir), elem)

def handle_root_file_images(elem, doc):
	if doc.initial_run:
		if hasattr(elem, "content"):
			fix_referred_file_path_dir_from_container_element(container_elem=elem, base_path=os.path.join(doc.next_file_links_starting_dir))

			join_then_make_relative_file_paths_and_copy(doc, os.path.join(doc.next_file_links_starting_dir), elem)

def check_for_more_file_links(elem, doc):
	if isinstance(elem, pf.CodeBlock):
		if "parts" in elem.classes:
			doc.file_links_present = True
		

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

def handle_forbidden_characters(elem, doc):
	if doc.format == "latex":
		...


def inspect_doc(elem, doc):
	debug_elem(elem)


def main(doc=None):
	doc.file_links_present = False
	doc = doc.walk(check_for_more_file_links)
	doc.initial_run = True
	doc.next_file_links_starting_dir = pathlib.Path(doc.get_metadata("starting_dir")).expanduser()
	doc.initial_folder_depth = get_depth(doc.next_file_links_starting_dir)
	while doc.file_links_present:
		pf.debug("Loop!")
		# doc = doc.walk(add_referred_content)
		doc = pf.run_filter(pf.yaml_filter, tag="parts", function=handle_parts_block, doc=doc, strict_yaml=True)
		doc = pf.run_filter(handle_root_file_images, doc=doc)
		# doc.walk(inspect_doc)
		doc.file_links_present = False
		doc = doc.walk(check_for_more_file_links)
		doc.initial_run = False
	doc = doc.walk(make_top_level_headings_into_parts)
	doc = doc.walk(handle_forbidden_characters)
	return doc

if __name__ == '__main__':
	main()

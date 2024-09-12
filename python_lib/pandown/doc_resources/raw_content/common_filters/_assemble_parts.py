

import panflute as pf
import subprocess, os, yaml, re, pprint, copy, shutil, pathlib

import urllib 
from pandown import run_local_cmd, debug_elem 
from pandown.common import get_ordered_list_of_markdown_files_recursively_from

already_added_parts = {}

from copy_linked_items import file_formats_that_link_content, file_formats_that_embed_content

# from pandown import loggerClass
# logging.setLoggerClass(loggerClass)
# log = logging.getLogger(__name__)

def fix_referred_file_path_dir_from_container_element(container_elem, base_path):
	for elem in container_elem.content:
		if isinstance(elem, pf.Image):
			# make the image URL respect the full path
			url_as_local_path = urllib.parse.unquote(elem.url) # to get rid of things like %20, if present #elem.url.replace('%20', ' ')
			img_path = os.path.join(base_path, pathlib.Path(url_as_local_path))
			pf.debug(f"new img path: {img_path} from {base_path} and {elem.url}")
			assert os.path.isfile(img_path), f"image not found: {img_path}"
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

def join_then_make_relative_file_paths_and_copy(doc, _new_elem):
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



def handle_forbidden_characters(elem, doc):
	if doc.format == "latex":
		...

def main(doc=None):
	starting_dir = pathlib.Path(doc.get_metadata("starting_dir")).expanduser()
	src_files = get_ordered_list_of_markdown_files_recursively_from(starting_dir)

	content = []

	pf.debug(f"{len(src_files)} source files found from {starting_dir}")

	for src_file, depth in src_files:

		assert src_file.is_file(), f"This file not found: {src_file}"

		with open(src_file) as f:
			s = f.read() 
		
			if len(s) == 0:
				pf.debug(f"Opening file {src_file.relative_to(starting_dir)}: Empty file, skipping")
				new_elems = []
			else:
				pf.debug(f"Opening file: {src_file.relative_to(starting_dir)}: Parsing")
				new_elems = pf.convert_text(s)

		def handle_sub_elem(subelem):
			if hasattr(subelem, "content"):
				for subsubelem in subelem.content:
					handle_sub_elem(subsubelem)
			
			if isinstance(subelem, pf.Header):
				subelem.level += depth # ??
			
			if hasattr(subelem, "content"): # but content section above?
				fix_referred_file_path_dir_from_container_element(container_elem=subelem, base_path=src_file.parent)
				join_then_make_relative_file_paths_and_copy(doc, subelem)

		for subelem in new_elems:
			handle_sub_elem(subelem)

		content.append(pf.Div(*new_elems, attributes={'source': str(src_file)}))

	doc.content.append(pf.Div(*content))

if __name__ == '__main__':
	main()

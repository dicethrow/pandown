

import panflute as pf
import subprocess, os, yaml, re, pprint, copy, shutil, pathlib
import hashlib
from pandown import run_local_cmd, debug_elem 


# This assumes a single file is passed with valid links to src content.

# If the file format does not embed the content, then this filter
# will copy the used content to `/output_<format>/generated_output_files/`
# which can then be copied with `result.<format>` so that it can be used
# in a portable way. e.g. for .html.

# Even for formats like .pdf which embed images, this will still work
# to make copies of local files that are linked in the PDF.
# The PDF and the local file contaner could be distributed in a zip,
# so that the `generated_output_files` folder is always adjacent.

file_formats_that_embed_content = ["latex"]
file_formats_that_link_content = ["html"]

file_hashes_already_copied = []

def copy_linked_items(elem, doc):

	toCopyElement = False
	

	if doc.format in file_formats_that_embed_content:
		if isinstance(elem, pf.Link):
			url = pathlib.Path(doc.get_metadata("output_dir")) / elem.url
			if url.exists():
				# then it's a link to a file that should be copied
				toCopyElement = True
			else:
				# then a link to a website, shouldn't be copied
				toCopyElement = False
	elif doc.format in file_formats_that_link_content:
		if isinstance(elem, pf.Link) or isinstance(elem, pf.Image):
			url = pathlib.Path(doc.get_metadata("output_dir")) / elem.url
			if url.exists():
				# then it's a link to a file that should be copied
				toCopyElement = True
			else:
				# then a link to a website, shouldn't be copied
				toCopyElement = False

	if toCopyElement:

		url = url.resolve()

		content_dir = pathlib.Path(doc.get_metadata("starting_dir"))
		generated_intermediate_files_dir = pathlib.Path(doc.get_metadata("generated_intermediate_files_dir"))
		generated_output_files_dir = pathlib.Path(doc.get_metadata("generated_output_files_dir"))
		
		if url.is_relative_to(content_dir):
			pf.debug("Relative to content: ", url)
			relative_url = url.relative_to(content_dir)
			desired_new_full_path = generated_output_files_dir / "content" / relative_url

		elif url.is_relative_to(generated_intermediate_files_dir):
			pf.debug("Relative to generated_intermediate_files_dir: ", url)
			relative_url = url.relative_to(generated_intermediate_files_dir)
			desired_new_full_path = generated_output_files_dir / relative_url

		else:
			pf.debug("Is external: ", url)
			# hash so same-named files are not overwritten
			# but not random, so files with the same path will have the same hash
			hash_str = hashlib.sha256(str(url).encode()).hexdigest()[:12] 
			desired_new_full_path = generated_output_files_dir / "external" / hash_str /  url.name

		# 1. copy the url to the new location,
		# to check if this file has already been copied, 
		if not os.path.isfile(desired_new_full_path): # the file might be linked to several times, only copy on the first time
			desired_new_full_path.parent.mkdir(parents=True, exist_ok=True)
			shutil.copy2(url, desired_new_full_path) # copy2 to try to preserve metadata

		# 2. calculate a relative url from the html/pdf document that points to the new location
		rel_path = "." + os.sep + os.path.relpath(desired_new_full_path, doc.get_metadata("output_dir"))
		pf.debug("rel path: ", rel_path)

		elem = type(elem)(pf.Str(pf.stringify(elem)),
			url = str(rel_path),
			title = elem.title,identifier  = elem.identifier,classes = elem.classes,attributes = elem.attributes)

		return elem

# # this is to see what the link goes to, even if the link isnt working
# def show_url_in_link_name(elem, doc):
# 	if isinstance(elem, pf.Link):

# 		# to make links display the path/url
# 		existing_str = pf.stringify(elem)
# 		if "[" and "]" in existing_str:
# 			pf.debug("Double! " + str(type(elem)) + existing_str)
# 			# this is bad, shouldn't happen
# 		else:
# 			pf.debug("OK" + str(type(elem)) + existing_str)

# 		new_label = f"{pf.stringify(elem)} [{elem.url}]"
# 		elem = pf.Link(pf.Str(new_label),url = elem.url,title = elem.title,
# 			identifier  = elem.identifier,classes = elem.classes,attributes = elem.attributes)
		
# 		return elem

def main(doc=None):

	# if doc.format in file_formats_that_link_content:
	# 	if os.path.isdir(doc.get_metadata("generated_output_files_dir")):
	# 		shutil.rmtree(doc.get_metadata("generated_output_files_dir")) # to remove any previous items

	doc = doc.walk(copy_linked_items)
	# doc = doc.walk(show_url_in_link_name)
	return doc

if __name__ == '__main__':
	main()

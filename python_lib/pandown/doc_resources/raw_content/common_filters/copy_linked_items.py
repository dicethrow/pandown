

import panflute as pf
import subprocess, os, yaml, re, pprint, copy, shutil, pathlib

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




def copy_linked_items(elem, doc):

	toCopyElement = False

	if doc.format in file_formats_that_embed_content:
		if isinstance(elem, pf.Link):
			toCopyElement = True
	elif doc.format in file_formats_that_link_content:
		if isinstance(elem, pf.Link) or isinstance(elem, pf.Image):
			toCopyElement = True


	if toCopyElement:
		def resolveURLAsLocal(relativeURL):
			return pathlib.Path(os.path.join(doc.get_metadata("output_dir"), pathlib.Path(relativeURL))).resolve()

		url = resolveURLAsLocal(elem.url)
		# pf.debug(f"Tests: {doc.format in file_formats_that_embed_content}, {os.path.isfile(url)}, {url}")
		# pf.debug(doc.get_metadata("output_dir"))
		# If it is a link - lets change the text so it shows the URL

		if os.path.isfile(url):
			# otherwise, it could be referring to a website

			# 1. find the new file location that we want to copy it to
			# at the point where it says 'content', we want it to be in `generated_output_files`. if no content found, then copy it to the root of `generated_output_files`
			doc_dir = os.path.dirname(doc.get_metadata("output_dir"))
			content_dir = os.path.join(doc_dir, "content")

			location_from_doc_dir = os.path.relpath(url, doc_dir)
			desired_path = location_from_doc_dir # simpler for now
			# if "content" in location_from_doc_dir:
				# go down one level
				# desired_path = os.path.relpath(location_from_doc_dir, "content")
			# elif "generated_intermediate_files" in location_from_doc_dir:
				# desired_path = pathlib.Path(os.path.relpath(location_from_doc_dir, os.path.join(doc.get_metadata("output_dir"), "generated_intermediate_files"))).resolve()
			if "../" in location_from_doc_dir:
				desired_path = os.path.join("external", os.path.basename(location_from_doc_dir))

			# pf.debug(f"location_from_doc_dir: {location_from_doc_dir} to {desired_path}")
			

			desired_full_path = os.path.join(doc.get_metadata("generated_output_files_dir"), desired_path)
			# now we know the current location of the item, and where we want it to go. so now we copy it, and update the url to refer to the new copy.
			if not os.path.isfile(desired_full_path): # the file might be linked to several times
				# pf.debug("File doesnt exist yet")

				target_path = pathlib.Path(os.path.dirname(desired_full_path))
				target_path.mkdir(parents=True, exist_ok=True)

				# copy2 to try to preserve metadata
				shutil.copy2(pathlib.Path(url), pathlib.Path(desired_full_path))


			desired_path_relative_to_final_doc = os.path.relpath(desired_full_path, doc.get_metadata("output_dir"))
			elem = type(elem)(pf.Str(pf.stringify(elem)),
				url = "./" + desired_path_relative_to_final_doc,
				title = elem.title,identifier  = elem.identifier,classes = elem.classes,attributes = elem.attributes)
			
			# else:
				# pf.debug(f"File exists: {dst}")
			return elem 
	

	
	# doc.get_metadata("generated_output_files_dir")
	...
	# if doc.format == "html":
	# if doc.format in file_formats_that_link_content:
	# if False:
	# 	relative_src_path = os.path.relpath(newnew_elem.url, doc.next_file_links_starting_dir)
	# 	# pf.debug(f"relative_src_path: {relative_src_path}")

	# 	# set the URL to refer to where the files will be,
	# 	# then copy the files to that 
	# 	src = newnew_elem.url
	# 	dst = os.path.join(doc.folderToStoreLinkedFilesIn, relative_src_path)
	# 	if not os.path.isfile(dst): # the file might be linked to several times
	# 		# pf.debug("File doesnt exist yet")
	# 		dst_folder = os.path.dirname(dst)

	# 		target_path = pathlib.Path(dst_folder)
	# 		target_path.mkdir(parents=True, exist_ok=True)

	# 		# copy2 to try to preserve metadata
	# 		shutil.copy2(pathlib.Path(src), pathlib.Path(dst_folder))
	# 	# else:
	# 		# pf.debug(f"File exists: {dst}")

	# 	newnew_elem.url = dst
	# 	# pf.debug(f"new dst: {dst}")

	# 	# now make it relative to the output directory, if HTML
	# 	newnew_elem.url = os.path.relpath(newnew_elem.url, doc.get_metadata("output_dir"))

# this is to see what the link goes to, even if the link isnt working
def show_url_in_link_name(elem, doc):
	if isinstance(elem, pf.Link):

		# to make links display the path/url
		existing_str = pf.stringify(elem)
		if "[" and "]" in existing_str:
			pf.debug("Double! " + str(type(elem)) + existing_str)
			# this is bad, shouldn't happen
		else:
			pf.debug("OK" + str(type(elem)) + existing_str)

		new_label = f"{pf.stringify(elem)} [{elem.url}]"
		elem = pf.Link(pf.Str(new_label),url = elem.url,title = elem.title,
			identifier  = elem.identifier,classes = elem.classes,attributes = elem.attributes)
		
		return elem

def main(doc=None):

	# if doc.format in file_formats_that_link_content:
	# 	if os.path.isdir(doc.get_metadata("generated_output_files_dir")):
	# 		shutil.rmtree(doc.get_metadata("generated_output_files_dir")) # to remove any previous items

	doc = doc.walk(copy_linked_items)
	# doc = doc.walk(show_url_in_link_name)
	return doc

if __name__ == '__main__':
	main()

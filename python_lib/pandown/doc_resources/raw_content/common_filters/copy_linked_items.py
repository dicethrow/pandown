
# This assumes a single file is passed with valid links to src content

file_formats_that_copy_content = ["pdf"]
file_formats_that_link_content = ["html"]


def copy_linked_items():
	doc.get_metadata("generated_output_files_dir")
	...
	# if doc.format == "html":
	# if doc.format in file_formats_that_link_content:
	if False:
		relative_src_path = os.path.relpath(newnew_elem.url, doc.next_file_links_starting_dir)
		# pf.debug(f"relative_src_path: {relative_src_path}")

		# set the URL to refer to where the files will be,
		# then copy the files to that 
		src = newnew_elem.url
		dst = os.path.join(doc.folderToStoreLinkedFilesIn, relative_src_path)
		if not os.path.isfile(dst): # the file might be linked to several times
			# pf.debug("File doesnt exist yet")
			dst_folder = os.path.dirname(dst)

			target_path = pathlib.Path(dst_folder)
			target_path.mkdir(parents=True, exist_ok=True)

			# copy2 to try to preserve metadata
			shutil.copy2(pathlib.Path(src), pathlib.Path(dst_folder))
		# else:
			# pf.debug(f"File exists: {dst}")

		newnew_elem.url = dst
		# pf.debug(f"new dst: {dst}")

		# now make it relative to the output directory, if HTML
		newnew_elem.url = os.path.relpath(newnew_elem.url, doc.get_metadata("output_dir"))

def main(doc=None):

	# if doc.format in file_formats_that_link_content:
	# 	if os.path.isdir(doc.get_metadata("generated_output_files_dir")):
	# 		shutil.rmtree(doc.get_metadata("generated_output_files_dir")) # to remove any previous items

	doc = doc.walk(copy_linked_items)
	return doc

if __name__ == '__main__':
	main()
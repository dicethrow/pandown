# this is so we can share common/starter files between projects
# to avoid code duplication for things like templates and filters

# if a doc project wants more custom stuff, then it can copy/paste the files
# desired and not use these functions
import os, shutil

def get_absolute_content_dir(relative_path_to_containing_folder):
	#  relative_path_to_containing_folder is a string like "for_report/filters" or "for_report"
	# and do error checking to make sure it exists?
	dir_path = os.path.dirname(os.path.realpath(__file__))
	for foldername in str("raw_content/" + relative_path_to_containing_folder).split("/"):
		dir_path = os.path.join(dir_path, foldername)

	assert os.path.isdir(dir_path), "The provided path does not refer to a valid directory"

	return dir_path

def copy_starter_resources(src, dst, skip_if_dest_not_empty = True):
	for desired_dir_or_file in src:
		srcpath = os.path.dirname(os.path.realpath(__file__))
		for foldername in str("raw_content/" + desired_dir_or_file).split("/"):
			srcpath = os.path.join(srcpath, foldername)
	
		destpath = os.path.join(dst, desired_dir_or_file)
		if os.path.isfile(srcpath):
			shutil.copy(srcpath, destpath)
		elif os.path.isdir(srcpath):
			dst
			if os.path.exists(destpath):
				if skip_if_dest_not_empty:
					pass
				else:
					assert 0, "dir already exists, no behavior defined"
			else:
				shutil.copytree(srcpath, destpath)				
					
		else:
			assert 0, f"Given srcpath is not a directory or file: {srcpath}"

if __name__ == "__main__":
	# p = get_absolute_content_dir("for_report/filters")
	p = get_absolute_content_dir("for_report")
	print(p)
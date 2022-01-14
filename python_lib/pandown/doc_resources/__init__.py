# this is so we can share common/starter files between projects
# to avoid code duplication for things like templates and filters

# if a doc project wants more custom stuff, then it can copy/paste the files
# desired and not use these functions
import os

def get_absolute_content_dir(relative_path_to_containing_folder):
	#  relative_path_to_containing_folder is a string like "for_report/filters" or "for_report"
	# and do error checking to make sure it exists?
	dir_path = os.path.dirname(os.path.realpath(__file__))
	for foldername in str("raw_content/" + relative_path_to_containing_folder).split("/"):
		dir_path = os.path.join(dir_path, foldername)

	assert os.path.isdir(dir_path), "The provided path does not refer to a valid directory"

	return dir_path

if __name__ == "__main__":
	# p = get_absolute_content_dir("for_report/filters")
	p = get_absolute_content_dir("for_report")
	print(p)
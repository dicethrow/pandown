import argparse, os, subprocess, textwrap
from glob import glob
import subprocess
import shutil
import panflute as pf

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

# copied from lxdev.run_local_cmd
def run_local_cmd(cmd, **kwargs):
	def as_array(result_or_error):
		return result_or_error.decode("utf-8").split("\n")[:-1] if result_or_error != None else []

	# print(cmd, flush=True)
	print_result = kwargs.pop("print_result", False)
	print_error = kwargs.pop("print_error", False)
	print_cmd = kwargs.pop("print_cmd", False)

	if print_cmd:
		print("\n$ " + cmd)

	p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
	output, error = p.communicate()
	output = as_array(output)
	error = as_array(error)

	if print_result:
		for line in output:
			print(line)
	
	if print_error:
		for line in error:
			print(line)

	return output, error

def clear_terminal():
	# clean the terminal before we start.
	subprocess.call("clear")

def remove_generated_files(delete, except_for = []):
	# recommend to use glob for this function
	debug = False
	if debug: print(delete, except_for)
	for filename in delete:
		if filename in except_for:
			if debug: print(f"Not removing {filename}", end=" ")
			continue
		if debug: print(f"Removing {filename}", end=" ")
		try:
			os.remove(filename)
			if debug: print(f"with os.remove")
		except:
			shutil.rmtree(filename)
			if debug: print(f"with shutil.rmtree")


def xxx(keep_filetypes = []):
	deletableItems = []
	for each_dir in ["output", "generated_intermediate_files"]:
		deletableItems += glob(f"./doc/{each_dir}/*") 

	for filename in deletableItems:
		if any((t in filename) for t in keep_filetypes):
			continue
		else:
			# print(f"Removing {filename}", end=" ")
			try:
				os.remove(filename)
				# print(f"with os.remove")
			except:
				shutil.rmtree(filename)
				# print(f"with shutil.rmtree")

def add_yaml_entries_to_file(src_filename, dst_filename, new_header_lines):
	# do some manual changes to the top-level main.md document, before using panflute filters
	# previously, this had to be in the yaml header:
	#panflute-path: '~/from_host/x/Documents/git_repos/documentation/projects/workflow_with_lxd_zfs/doc/for_report/filters'
	#tarting_dir: "~/from_host/x/Documents/git_repos/documentation/projects/workflow_with_lxd_zfs/doc/content"
	with open(src_filename, "r") as f:
		lines = f.readlines()
	new_lines = []
	added_paths_yet = False
	for line in lines:
		if (line.strip() == "---") and not added_paths_yet:
			new_lines.append(line)
			# new_lines.append(f"panflute-path: '{doc_dir}/for_report/filters'\n")
			for new_line in new_header_lines:
				new_lines.append(new_line + "\n")
			added_paths_yet = True
		else:
			new_lines.append(line)
	with open(dst_filename, "w") as f:
		f.writelines(new_lines)
# default report build
from .doc_resources import get_path_to_common_content

import argparse, os, subprocess, textwrap
from glob import glob
import subprocess

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

def remove_generated_files(keep_filetypes = []):
	for filename in glob("./doc/output/*") + glob("./doc/generated_intermediate_files/*"):
		if any((t in filename) for t in keep_filetypes):
			continue
		else:
			try:
				os.remove(filename)
			except:
				os.rmdir(filename)

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

		
def build_default_report(template="test2.latex", debug_mode = False):
	# in the container, copy over the proj_location/content, and template
	# then, run the container:proj_location/build.py
	# which goes through the document and does its thing

	clear_terminal()

	# remove intermediate files from previous runs
	# remove_generated_files() # note - commented out, so the result.pdf is never removed; which makes vscode auto-reload the latest version of the file

	# display the current directory and its contents
	run_local_cmd("pwd", print_result = True)
	run_local_cmd("tree -a .", print_result=True)

	doc_dir = f"{run_local_cmd('pwd')[0][0]}/doc"

	script_runner = "-F " + os.path.expanduser("~/.local/bin/panflute")
	top_source_file = f"{doc_dir}/content/main.md"
	top_source_file_ammended = top_source_file.replace("content", "generated_intermediate_files")
	template_file = f"--template {get_path_to_common_content('for_report')}/templates/{template}"
	panflute_filters_path = f"{get_path_to_common_content('for_report')}/filters"
	extras = "--listings" # extras = ""

	# if_debug_mode = True
	if_debug_mode = debug_mode

	add_yaml_entries_to_file(
		src_filename = top_source_file, 
		dst_filename = top_source_file_ammended,
		new_header_lines = [
			f"panflute-path: '{panflute_filters_path}'",
			f"starting_dir: '{os.path.dirname(top_source_file)}'",
			f"generated_intermediate_files_dir: '{doc_dir}/generated_intermediate_files'"
		]
	)

	### from the .md use pandoc to make .tex
	latex_intermediate_file = f"{doc_dir}/generated_intermediate_files/result.latex"
	pandoc_cmd = f"pandoc {script_runner} {top_source_file_ammended} {template_file} -s -o {latex_intermediate_file} {extras}"
	result, error = run_local_cmd(pandoc_cmd, print_cmd = True, print_result = if_debug_mode, print_error=if_debug_mode)
	# assert error == [], "pandoc error"

	### from .tex make .pdf
	# lualatex needs to be caled twice, otherwise the toc doesn't generate properly. if references, call biber between
	latex_cmd = f'pdflatex --shell-escape -halt-on-error --output-directory doc/output doc/generated_intermediate_files/result.latex'  # options go before filename https://tex.stackexchange.com/questions/268997/pdflatex-seems-to-ignore-output-directory
	for repeats in range(2):
		run_local_cmd(latex_cmd, print_cmd = True, print_result = if_debug_mode, print_error = if_debug_mode)

	# remove everything except for desired filetypes
	# so things from latex, then file attachments such as images and csv
	remove_generated_files(keep_filetypes=[".pdf", ".latex", ".csv", ".svg", ".bmp"])


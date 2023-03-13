# default pdf build
from .doc_resources import get_path_to_common_content

import argparse, os, subprocess, textwrap
from glob import glob
import subprocess

from .common import run_local_cmd, clear_terminal, remove_generated_files, add_yaml_entries_to_file

		
def build_default_html(template="default/standalone.html", debug_mode = False):
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

	# check that the given template exists within the local project. If not, assume it's a default template
	if os.path.exists(f"{doc_dir}/templates/{template}"):
		template_file = f"--template {doc_dir}/templates/{template}"
	else:
		template_file = f"--template {get_path_to_common_content('html_templates')}/{template}" # todo: use os.path.join

	output_folder = f"{doc_dir}/output"
	
	panflute_filters_path = f"{get_path_to_common_content('common_filters')}"
	extras = "--listings" # extras = ""

	# if_debug_mode = True
	if_debug_mode = debug_mode

	add_yaml_entries_to_file(
		src_filename = top_source_file, 
		dst_filename = top_source_file_ammended,
		new_header_lines = [
			f"panflute-path: '{panflute_filters_path}'",
			f"starting_dir: '{os.path.dirname(top_source_file)}'",
			f"output_dir: '{output_folder}'",
			f"generated_intermediate_files_dir: '{doc_dir}/generated_intermediate_files'"
		]
	)


	### from the .md use pandoc to make .tex
	pandoc_cmd = "pandoc "
	pandoc_cmd += f"{script_runner} "
	pandoc_cmd += f"{top_source_file_ammended} "
	pandoc_cmd += template_file + " "
	pandoc_cmd += f"--standalone --table-of-contents --output {output_folder}/result.html "
	pandoc_cmd += f"{extras} "

	result, error = run_local_cmd(pandoc_cmd, print_cmd = True, print_result = if_debug_mode, print_error=if_debug_mode)
	# assert error == [], "pandoc error"
	
	# # unfortunately the whole filter's code is in the 'error' list. let's remove it
	# # technique using [:] allows edit in place, avoiding unnecessary copies? from https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
	
	# def keepLine(line):
	# 	exceptionDetected = False
	# 	status = False
	# 	if "Traceback (most recent call last):" in line:
	# 		# include this line and all following lines
	# 		exceptionDetected = True
	# 		status = True
	# 	elif exceptionDetected:
	# 		status = True
	# 	elif "Failed to run filter: " in line:
	# 		# just include this line
	# 		status = True
	# 	return status
	# error[:] = [line for line in error if keepLine(line)]

	from .errorRecogniser import errorRecogniser
	

	for line in error: 
		if "Exception" in line:
			errorRecogniser(error) # ah this doesnt work! need to work out how to handle stderr/stdout here.
			assert 0, "Pandown crashed, either a typo or a pandown bug needs fixing"

	# # print(result, error)
	# ### from .tex make .pdf
	# # lualatex needs to be caled twice, otherwise the toc doesn't generate properly. if references, call biber between
	# latex_cmd = f'pdflatex --shell-escape -halt-on-error --output-directory doc/output doc/generated_intermediate_files/result.latex'  # options go before filename https://tex.stackexchange.com/questions/268997/pdflatex-seems-to-ignore-output-directory
	# for repeats in range(2):
	# 	run_local_cmd(latex_cmd, print_cmd = True, print_result = if_debug_mode, print_error = if_debug_mode)

	# remove everything except for desired filetypes
	# so things from latex, then file attachments such as images and csv
	remove_generated_files(keep_filetypes=[".html", ".pdf", ".latex", ".csv", ".svg", ".bmp"])


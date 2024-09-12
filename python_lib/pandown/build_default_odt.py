# default odt build
from .doc_resources import get_path_to_common_content

import argparse, os, subprocess, textwrap, pathlib, shutil
from glob import glob
import subprocess

from contextlib import redirect_stdout, redirect_stderr

from .common import run_local_cmd, clear_terminal, remove_generated_files
from .errorRecogniser import pandocErrorRecogniser

def build_default_odt(template="default/standalone.html"):
	# in the container, copy over the proj_location/content, and template
	# then, run the container:proj_location/build.py
	# which goes through the document and does its thing

	clear_terminal()

	# remove intermediate files from previous runs
	# remove_generated_files() # note - commented out, so the result.pdf is never removed; which makes vscode auto-reload the latest version of the file

	# display the current directory and its contents
	run_local_cmd("pwd")
	run_local_cmd("tree -a .")

	doc_dir = f"{run_local_cmd('pwd')[0][0]}/doc"

	script_runner = "-F " + os.path.expanduser("~/.local/bin/panflute")
	top_source_file = f"{doc_dir}/content/main.md"
	output_folder = f"{doc_dir}/output_odt"

	# clean residue from last build process
	remove_generated_files(delete = [output_folder, f"{doc_dir}/output"])
 	# note that latex's minted code generates `output`, although we dont use it at the moment - messy
	
	# prepare files and directories for use with pandoc
	generated_intermediate_files_dir = os.path.join(output_folder, "generated_intermediate_files")
	top_source_file_ammended = os.path.join(generated_intermediate_files_dir, "main.md")
	
	desired_dirs = ["generated_intermediate_files", "generated_output_files"]
	for desired_dir in desired_dirs:
		target_path = pathlib.Path(os.path.join(output_folder, desired_dir))
		target_path.mkdir(parents=True, exist_ok=True)

	# check that the given template exists within the local project. If not, assume it's a default template
	if os.path.exists(f"{doc_dir}/templates/{template}"):
		template_file = f"--template {doc_dir}/templates/{template}"
	else:
		template_file = f"--template {get_path_to_common_content() / 'html_templates' /template}" # todo: use os.path.join
	
	panflute_filters_path = f"{get_path_to_common_content() / 'common_filters'}"
	extras = "--listings" # extras = ""

	# add_yaml_entries_to_file(
	# 	src_filename = top_source_file, 
	# 	dst_filename = top_source_file_ammended,
	# 	new_header_lines = [
	# 		f"panflute-path: '{panflute_filters_path}'",
	# 		f"starting_dir: '{os.path.dirname(top_source_file)}'",
	# 		f"output_dir: '{output_folder}'",			
	# 	] + [f"{d}_dir: '{pathlib.Path(os.path.join(output_folder, d))}'" for d in desired_dirs]
	# )


	### from the .md use pandoc to make .tex
	pandoc_cmd = "pandoc "
	pandoc_cmd += f"{script_runner} "
	pandoc_cmd += f"{top_source_file_ammended} "
	pandoc_cmd += template_file + " "
	pandoc_cmd += f"--standalone --table-of-contents --output {output_folder}/result.html "
	pandoc_cmd += f"{extras} "

	# 1. build HTML
	pandoc_logfile = os.path.join(generated_intermediate_files_dir,  "pandoc_log_tohtml.txt")
	with open(pandoc_logfile, "w", buffering=1) as stdoutfile, redirect_stdout(stdoutfile):
		result, error = run_local_cmd(pandoc_cmd, print_cmd = True)
	
		success = pandocErrorRecogniser(result, error)
	assert success, "Pandoc failure, see log"

	# 2. turn the HTML into .odt
	pandoc_logfile = os.path.join(generated_intermediate_files_dir,  "pandoc_log_toodt.txt")
	with open(pandoc_logfile, "w", buffering=1) as stdoutfile, redirect_stdout(stdoutfile):
		result, error = run_local_cmd("pandoc result.html -o result.odt",
			cwd = output_folder, print_cmd = True)
	
		success = pandocErrorRecogniser(result, error)
	assert success, "Pandoc failure, see log"

	# remove everything except for desired filetypes
	# remove_generated_files(keep_filetypes=[".html", ".pdf", ".latex", ".csv", ".svg", ".bmp"])
	remove_generated_files(
		delete = glob(f"{output_folder}/*") + [f"{doc_dir}/output"],
		except_for = glob(f"{output_folder}/generated_intermediate_files") + \
			glob(f"{output_folder}/generated_output_files") + \
			[f"{output_folder}/result{suffix}" for suffix in ('.html','.odt')]
	)

	print("success")


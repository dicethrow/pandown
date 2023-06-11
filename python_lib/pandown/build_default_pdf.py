# default pdf build
from .doc_resources import get_path_to_common_content

import argparse, os, subprocess, textwrap, pathlib, shutil
from glob import glob
import subprocess
import platform

from contextlib import redirect_stdout, redirect_stderr

from .common import run_local_cmd, clear_terminal, remove_generated_files, add_yaml_entries_to_file, get_yaml_entries_from_file
from .errorRecogniser import pandocErrorRecogniser, latexErrorRecogniser

		
def build_default_pdf():
	# in the container, copy over the proj_location/content, and template
	# then, run the container:proj_location/build.py
	# which goes through the document and does its thing

	clear_terminal()

	# remove intermediate files from previous runs
	# remove_generated_files() # note - commented out, so the result.pdf is never removed; which makes vscode auto-reload the latest version of the file

	# display the current directory and its contents
	if platform.system() == "Windows":
		run_local_cmd("cd", print_result = True)
		run_local_cmd("tree .", print_result=True)
		doc_dir = f"{run_local_cmd('cd')[0][0]}\\doc"
		script_runner = "-F " + os.path.expanduser("~/.local/bin/panflute")
	else:
		run_local_cmd("pwd", print_result = True)
		run_local_cmd("tree -a .", print_result=True)
		doc_dir = f"{run_local_cmd('pwd')[0][0]}/doc"
		script_runner = "-F " + os.path.expanduser("~\AppData\Local\Programs\Python\Python311\Scripts\panflute.py")

	top_source_file = f"{doc_dir}/content/main.md".replace("/", os.sep)
	output_folder = f"{doc_dir}/output_pdf".replace("/", os.sep)

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

	# load the specified pandown template file
	yaml_entries = get_yaml_entries_from_file(top_source_file)
	if 'pandown-template-pdf' not in yaml_entries:
		yaml_entries['pandown-template-pdf'] = "test2.latex"
	
	# check that the given template exists within the local project. 
	template = yaml_entries['pandown-template-pdf']
	if os.path.exists(f"{doc_dir}/templates/{template}").replace("/", os.sep):
		template_file = f"--template {doc_dir}/templates/{template}".replace("/", os.sep)
	else:
		template_file = f"--template {get_path_to_common_content('pdf_templates')}/{template}".replace("/", os.sep)

	panflute_filters_path = f"{get_path_to_common_content('common_filters')}"
	extras = "--listings" # extras = ""

	add_yaml_entries_to_file(
		src_filename = top_source_file, 
		dst_filename = top_source_file_ammended,
		new_header_lines = [
			f"panflute-path: '{panflute_filters_path}'",
			f"starting_dir: '{os.path.dirname(top_source_file)}'",
			f"output_dir: '{output_folder}'",
		] + [f"{d}_dir: '{pathlib.Path(os.path.join(output_folder, d))}'" for d in desired_dirs]
	)

	### from the .md use pandoc to make .tex
	latex_intermediate_file = os.path.join(generated_intermediate_files_dir, "result.latex")
	pandoc_cmd = f"pandoc {script_runner} {top_source_file_ammended} {template_file} -s -o {latex_intermediate_file} {extras}"
	
	pandoc_logfile = os.path.join(generated_intermediate_files_dir,  "pandoc_log.txt")
	with open(pandoc_logfile, "w", buffering=1) as stdoutfile, redirect_stdout(stdoutfile):
		result, error = run_local_cmd(pandoc_cmd, print_cmd = True, print_result = True, print_error=True, timeout = 15)

	success = pandocErrorRecogniser(result, error)
	assert success, "Pandoc failure, see log"

	### from .tex make .pdf
	# lualatex needs to be caled twice, otherwise the toc doesn't generate properly. if references, call biber between
	latex_cmd = f'pdflatex --shell-escape -halt-on-error --output-directory doc/output_pdf doc/output_pdf/generated_intermediate_files/result.latex'  # options go before filename https://tex.stackexchange.com/questions/268997/pdflatex-seems-to-ignore-output-directory
	latex_logfile = os.path.join(generated_intermediate_files_dir,  "latex_log.txt")
	with open(latex_logfile, "w", buffering=1) as stdoutfile, redirect_stdout(stdoutfile):
		for repeats in range(2):
			result, error = run_local_cmd(latex_cmd, print_cmd = True, print_result = True, print_error=True, timeout = 15)

	success = latexErrorRecogniser(result, error)
	assert success, "Latex failure, see log"
	
	remove_generated_files(
		delete = glob(f"{output_folder}/*") + [f"{doc_dir}/output"],
		except_for = glob(f"{output_folder}/generated_intermediate_files") + \
			glob(f"{output_folder}/generated_output_files") + \
			[f"{output_folder}/result{suffix}" for suffix in ('.pdf',)]
	)

	print("success")


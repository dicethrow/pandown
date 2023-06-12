# default pdf build
from .doc_resources import get_path_to_common_content

import argparse, os, subprocess, textwrap, pathlib, shutil
from glob import glob
import subprocess
import platform

from contextlib import redirect_stdout, redirect_stderr

from .common import run_local_cmd, clear_terminal, remove_generated_files, add_yaml_entries_to_file, get_yaml_entries_from_file
from .errorRecogniser import pandocErrorRecogniser, latexErrorRecogniser

import logging
from .my_logging import loggerClass
logging.setLoggerClass(loggerClass)
log = logging.getLogger(__name__)
		
def build_default_pdf():
	log.info("Starting build_default_pdf()")
	# clear_terminal()

	# display the current directory and its contents
	cwd = pathlib.Path().absolute()
	doc_dir = cwd / "doc"
	top_source_file = doc_dir / "content" / "main.md"
	output_folder = doc_dir / "output_pdf"

	# clean residue from last build process
	remove_generated_files(delete = [output_folder, doc_dir / "output"])
 	# note that latex's minted code generates `output`, although we dont use it at the moment - messy

	# prepare files and directories for use with pandoc
	generated_intermediate_files_dir = output_folder / "generated_intermediate_files"
	top_source_file_ammended = generated_intermediate_files_dir / "main.md"
	
	desired_dirs = ["generated_intermediate_files", "generated_output_files"]
	for desired_dir in desired_dirs:
		target_path = output_folder / desired_dir
		target_path.mkdir(parents=True, exist_ok=True)

	# load the specified pandown template file
	yaml_entries = get_yaml_entries_from_file(top_source_file)
	if 'pandown-template-pdf' not in yaml_entries:
		yaml_entries['pandown-template-pdf'] = "test2.latex"
	
	# check that the given template exists within the local project. 
	template = yaml_entries['pandown-template-pdf']
	custom_template_folder = doc_dir / "templates"
	if (custom_template_folder / template).exists():
		template_folder = custom_template_folder
	else:
		template_folder = get_path_to_common_content() / 'pdf_templates'
	template_file = f"--template {template_folder / template}"

	panflute_filters_path = get_path_to_common_content() / 'common_filters'
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
	script_runner = "-F panflute"
	latex_intermediate_file = generated_intermediate_files_dir / "result.latex"

	pandoc_cmd = f"pandoc "
	pandoc_cmd += f"{script_runner} "
	pandoc_cmd += f"{top_source_file_ammended} "
	pandoc_cmd += f"{template_file} "
	pandoc_cmd += f"--standalone --output {latex_intermediate_file} "
	pandoc_cmd += f"{extras}"
	
	pandoc_logfile = generated_intermediate_files_dir / "pandoc_log.txt"

	# logging disabled for this line as otherwise pandoc pollutes stdout
	result, error = run_local_cmd(pandoc_cmd, print_cmd = True, disable_logging = False)
			
	success = pandocErrorRecogniser(result, error)
	if not success:
		for line in error:
			log.critical(line)
		assert False, "Pandoc failure, see log; "
	### from .tex make .pdf
	# lualatex needs to be caled twice, otherwise the toc doesn't generate properly. if references, call biber between
	pdf_output_dir = doc_dir / "output_pdf"
	rel_output_dir = pdf_output_dir.relative_to(doc_dir.parent)
	rel_src_file = latex_intermediate_file.relative_to(doc_dir.parent)

	latex_cmd = f'pdflatex --shell-escape -halt-on-error --output-directory {rel_output_dir} {rel_src_file}'  # options go before filename https://tex.stackexchange.com/questions/268997/pdflatex-seems-to-ignore-output-directory
	latex_logfile = generated_intermediate_files_dir / "latex_log.txt"
	# with open(latex_logfile, "w", buffering=1) as stdoutfile, redirect_stdout(stdoutfile):
	for repeats in range(2): # needs to run twice; once to generate the toc, second to use the toc
		result, error = run_local_cmd(latex_cmd, print_cmd = True)

	success = latexErrorRecogniser(result, error)
	assert success, "Latex failure, see log"
	
	remove_generated_files(
		delete = list(output_folder.glob("*")) + [doc_dir / 'output'],
		except_for= list(output_folder.glob('generated_*_files')) + \
			[output_folder / f'result{suffix}' for suffix in ('.pdf',)]
	)

	print("success") # for stdout
	# print("")
	# log.inf



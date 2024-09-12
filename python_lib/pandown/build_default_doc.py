# default pdf build
from .doc_resources import get_path_to_common_content

import sys
import json
import hashlib
from contextlib import contextmanager
import argparse, os, subprocess, textwrap, pathlib, shutil
# from glob import glob
import subprocess
import platform

from contextlib import redirect_stdout, redirect_stderr

from .common import get_ordered_list_of_markdown_files_recursively_from, run_local_cmd, clear_terminal, remove_generated_files, write_yaml_entries_to_file, get_yaml_entries_from_file
from .errorRecogniser import pandocErrorRecogniser, latexErrorRecogniser

import logging
from .my_logging import loggerClass
logging.setLoggerClass(loggerClass)
log = logging.getLogger(__name__)

def build_default_doc(target):
	assert target in ["pdf", "html"]

	log.info(f"Starting build_default_doc({target})")

	# display the current directory and its contents
	cwd = pathlib.Path().absolute()
	doc_dir = cwd / "doc"
	src_dir = doc_dir / "content"
	top_source_file = get_ordered_list_of_markdown_files_recursively_from(src_dir)[0][0]
	options_file = doc_dir / "options.yaml"
	output_folder = doc_dir / f"output_{target}"

	# clean residue from last build process
	remove_generated_files(delete = [output_folder, doc_dir / "output"])
 	# note that latex's minted code generates `output`, although we dont use it at the moment - messy

	# prepare files and directories for use with pandoc
	generated_intermediate_files_dir = output_folder / "generated_intermediate_files"
	options_file_ammended = generated_intermediate_files_dir / "options.yaml"
	desired_dirs = ["generated_intermediate_files", "generated_output_files"]
	for desired_dir in desired_dirs:
		target_path = output_folder / desired_dir
		target_path.mkdir(parents=True, exist_ok=True)

	yaml_entries = get_yaml_entries_from_file(options_file)

	# load the specified pandown template file
	# the template will either be in the local project - if not, a default pandown template.
	# resolve one then save to yaml entries.
	default_templates = { 
		"html" : "default/standalone.html",
		"pdf" : "test2.latex"
	}
	template_filename = yaml_entries.get(f"pandown-template-{target}", default_templates[target])
	if (doc_dir / "templates" / template_filename).exists():
		full_path_to_template = doc_dir / "templates" / template_filename
	else: # then it's referring to a default pandown template
		full_path_to_template = get_path_to_common_content() / f'{target}_templates' / template_filename
	assert full_path_to_template.exists(), f"Unable to find template: {full_path_to_template}"
	# yaml_entries["template"] = str(full_path_to_template) # this line doesn't work for some reason

	# Note: The source file given to pandoc_cmd, before assembling all the separate source
	# documents together, is now just the yaml block. This is so all the source can be added
	# afterward in the same way, without having to treat the content from the first file
	# differently. This is a bit roundabout, but makes sense if we always assemble files
	# as part of document generation, which is what the latest approach is to do.
	# The filter '_assemble_parts' is named with an underscore to indicate that it is
	# internal to this generation, and not optional, and so it is added above.

	# Now add two compulsory filters that are done first:
	# 1. _ignore_comments, to remove things not desired to be in the final doc
	# 2. _assemble_parts, to put together all the source files properly and to correct links/files
	filters = yaml_entries.get("panflute-filters", [])
	filters.insert(0, "_assemble_parts")
	filters.insert(0, "_ignore_comments")
	yaml_entries["panflute-filters"] = filters

	panflute_filters_path = get_path_to_common_content() / 'common_filters'
	yaml_entries["panflute-path"] = str(panflute_filters_path)

	yaml_entries["starting_dir"] = str(os.path.dirname(src_dir))
	yaml_entries["output_dir"] = str(output_folder)
	for d in desired_dirs:
		yaml_entries[f"{d}_dir"] = str(pathlib.Path(os.path.join(output_folder, d)))

	write_yaml_entries_to_file(options_file_ammended, yaml_entries)

	script_runner = "-F panflute"
	extras = "--listings" # extras = ""

	pandoc_cmd = "pandoc "
	pandoc_cmd += f"{script_runner} "
	pandoc_cmd += f"--from=markdown {options_file_ammended} " #
	pandoc_cmd += f"--template={full_path_to_template} "

	if target == "pdf":
		### from the .md use pandoc to make .tex
		### then make .pdf from .tex with a second program, pdftex?
		### from the .md use pandoc to make .tex
		latex_intermediate_file = generated_intermediate_files_dir / "result.latex"
		pandoc_cmd += f"--standalone --output {latex_intermediate_file} "

	elif target == "html":
		### go straight from .md to .html
		pandoc_cmd += f"--standalone --table-of-contents --output {output_folder / 'result.html'} "

	pandoc_cmd += f"{extras} "

	result, error = run_local_cmd(pandoc_cmd, print_cmd = True, disable_logging = False)

	success = pandocErrorRecogniser(result, error)

	if target == "pdf":
		# do extra things for pdf:
		# from .tex make .pdf
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
			[output_folder / f'result{suffix}' for suffix in (f'.{target}',)]
	)

	if target == "pdf":
		# now rename it if desired
		if "result-name" in yaml_entries:
			current_full_path = pdf_output_dir / "result.pdf"
			new_full_path = pdf_output_dir / (yaml_entries["result-name"] + ".pdf")
			# new_path = path.parent / f"{path.name}.pdf"
			shutil.move(current_full_path, new_full_path)

	print("success") # for stdout
	


# from https://stackoverflow.com/questions/299446/how-do-i-change-directory-back-to-my-original-working-directory-with-python
@contextmanager
def my_cwd(path):
	oldpwd = os.getcwd()
	os.chdir(path)
	try:
		yield
	finally:
		os.chdir(oldpwd)

# adapted from https://stackoverflow.com/questions/2267362/how-to-convert-an-integer-to-a-string-in-any-base/74324587#74324587
def to_base36(number):
	base_string = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	base = len(base_string) # 36
	result = ""
	while number:
		result += base_string[number % base]
		number //= base
	return result[::-1] or "0"

# from https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
def get_file_hash(filename):
	# import sys
	# import hashlib

	# BUF_SIZE is totally arbitrary, change for your app!
	BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

	# md5 = hashlib.md5()
	sha1 = hashlib.sha1()

	with open(filename, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			# md5.update(data)
			sha1.update(data)

	# print("MD5: {0}".format(md5.hexdigest()))
	# print("SHA1: {0}".format(sha1.hexdigest())
	return sha1.hexdigest()

def test_rmii_sync():
	log.info("In test_rmii_sync")
	# display the current directory and its contents
	cwd = pathlib.Path().absolute()
	doc_dir = cwd / "doc"
	top_source_file = doc_dir / "content" / "main.md"
	output_folder = doc_dir / "output_pdf"
	rmii_output_dir = doc_dir / "output_pdf_from_rmii"

	version_id_records_file = rmii_output_dir / "version_ID_records.json"
	if version_id_records_file.exists():
		with open(version_id_records_file, "r") as f:
			version_ids = json.load(f)
		last_version_id_int = max([int(ver_str, 36) for ver_str in version_ids.keys()]) # largest is the most recent version counter
		version_id = to_base36(last_version_id_int + 1)	
	else:
		version_id = "A"
		version_ids = {}

	yaml_entries = get_yaml_entries_from_file(top_source_file)
	assert "result-name" in yaml_entries

	output_file = output_folder / (yaml_entries["result-name"] + ".pdf")

	# find in rmapi tree
	result, error = run_local_cmd(f"rmapi find / {yaml_entries['result-name']}*", print_cmd = True, disable_logging = False)
	if result != []:
		log.info("Found:")
		for line in result:
			log.info(line)
		assert len(result) == 1, "Multiple find hits found! not handled"
		found_location = result[0].split(" ")[1]
		log.info(found_location)

		# # now dowload it
		with my_cwd(doc_dir / "output_pdf_from_rmii"):
			cmd = f"rmapi get {found_location}"
			result, error = run_local_cmd(cmd, print_cmd = True, disable_logging = False)
			for line in result:
				log.info(line)

			# extract the resulting .zip
			found_versioned_zip = list(rmii_output_dir.glob(f"{yaml_entries['result-name']}*.zip"))[0] # should be only one
			result, error = run_local_cmd(f"unar {found_versioned_zip}", print_cmd = True, disable_logging = False)
			for line in result:
				log.info(line)
				assert "failed" not in line

			# turn it into a pdf (as the annotation files need to be put together manually)
			unzipped_dir = rmii_output_dir / found_versioned_zip.stem
			result, error = run_local_cmd(f"/home/ubuntu/Documents/py311env/bin/python3.11 -m remarks {unzipped_dir} {unzipped_dir}", print_cmd = True, disable_logging = False)
			for line in result + error:
				log.info(line)


			# move the result .pdf 
			current_location = rmii_output_dir / found_versioned_zip.stem / (found_versioned_zip.stem + " _remarks.pdf")
			target_location = rmii_output_dir / (found_versioned_zip.stem + ".pdf")
			shutil.move(current_location, target_location)
			# result, error = run_local_cmd(f"shutil", print_cmd = True, disable_logging = False)
			# for line in result + error:
				# log.info(line)

			# remove the now-downloaded file from rmcloud
			cmd = f"rmapi rm {found_location}"
			result, error = run_local_cmd(cmd, print_cmd = True, disable_logging = False)
			for line in result:
				log.info(line)

			# only keep a local copy of this version if it is annotated, which we can determine by checking
			# if the unzipped folder contains a .rm file
			has_annotations = any(unzipped_dir.rglob("*.rm"))
			if has_annotations:
				log.info("has annotations")
			else:
				log.info("no annotations, todo: delete, as it doesn't contain anything we don't already have")
				os.remove(target_location)

			# remove the zip and the extracted files
			shutil.rmtree(unzipped_dir)
			os.remove(rmii_output_dir / (found_versioned_zip.stem + ".zip"))
		
	else:
		log.info("Not found")


	# add version ID to the filename
	
		

	log.info(f"Now using version: {version_id}")

	version_ids[version_id] = get_file_hash(output_file) # note we don't use hash anymore, as it doesn't work, and the find-the-.rm-file works
	with open(version_id_records_file, "w") as f:
		json.dump(version_ids, f)

	versioned_filename = output_file.with_name(output_file.name.replace(".pdf", f"_{version_id}.pdf"))
	shutil.move(output_file, versioned_filename)

	# copy to rmii cloud, to the root location
	# add version count to filename?
	result, error = run_local_cmd(f"rmapi put {versioned_filename} / ", print_cmd = True, disable_logging = False)
	for line in result:
		log.info(line)
		

	log.info("End of test_rmii_sync")


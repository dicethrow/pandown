import argparse, os, textwrap
from glob import glob
import shutil
import panflute as pf
import shlex
from threading import Timer
import copy
import platform
import sys
import logging
import io

import subprocess
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore, Style, ansi

import contextlib

from .my_logging import loggerClass
logging.setLoggerClass(loggerClass)
log = logging.getLogger(__name__)

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
	# e.g. run_local_cmd(pandoc_cmd, print_cmd = True, disable_logging = True)
	# print(cmd, flush=True)

	disable_logging = kwargs.pop("disable_logging", False)
	print_cmd = kwargs.pop("print_cmd", False)
	logfile = kwargs.pop("logfile", False)

	def do_print_cmd(cmd):
		log.info("About to execute: $ " + cmd)

	if print_cmd:
		do_print_cmd(cmd)

	original_cmd = cmd
	if (platform.system() == "Windows"):# and cmd not in ["pwd"]:
		# the repr() here turns slashes into doubleslashes, needed on windows
		cmds = ["cmd", "/c"] + [c for c in shlex.split(repr(cmd))] 
	else:
		cmds = shlex.split(cmd)
		
	if platform.system() == "Windows":
		kwargs["universal_newlines"] = True
		kwargs["encoding"] = "cp850"
	else:
		kwargs["encoding"] = "utf-8"

	
	

	def run_cmds(cmds, **kwargs):
		# returns stdout, stderr
		# note: stdout is only things that are print()ed, stderr is for logs.

		def show_line(line, default):
			# This is so that if a program is called that raises a WARNING, for example,
			# then the log level here is to also treat it as a WARNING.
			
			func = None
			for test in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
				if test in line:
					# technique from https://stackoverflow.com/questions/34954373/disable-format-for-some-messages
					# to minimise double-up of logging
					# log.info("Debug found in")
					func = lambda s : log.debug("\t subprocess:" + s, extra={'simple': True})
					break

			if func == None:
				func = default
			# , extra={'simple': True}
			# if "CRITICAL" in line: 
			# 	func = lambda s : log.critical("from subprocess: \n\t" + s)
			# elif "ERROR" in line:
			# 	func = lambda s : log.error("from subprocess: \n\t" + s)
			# elif "WARNING" in line:
			# 	func = lambda s : log.warning("from subprocess: \n\t" + s)
			# elif "INFO" in line:
			# 	func = lambda s : log.info("from subprocess: \n\t" + s)
			# elif "DEBUG" in line:
			# 	func = lambda s : log.debug("from subprocess: \n\t" + s)
				
			
			# if we're dealing with an original line, not from another program,
			# else:
				# func = default

			return func(line)
			# return print(line)

		stdout_print_func = kwargs.pop("stdout_print_func", lambda s : show_line(s, log.debug)) #log.debug)
		stderr_print_func = kwargs.pop("stderr_print_func", lambda s : show_line(s, log.debug))

		def monitor_pipe(p, stdfile, print_func):
			result = []
			while p.poll() is None:
				line = stdfile.readline()
				if line == "":
					continue
				line = line.strip()
				print_func(line)
				result.append(line)
			# stdfile.flush()
			return result

		with subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs) as p:

			with ThreadPoolExecutor(2) as pool:
				# technique from https://stackoverflow.com/questions/18421757/live-output-from-subprocess-command

				r1 = pool.submit(monitor_pipe, p, p.stdout, stdout_print_func)
				r2 = pool.submit(monitor_pipe, p, p.stderr, stderr_print_func)

				stdout = r1.result()
				stderr = r2.result()

		return stdout, stderr

	# log.debug("debug message")
	# log.info("info message")
	# log.warning("warning message")
	# log.error("error message")
	# log.critical("critical message")


	if disable_logging:
		log.debug("Disabling logging, about to run run_cmds()")
		kwargs["stdout_print_func"] = lambda s : ...
		kwargs["stderr_print_func"] = lambda s : ...

	stdout, stderr = run_cmds(cmds, **kwargs)

	if disable_logging:
		log.debug("Completed run_cmds() with logging disabled")

	return stdout, stderr

def clear_terminal():
	# clean the terminal before we start.
	if platform.system() == "Windows":
		subprocess.call(["cmd", "/c", "cls"])
	else:
		subprocess.call("clear")

	# subprocess.call(["cmd", "/c", "echo hello"])   # from https://stackoverflow.com/questions/3022013/windows-cant-find-the-file-on-subprocess-call
	

def remove_generated_files(delete, except_for = []):
	# recommend to use glob for this function
	# debug = False
	# if debug: print(delete, except_for)

	# log.debug(delete, except_for)
	for filename in delete:
		if filename in except_for:
			# log.debug(f"Not removing {filename}")
			continue
		# log.debug(f"Removing {filename}")
		
		if os.path.isdir(filename): 
			shutil.rmtree(filename)
		elif os.path.isfile(filename):
			os.remove(filename)
		else:
			log.warning(f"file not found, hence not deleted: \t{filename}")
		

def get_yaml_entries_from_file(src_filename):
	with open(src_filename, "r") as f:
		lines = f.readlines()
	yaml_entries = {}
	
	state = "Not yet started"
	for line in lines:

		if state == "Not yet started":
			if line.strip() == "---":
				state = "In yaml block"
				continue

		if state == "In yaml block":
			if line.strip() == "...": # can this also be --- ?
				state = "Finished yaml block"
				continue
			key, value = line.split(": ")	
			value = value.strip() # as it often has a trailing \n
			assert key != []
			assert value != []
			yaml_entries[key] = value

		if state == "Finished yaml block":
			break
		
	return copy.deepcopy(yaml_entries) # is deepcopy necessary?



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
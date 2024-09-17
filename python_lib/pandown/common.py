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
import pathlib
import yaml, json
import natsort

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
			log.debug(f"Not removing {filename}")
			continue
		log.debug(f"Removing {filename}")
		
		if os.path.isdir(filename): 
			shutil.rmtree(filename)
		elif os.path.isfile(filename):
			os.remove(filename)
		else:
			log.warning(f"file not found, hence not deleted: \t{filename}")
		
def get_ordered_list_of_markdown_files_recursively_from(start_dir, exclude_prefix="output_"):
	# from https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
	# array of [path, depth] entries, sorted in alphabetical recursive order
	file_list = []
	start_depth = len(pathlib.Path(start_dir).parents)
	for (dirpath, dirnames, filenames) in os.walk(start_dir, topdown=True):
		# pf.debug(f"{dirpath}, {dirnames}, {filenames}")

		if str(start_dir) + os.sep + exclude_prefix in dirpath: # exclude these
			continue 

		# pf.debug(f"{dirpath}, {dirnames}, {filenames}")

		rel_file_depth = len(pathlib.Path(dirpath).parents) - start_depth - 1
		for f in filenames:
			if f.endswith(".md"):
				file_list.append([pathlib.Path(dirpath, f), rel_file_depth])
		# break
		
		# note: row[0] are of type PosixPath
		# using natsort.os_sorted so the sorted paths are close to the
		# user's operating system file browser, see 
		# https://natsort.readthedocs.io/en/stable/api.html#natsort.os_sorted
		file_list = natsort.os_sorted(file_list, key = lambda row : str(row[0]))

	return file_list # 


def get_yaml_entries_from_file(src_filename):
	with open(src_filename, "r") as f:
		data = yaml.safe_load(f)

	# pf.debug(json.dumps(data, indent=2))
	return data

def write_yaml_entries_to_file(dst_filename, content):
	with open(dst_filename, "w") as f:
		yaml.safe_dump(content, f, explicit_start=True, explicit_end=True)
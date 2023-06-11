import argparse, os, textwrap
from glob import glob
import subprocess
import shutil
import panflute as pf
import shlex
from threading import Timer
import copy
import platform
import sys
import time

import subprocess as sp
from concurrent.futures import ThreadPoolExecutor

from colorama import Fore, Style


def do_proc(s, **kwargs):

	cmds = shlex.split(s)	

	with sp.Popen(cmds, stdout=sp.PIPE, stderr=sp.PIPE, encoding="utf-8", shell=True) as p:

		with ThreadPoolExecutor(2) as pool:
			# technique from https://stackoverflow.com/questions/18421757/live-output-from-subprocess-command
			def log_popen_pipe(p, stdfile, print_func):
				result = []
				while p.poll() is None:
					line = stdfile.readline()
					if line == "":
						continue
					line = line.strip()
					print_func(line)
					result.append(line)
				return result

			r1 = pool.submit(log_popen_pipe, p, p.stdout, print_func = lambda s : print(f"{Fore.GREEN}{s}{Fore.RESET}"))
			r2 = pool.submit(log_popen_pipe, p, p.stderr, print_func = lambda s : print(f"{Fore.RED}{s}{Fore.RESET}"))
			stdout = r1.result()
			stderr = r2.result()

	return stdout, stderr


if __name__ == "__main__":
	print("Starting...")

	# do_proc("wget https://www.analog.com/media/en/training-seminars/design-handbooks/basic-linear-design/chapter1.pdf")

	# do_proc("echo foo >> /dev/stdout")
	# do_proc("echo goo >> /dev/stderr")
	print(do_proc("./xxxx.sh"))

	print("Done")
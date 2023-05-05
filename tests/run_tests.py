import unittest
import os
from pandown import run_local_cmd, remove_generated_files
from contextlib import contextmanager
import glob

def run_this_test(test_path):
	# this is used for running a subset of tests.
	# if want to run the test, return true
	# if want to skip the test, return false.

	# return True

	if "forbidden" in test_path:
	# if "basic_nested_parts__" in test_path:
		return True
	else:
		return False


# from https://stackoverflow.com/questions/299446/how-do-i-change-directory-back-to-my-original-working-directory-with-python
@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)

class test_runner(unittest.TestCase):
	""" 
	Note that the pdf/html stuff will delete each other, annoyingly. Useful behaviour but not during testing.
	"""
	# def setUp(self):
	# 	# remove outputs from the test folders
	# 	for test_dir in glob.glob("tests/test__*"):
	# 		with cwd(test_dir):
	# 			remove_generated_files(keep_filetypes=[])


	def test_pdf(self):
		for test_dir in glob.glob("tests/test__*"):
			if run_this_test(test_dir):
				with cwd(test_dir):
					print(f"Running test {test_dir}:")
					result, error = run_local_cmd("python3 doc/build.py pdf", 
						print_cmd = True, print_result = True, print_error = True)

					newline = "\n"
					self.assertTrue(result[-1] == "success", 
						f"result: {newline.join(result)},\n error: {newline.join(error)}")

	def test_html(self):
		for test_dir in glob.glob("tests/test__*"):
			if run_this_test(test_dir):
				with cwd(test_dir):
					print(f"Running test {test_dir}:")
					result, error = run_local_cmd("python3 doc/build.py html", 
						print_cmd = True, print_result = True, print_error = True)

					newline = "\n"
					self.assertTrue(result[-1] == "success", 
						f"result: {newline.join(result)},\n error: {newline.join(error)}")
	
	# def test_odt(self):
	# 	for test_dir in glob.glob("tests/test__*"):
	# 		with cwd(test_dir):
	# 			print(f"Running test {test_dir}:")
	# 			result, error = run_local_cmd("python3 doc/build.py odt", 
	# 				print_cmd = True, print_result = True, print_error = True)

	# 			newline = "\n"
	# 			self.assertTrue(result[-1] == "success", 
	# 				f"result: {newline.join(result)},\n error: {newline.join(error)}")

if __name__ == "__main__":
	unittest.main(verbosity=2)
	
import unittest
import os
from pandown import run_local_cmd
from contextlib import contextmanager

# from https://stackoverflow.com/questions/299446/how-do-i-change-directory-back-to-my-original-working-directory-with-python
@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)

class test_html(unittest.TestCase):
	def test_generate(self):
		with cwd("tests/test_html"):
			result, error = run_local_cmd("python3 doc/build.py generate")
			self.assertEqual(error, []) # is this adequate?

class test_pdf(unittest.TestCase):
	def test_generate(self):
		with cwd("tests/test_pdf"):
			result, error = run_local_cmd(f"python3 doc/build.py generate")
			
			self.assertEqual(error, []) # is this adequate?
			
			resultFound = False
			for line in result:
				if "Output written on doc/output/result.pdf" in line:
					resultFound = True
			self.assertTrue(resultFound)

if __name__ == "__main__":
	unittest.main(verbosity=2)
	
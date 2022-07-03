import unittest
import os
from pandown import run_local_cmd, remove_generated_files
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

test_docs = [
	"test__basic",
	"test__basic_nested_parts",
	"test__basic_nested_parts__level_neg_1",
	"test__level_neg_1"
	
]

class test_runner(unittest.TestCase):
	""" 
	Note that the pdf/html stuff will delete each other, annoyingly. Useful behaviour but not during testing.
	"""
	def setUp(self):
		# remove outputs from the test folders
		for test in test_docs:
			with cwd(f"tests/{test}"):
				remove_generated_files(keep_filetypes=[])


	def test_pdf(self):
		for test in test_docs:
			with cwd(f"tests/{test}"):
				result, error = run_local_cmd("python3 doc/build.py pdf")

				self.assertEqual(error, [])
				resultFound = False
				for line in result:
					if "Output written on doc/output/result.pdf" in line:
						resultFound = True
				newline = "\n"
				self.assertTrue(resultFound, f"result: {newline.join(result)},\n error: {newline.join(error)}")



	def test_html(self):
		for test in test_docs:
			with cwd(f"tests/{test}"):
				result, error = run_local_cmd("python3 doc/build.py html")

				self.assertEqual(error, [])

				for line in result:
					self.assertFalse("Filter returned error status" in line)

if __name__ == "__main__":
	unittest.main(verbosity=2)
	
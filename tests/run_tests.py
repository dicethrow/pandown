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

test_docs = [
	"test__basic",
	"test__level_neg_1"
]

class test_runner(unittest.TestCase):
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
	
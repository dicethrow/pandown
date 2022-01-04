import argparse, subprocess

parser = argparse.ArgumentParser()
parser.add_argument("src_file", type=str, help="first source file")
parser.add_argument("filters_file", type=str, help="first filter file")
parser.add_argument("output_folder", type=str, help="folder for output")


args = parser.parse_args()

print("In demo report")

# this starts it, and further calls to pandoc will be made as needed
# should this first one have a --standalone?
# subprocess.call(f"echo hi_a".split())
# subprocess.call(f"echo {args.src_file}".split())
# subprocess.call(f"cat {args.src_file} | tail".split(" "))


# implelementing pipes from https://stackoverflow.com/questions/13332268/how-to-use-subprocess-command-with-pipes
# trying to implement something like `cat file | pandoc --filter myfilter.py`
# ps = subprocess.Popen(f"cat {args.src_file}".split(), stdout=subprocess.PIPE)
# output = subprocess.check_output(f"pandoc --filter {args.filters_file}".split(), stdin=ps.stdout)
subprocess.call(f"pandoc --filter {args.filters_file} {args.src_file} -o {args.output_folder}/result.md".split())#, stdin=ps.stdout)
# ps.wait()

# print("Output is:")
# print(output)


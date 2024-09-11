#!/usr/bin/env python3
import pandown, argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("task", type=str, help="action to do")
	# parser.add_argument("proj_location", type=str, help="project dir to build")
	args = parser.parse_args()

	assert args.task in ["pdf", "html", "odt"], "invalid task given"

	if args.task == "html":
		pandown.build_default_html()
	
	elif args.task == "pdf":
		pandown.build_default_pdf()

	elif args.task == "odt":
		pandown.build_default_odt()
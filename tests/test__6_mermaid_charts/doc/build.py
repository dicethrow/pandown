#!/usr/bin/env python3
import pandown, argparse

import logging
import sys

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# # logging.setLoggerClass(pandown.ColorLogger)

# logging.setLoggerClass(pandown.ColorLogger)
# log = logging.getLogger(__name__)

# pandown.ColorLogger.logfile = "testfile_logb.log"
logging.setLoggerClass(pandown.loggerClass)
log = logging.getLogger(__name__)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("task", type=str, help="action to do")
	# parser.add_argument("proj_location", type=str, help="project dir to build")
	args = parser.parse_args()

	assert args.task in ["pdf", "html"], "invalid task given"

	log.info("Starting build.py")

	pandown.build_default_doc(args.task)

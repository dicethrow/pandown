
import logging
from .my_logging import loggerClass

logging.setLoggerClass(loggerClass)
log = logging.getLogger(__name__)

# This prints out useful info to help interpret errors
def pandocErrorRecogniser(resultLines, errorLines):
	# # unfortunately the whole filter's code is in the 'error' list. let's remove it
	# # technique using [:] allows edit in place, avoiding unnecessary copies? from https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
	# def keepLine(line):
	# 	exceptionDetected = False
	# 	status = False
	# 	if "Traceback (most recent call last):" in line:
	# 		# include this line and all following lines
	# 		exceptionDetected = True
	# 		status = True
	# 	elif exceptionDetected:
	# 		status = True
	# 	elif "Failed to run filter: " in line:
	# 		# just include this line
	# 		status = True
	# 	return status
	# error[:] = [line for line in error if keepLine(line)]

	# for line in errorLines:

	# 	if ("dictionary update sequence element " in line and
	# 		" has length " in line and 
	# 		" is required" in line
	# 	):
	# 		print("You might have a redundant --- in a parts block somewhere, find and remove it")
	
	success = True
	for eline in errorLines:
		if "Exception" in eline:
			success = False

	recognisedError = False

	if not success:	
		for i, eline in enumerate(errorLines):
			if "[WARNING] Could not fetch resource" in eline:
				log.error("There is an issue with the URL, or the working directory, as pandoc cant follow the path")
				recognisedError = True
			
			if ("YAML parse exception at" in eline) and ( errorLines[i+1] == "mapping values are not allowed in this context"):
				log.error("You may have some --- strings in your text that is being misinterpreted as an invalid YAML block")
				recognisedError = True
			
	# now check resultLines for info
	# note! 12sep24, these don't work, I get this in the log but can't detect it like this - why?
	# [2024-09-12 11:56:29,905] DEBUG [pandown.common.show_line:105] /usr/bin/env: ‘node’: No such file or directory

	for i, rline in enumerate(resultLines):
		if "No such file or directory" in rline:
			log.error("Some file or executable cannot be found")
			recognisedError = True

		if "/usr/bin/env: ‘node’: No such file or directory" in rline:
			log.error("Node cannot be found. This is used to generate mermaid diagrams. If it worked before last login, it may be instaled but not on path.")
			recognisedError = True


	if not success:
		log.error("Undiagnosed pandoc issue. Displaying pandoc output:")
		newline = "\n"
		log.error(f"{newline.join(resultLines)},\n error: {newline.join(errorLines)}")
		assert False, "Pandoc failure, see log; "

	elif recognisedError:
		log.error("Recognised pandoc issue, see above")
		assert False, "Pandoc failure, see log; "

	else:
		log.info("No pandoc errors detected")


	# newline = "\n"
	# log.error(f"{newline.join(resultLines)},\n error: {newline.join(errorLines)}")

	
	return success

def latexErrorRecogniser(resultLines, errorLines):

	lines = resultLines + errorLines
	success = False
	for rline in lines:
		if "Output written on " in rline:
			success = True
	
	# how to check for case that no .latex file is produced?
	# otherwise it will hang (expecting stdin instead?)


	if success:
		log.info("No latex errors detected")
		
	if not success:
		recognisedError = False

		for rline in lines:
			if "! LaTeX Error: Environment lstlisting undefined." in rline:
				log.warning("Latex error regarding lstlisting / code stuff. Ensure minted_code filter is used, to bypass this for now")
				recognisedError = True
		...
		if not recognisedError:
			log.warning("Warning! Undiagnosed latex issue. Displaying latex output:")
			newline = "\n"
			log.warning(f"{newline.join(lines)}")
	
	return success
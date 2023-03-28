
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
	
	if success:
		print("No pandoc errors detected")

	if not success:
		recognisedError = False
		
		for eline in errorLines:
			if "[WARNING] Could not fetch resource" in eline:
				print("There is an issue with the URL, or the working directory, as pandoc cant follow the path")
				recognisedError = True

		if not recognisedError:
			print("Warning! Undiagnosed pandoc issue. Displaying pandoc output:")
			newline = "\n"
			print(f"{newline.join(resultLines)},\n error: {newline.join(errorLines)}")


	return success

def latexErrorRecogniser(resultLines, errorLines):

	lines = resultLines + errorLines
	success = False
	for rline in lines:
		if "Output written on doc/output_pdf/result.pdf" in rline:
			success = True
	
	# how to check for case that no .latex file is produced?
	# otherwise it will hang (expecting stdin instead?)


	if success:
		print("No latex errors detected")
		
	if not success:
		recognisedError = False

		for rline in lines:
			if "! LaTeX Error: Environment lstlisting undefined." in rline:
				print("Latex error regarding lstlisting / code stuff. Ensure minted_code filter is used, to bypass this for now")
				recognisedError = True
		...
		if not recognisedError:
			print("Warning! Undiagnosed latex issue. Displaying latex output:")
			newline = "\n"
			print(f"{newline.join(lines)}")
	
	return success
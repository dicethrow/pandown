

# This prints out useful info to help interpret errors
def errorRecogniser(errorLines):
	for line in errorLines:

		if ("dictionary update sequence element " in line and
			" has length " in line and 
			" is required" in line
		):
			print("You might have a redundant --- in a parts block somewhere, find and remove it")


def latexErrorRecogniser(resultLines, errorLines):
	success = False
	for rline in resultLines:
		if "Output written on doc/output_pdf/result.pdf" in rline:
			success = True
	
	if success:
		print("No latex errors detected")
		
	if not success:
		recognisedError = False
		...
		if not recognisedError:
			print("Warning! Undiagnosed latex issue. Displaying latex output:")
			newline = "\n"
			print(f"{newline.join(resultLines)},\n error: {newline.join(errorLines)}")
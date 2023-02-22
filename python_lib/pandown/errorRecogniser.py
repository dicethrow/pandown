

# This prints out useful info to help interpret errors
def errorRecogniser(errorLines):
	for line in errorLines:

		if ("dictionary update sequence element " in line and
			" has length " in line and 
			" is required" in line
		):
			print("You might have a redundant --- in a parts block somewhere, find and remove it")



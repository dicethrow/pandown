
---
title: Some title
subtitle: And a small subtitle
documentclass: paper
panflute-filters: [ignore_comments, assemble_parts, copy_linked_items, minted_code]
result-name: pandown_test__rmii_syncing
...

This document is for testing rmii syncing

# rmii plans

## use cases
- drag and drop
	 - drag a file to a desktop script / icon
	 	- this would be on the host computer
	 	- would presumably need to call lxdev to run stuff in lxd_doc-dev
	 	- and so pandown would need a command line interface to implement the copy over process
	- this coies it to RMII (to the root folder?) and makes a 'receipt' file on the desktop
	- the file is then annotated or read on the rmii when it next syncs to the rmii cloud
	- after the planned reading / annotating is done, the 'receipt' file is dragged to the script. This:
		1. copies back and overwrites the original PDF on the host pc with the one from the rmii in its original location
		2. the original file, and receipt file is placed into the recycle bin (so it is recoverable if desired)
		3. the file on the rmii is moved from the root directory to the trash bin (so it is also recoverable on the rmii if desired)
	- alternatively, the receipt file can just be deleted if this copy-back function is not desired

- pandown publish to rmii
	- generate pdf
	- find in rmii tree, if not found, use root dir as the destination location
		- this allows the file's location on the rmii to be determined and stored on the rmii
	- to handle case of non-uploaded changes (failed syncs), add concise version identifier to name. perhaps an underscore then A,B,...,Z,AA,AB,... ?
	- if old version in rmii and has annotations, move to host pc
		- and save in a folder in the doc project perhaps of annotated versions?
		- however only save it if there are annotations. perhaps a hash comparison could be made before export and after return, to identify changes?
- later, add publish to gdrive?


## steps

- set up rmapi on doc-dev - done
- test drag and drop onto desktop icon script - done


- rmapi find / mbp*
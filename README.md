# pandown

## how pandown works

- the pandown python lib is installed locally
- it is used to manage interactions with a container, which contains the pandoc program.
- 

## making documents with pandown


- starting at root main.md,
	1. go through until a 'parts' filter found, adding all lines to local_tmp
	2. if, before ending the file, a {first_path}/main.md is found, call recursively
	3. when ending the outermost file, return a string containing that file content
		and counted header levels


- how to call pandoc from within panflute?




- the level of the heading is the heading level within the file, plus its depth in the folder tree
- links, pictures etc should be made to work using conventional markdown preview, then a pandoc filter/s should be implemented to ensure it works
- custom features can be implemented using markdown comment blocks 

idea - document this project as an example project?

https://lee-phillips.org/panflute-gnuplot/

https://github.com/ickc/pantable
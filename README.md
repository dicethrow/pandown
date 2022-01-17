# pandown

Work in progress.

Goal: Make documents easily, from small to huge, where:
- the content is an easily organised file/folder tree of small markdown documents
- collaboration can use git workflows
- the template is a rarely touched but highly capable pandoc latex template
- the output can be any format that pandoc supports
- the markdown should be structured in a way that a vscode markdown previewer will still preview the content (and relatively reference images etc) correctly
- the messy libraries, dependencies, latex stuff etc is confined to a containerised virtual machine


# making documents with pandown

## what's the big idea?
Write each part as a separate markdown file.
Each section can refer to other sub-parts, located in folders within the same directory as the parent markdown file. There is a primitive that shows how to include these sub-parts, and commenting that out will prevent using them.

In this way, a large document can be generated from many smaller components.
- the level of the heading is the heading level within the file, plus its depth in the folder tree
- links, pictures etc should be made to work using conventional markdown preview, then a pandoc filter/s should be implemented to ensure it works
- custom features can be implemented using markdown comment blocks 

## how pandown is used

1. Edit the content, e.g. `demo_report/content`
2. run, for example, `demo_report/build.py` on your local machine. This will:
	1. send files to the container (mine is set to be accessable when I run `ssh lxd_doc-dev`)
	2. run pandoc in the container on the content,
	3. then copy back the result to, for example, `demo_report/output`.

## how pandown works
- the pandown python lib is installed locally
- it is used to manage interactions with a container, which contains the pandoc program.
	- I use a LXD container, but the interface is all ssh/scp so any container is compatible with that would work
- the panflute library is used to make markdown filters for pandoc.
	- The main filter as of early January 2022 is the recursive markdown 'preprocessor' that
		- sticks all the specified markdown files together
		- updates heading levels, so the result heading level is (the markdown file heading level) + (the nesting level in the source file tree)
		- update image links etc, so images can be stored in the same directory as the markdown file that refers to them, and still work with pandoc which requires absolute paths.
- note that code colouring in `test2.latex` template requires `sudo apt-get install python3-pygments` before using, as mentioned [here](https://tex.stackexchange.com/questions/146264/i-cant-get-minted-package-to-work-under-ubuntu-pygments-error/563919#563919)

## what's next to do
- For PDF/latex generation, shift the heading levels so the highest level markdown heading corresponds to latex 'part'.
- Polish up the PDF/latex template so it matches documents I like
- Make some other PDF/latex templates 
- Add templates, filters etc to generate html for simple web-based content/blogs
- Investigate replacing the listings code library with `minted` and `pygments` for better performance, [mentioned here](https://tex.stackexchange.com/questions/89276/insert-bash-code-with-coloration-into-my-latex-report)
- make the demo document be this readme
- Currently switching from `listings` to `minted` for code colouring, but not working yet

## bugs
- 17jan2022
	- images in the root markdown file only work if a `parts` yaml block is used and refers to other content
	- non-alphanumeric characters in the yaml title block can break latex as they don't yet have escaping applied
	- the key-value pairs in the yaml `parts` blocks are not optional but should be

## unsorted useful links
- https://lee-phillips.org/panflute-gnuplot/
- https://github.com/ickc/pantable
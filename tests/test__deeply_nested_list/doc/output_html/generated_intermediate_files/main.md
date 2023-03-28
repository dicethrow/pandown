
---
panflute-path: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/python_lib/pandown/doc_resources/raw_content/common_filters'
starting_dir: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/tests/test__deeply_nested_list/doc/content'
output_dir: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/tests/test__deeply_nested_list/doc/output_html'
generated_intermediate_files_dir: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/tests/test__deeply_nested_list/doc/output_html/generated_intermediate_files'
generated_output_files_dir: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/tests/test__deeply_nested_list/doc/output_html/generated_output_files'
title: Some title
subtitle: And a small subtitle
documentclass: paper
panflute-filters: [ignore_comments, assemble_parts,mermaid_charts, minted_code]
...

# This is part one

## heading one in /main.md


Here is an attempt to make a deeply nested list.

- one
- second one
	- two
	- second two
		- three
		- second three
			- four
			- second four
				- five
				- second five
					- six
					- second six
						- seven
						- second seven
					- at six again
				- at five again
			- at four again
		- at three again
	- at two again
- at one again

end of content
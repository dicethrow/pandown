
---
panflute-path: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/python_lib/pandown/doc_resources/raw_content/common_filters'
starting_dir: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/tests/test__basic_nested_parts/doc/content'
output_dir: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/tests/test__basic_nested_parts/doc/output_pdf'
generated_intermediate_files_dir: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/tests/test__basic_nested_parts/doc/output_pdf/generated_intermediate_files'
generated_output_files_dir: '/home/ubuntu/from_host/x/Documents/git_repos/documentation/tools/pandown/tests/test__basic_nested_parts/doc/output_pdf/generated_output_files'
title: Some title
subtitle: And a small subtitle
documentclass: paper
panflute-filters: [ignore_comments, assemble_parts,mermaid_charts, copy_linked_items, minted_code]
...

The headings and depth etc of `1_subfolderA`, `2_subfolderB` and `3_subfolderC` should be identical. (how to refer to headings, with internal links?)

``` parts
1_subfolderA
2_subfolderB
3_subfolderC
e_file1.md
f_file2.md
```
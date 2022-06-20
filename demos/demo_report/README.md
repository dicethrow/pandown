This shows the simplest possible way to use pandown. 

Edit the source files in `doc/content`, then run `build.py`.
That will combine the source files and a latex template into `doc/generated_intermediate_files/*.latex`, and that latex file will then be used to generate `doc/output/result.pdf`.

Note that `open_workspace_in_doc-dev.sh` is a script that starts vscode in my `doc-dev` LXD container, you don't need this script if you don't want to use a virtual machine/container.

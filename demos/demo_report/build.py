import argparse, os, subprocess, textwrap
import pandown

def clear_terminal():
	# clean the terminal before we start.
	subprocess.call("clear")


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("task", type=str, help="action to do")
	# parser.add_argument("proj_location", type=str, help="project dir to build")
	args = parser.parse_args()

	assert args.task in ["generate"], "invalid task given"

	if args.task == "generate":
		# in the container, copy over the proj_location/content, and template
		# then, run the container:proj_location/build.py
		# which goes through the document and does its thing

		clear_terminal()

		with  pandown.RemoteClient(host = "lxd_doc-dev", lxd_container_name = "doc-dev", user = "ubuntu", 
			ssh_config_filepath="~/.ssh/config") as ssh_remote_client:

			ssh_remote_client.clean()

			def copy_over_common_content():
				# the directory that this .py file is in
				# dir_path = os.path.dirname(os.path.realpath(__file__))
				dir_path = pandown.get_absolute_content_dir("for_report")
				print("dir path is ", dir_path)
				ssh_remote_client.rsync(
					delete = True,
					direction="local_to_remote",
					rel_local_dir=dir_path,#"demos/demo_report",#f"{args.proj_location}",#"content",
					rel_remote_dir="Uploads"
					# abs_remote_dir="home/ubuntu/Uploads/content"
				)
			copy_over_common_content()

			def copy_over_content():
				# the directory that this .py file is in
				dir_path = os.path.dirname(os.path.realpath(__file__))

				ssh_remote_client.rsync(
					delete = False,
					direction="local_to_remote",
					rel_local_dir=dir_path,#"demos/demo_report",#f"{args.proj_location}",#"content",
					rel_remote_dir="Uploads"
					# abs_remote_dir="home/ubuntu/Uploads/content"
				)
			copy_over_content()

			# move templates to right folder
			ssh_remote_client.execute_commands("rsync -av ~/Documents/Uploads/templates/ ~/.pandoc/templates/")

			ssh_remote_client.execute_commands("echo 'on rpi'")
			ssh_remote_client.execute_commands("pwd")
			ssh_remote_client.execute_commands("tree -a -I host_venv")
			
			# output_type = "md"
			output_type = "pdf"

			# template = "eisvogel.latex"
			template = "test.latex"

			script_runner = "-F ~/.local/bin/panflute"
			top_source_file = "~/Documents/Uploads/content/main.md"
			template_file = f"--template ~/.pandoc/templates/{template}"
			output_file = f"-o ~/Documents/Outputs/result.{output_type}"


			use_tex_intermediate = False
			if use_tex_intermediate:
				tex_intermediate_file = f"~/Documents/Outputs/result.tex"
				pandoc_cmd = f"pandoc {script_runner} {top_source_file} {template_file} -s -o {tex_intermediate_file}"
				pandoc_cmd2 = f"pandoc {tex_intermediate_file} {output_file}"
				ssh_remote_client.execute_commands([pandoc_cmd,pandoc_cmd2], ignore_failures=True) # 	 

			else:
				pandoc_cmd = f"pandoc {script_runner} {top_source_file} {template_file} {output_file}"
				ssh_remote_client.execute_commands(pandoc_cmd, ignore_failures=True) # 	 

			
			# ssh_remote_client.execute_commands(["cd ~/Documents/Uploads/content", "pandoc -F ~/.local/bin/panflute main.md -o /../Outputs/result.md", "cd ~"], ignore_failures=True)
			
			ssh_remote_client.execute_commands("tree -a -I host_venv")
			ssh_remote_client.execute_commands("cat ~/Documents/Outputs/result.*")

			def copy_back_results():
				ssh_remote_client.rsync(
					delete = True,
					direction="remote_to_local",
					rel_local_dir="demos/demo_report/outputs",#f"{args.proj_location}/outputs",
					rel_remote_dir="Outputs"
					# abs_remote_dir="home/ubuntu/Outputs"
				)
			copy_back_results()

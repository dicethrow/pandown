import argparse, os, subprocess, textwrap
import pandown, lxdev

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

		with  lxdev.RemoteClient(
			host = "lxd_doc-dev", 
			lxd_container_name = "doc-dev",
			local_working_directory = os.path.dirname(os.path.realpath(__file__))
			) as ssh_remote_client:
			
			ssh_remote_client.empty_folders(["outputs"], "local_and_remote")

			pandown.copy_starter_resources(src=["for_report/filters", "for_report/templates"], dst=ssh_remote_client.local_working_directory, skip_if_dest_not_empty = True)

			ssh_remote_client.rsync_to_container()
			
			ssh_remote_client.execute_commands(f"rsync -av {ssh_remote_client.remote_working_directory}/for_report/templates/ ~/.pandoc/templates/")

			ssh_remote_client.execute_commands("pwd")
			ssh_remote_client.execute_commands(f"tree -a {ssh_remote_client.remote_working_directory}")
			
			# output_type = "md"
			output_type = "pdf"

			# template = "eisvogel.latex"
			# template = "test.latex"
			template = "test2.latex"

			script_runner = "-F ~/.local/bin/panflute"
			# top_source_file = "~/Documents/Uploads/content/main.md"
			top_source_file = f"{ssh_remote_client.remote_working_directory}/content/main.md"
			# template_file = f"--template ~/.pandoc/templates/{template}"
			template_file = f"--template {ssh_remote_client.remote_working_directory}/for_report/templates/{template}"
			# output_file = f"-o ~/Documents/Outputs/result.{output_type}"
			output_file = f"-o {ssh_remote_client.remote_working_directory}/output"
			extras = "--listings"
			# extras = ""


			use_tex_intermediate = True#False
			if use_tex_intermediate:
				# tex_intermediate_file = f"/Outputs/result.tex"
				tex_intermediate_file = f"{ssh_remote_client.remote_working_directory}/outputs/result.tex"
				pandoc_cmd = f"pandoc {script_runner} {top_source_file} {template_file} -s -o {tex_intermediate_file} {extras}"
				# pandoc_cmd2 = f"pandoc {tex_intermediate_file} {output_file}"
				# pandoc_cmd2 = f"pandoc {script_runner} {top_source_file} {template_file} {output_file}"
				# ssh_remote_client.execute_commands([pandoc_cmd,pandoc_cmd2], ignore_failures=True) # 	 
				
				latex_cmd = f"lualatex -shell-escape -halt-on-error --output-directory {ssh_remote_client.remote_working_directory}/outputs {tex_intermediate_file}" # options go before filename https://tex.stackexchange.com/questions/268997/pdflatex-seems-to-ignore-output-directory

				ssh_remote_client.execute_commands(pandoc_cmd, ignore_failures=True) # 	 
				
				# lualatex needs to be caled twice, otherwise the toc doesn't generate properly
				# if references, call biber between
				ssh_remote_client.execute_commands(latex_cmd, ignore_failures=True)
				
				ssh_remote_client.execute_commands(latex_cmd, ignore_failures=True)
			else:
				pandoc_cmd = f"pandoc {script_runner} {top_source_file} {template_file} {output_file} {extras}"
				ssh_remote_client.execute_commands(pandoc_cmd, ignore_failures=True) # 	 

			# remove undesired output
			ssh_remote_client.execute_commands(f"cd {ssh_remote_client.remote_working_directory}/outputs && rm *.aux *.bcf *.log *.out *.xml *.toc")
						
			ssh_remote_client.execute_commands(f"tree -a {ssh_remote_client.remote_working_directory}")

			ssh_remote_client.rsync_from_container()

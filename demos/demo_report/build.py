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

			def copy_over_content():
				ssh_remote_client.rsync(
					delete = True,
					direction="local_to_remote",
					rel_local_dir="demos/demo_report",#f"{args.proj_location}",#"content",
					rel_remote_dir="Uploads"
					# abs_remote_dir="home/ubuntu/Uploads/content"
				)
			copy_over_content()

			ssh_remote_client.execute_commands("echo 'on rpi' && pwd && tree")
			
			ssh_remote_client.execute_commands("pandoc -F ~/.local/bin/panflute ~/Documents/Uploads/content/main.md -o ~/Documents/Outputs/result.md", ignore_failures=True) # 	 	
			
			# ssh_remote_client.execute_commands(["cd ~/Documents/Uploads/content", "pandoc -F ~/.local/bin/panflute main.md -o /../Outputs/result.md", "cd ~"], ignore_failures=True)
			
			ssh_remote_client.execute_commands("tree")
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

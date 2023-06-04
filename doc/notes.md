# Setting up your computer

## Table of contents

1. [System overview](./0_documentation.md)
2. [Setting up your computer](./1_computer_setup.md) *This document*
3. [Firmware validation](./2_validation_of_firmware.md)
4. [Hardware validation](./3_validation_of_hardware.md)
5. [Usage of firmware](./4_usage_of_firmware.md)
6. [Design of firmware](./5_design_of_firmware.md)
7. [Common problems and fixes](./6_common_problems_and_fixes.md)

## Key concepts

**vscode** is a text editor used for writing and running code

**platformio** is an extension/plugin for text editors like vscode, and is similar to arduino. It makes available functionality to run our code on our hardware

**git** is a software tool with a command line interface for version control

**bitbucket** is a database that holds git data

**private key, public key** are two parts of the SSH encryption process used by bitbucket that, when set up, will allow us to use git without having to enter a password each time

**gitk** is a software tool with a graphical interface for visually inspecting the status of git 

**project directory** is the root directory of this repository, and is the reference location for files when paths are specified. For example, the location of this file is `doc/1_computer_setup.md`, which is its relative location from the project directory.

**joulescope** is a hardware tool for measuring power consumption which, when connected over USB, has a graphical interface

**development and testing environment** refers to the connection of various pieces of hardware that are required to implement code and run tests, as shown in this diagram:

``` mermaid
flowchart LR
	%% elements
	pcb(PCB)
	pc(Development computer)
	jig(Programming jig)
	joulescope("Joulescope (optional)")
	battery(LiPo battery)

	pc <-- USB connection --> jig
	pc <-- USB connection --> joulescope

	battery -. two wires carrying 4.2v .-> joulescope -.-> jig
	jig -- pogo pins --> pcb
```

## Previous problems and fixes

- Don't have whitespace in your file paths. This means that you shouldn't use a folder that is hosted on onedrive, as that means you'd have whitespace in your filepath.
- Install python before vscode, if your computer doesn't have python. Once we had an issue where vscode found a weird version of python, which caused failures.
- If you want to open a markdown preview of this file, right-click this file's tab, and click `Open preview`
- If you get a compiler error, try re-opening vscode by using 'run as admin'.
## Procedure

1. Set up a bitbucket SSH key for your computer:
	
	This is so platformio can get access to the camera library, hosted on bitbucket. See line 22 of `platformio.ini` for this library

	- On windows: Follow the steps [here](https://support.atlassian.com/bitbucket-cloud/docs/set-up-an-ssh-key/), which are:
		1. Click the search icon on your windows desktop, **type `powershell`**. One program should match, run it.

		2. You should see a black window with a prompt, which will allow us to run command line interface programs. **Type `ssh-keygen`** and press enter. Several prompts will be printed to screen, **press enter for each one**, which will select the default options. You'll see some information saying the private key is saved to a location like `C:\Users\ZacWylde/.ssh/id_rsa`.

		3. Note that for this step, we want the public key, not the private key. To open the public key, add `.pub` to the path printed in the previous step, and open it in a text editor. A convenient way to do this is to **type ```cat 'C:\Users\ZacWylde\.ssh\id_rsa.pub'```**, changing this to use your user account name printed in the previous step, and **ensure the file path is in quotation marks**. Highlight the content that is printed out, and **copy the contents for the next step**.
		
		4. Open bitbucket, navigate to personal settings, then to ssh keys. Click Add SSH key, and **copy and paste the contents of the file you opened in the previous step**.

2. **Install python**, using this [download link](https://www.python.org/downloads/). When in the installer, **ensure the `Add Python 3.xx to PATH` checkbox is ticked**, as that will enable platformio to use python. When installation finishes, an option to `Disable path length limit` will appear, **click this link** to disable path length limit. Not doing this may otherwise cause issues later on.

	- In order to run some wifi tests, the python library `requests` is required. To install this, **open a terminal** (e.g. right click on your desktop and click `Open in terminal`), and **type `pip install requests`**, then **press enter**.

3. If using windows or mac, we'll need to install a driver for connecting to the programming jig, so **install the driver** from [this link](https://silabs.com/developers/usb-to-uart-bridge-vcp-drivers). Unzip the downloaded folder and **follow the instructions within the text file** (i.e. right-click on the `silaber` file and click `install`).

4. **Install git** using this [download link](https://gitforwindows.org/), changing the default text editor to notepad, keeping all other default settings.

5. Clone this repository to a folder on your computer, such as your desktop:
	
	1. Open a folder in file explorer where you'd like to save a copy of this repository, then **right-click in some white space** and select `Open in Terminal`, and a black termainal window will open (If this option doesn't appear, open powershell like before, type `cd`, press space, then drag the folder into the termainal (this will enter its path), and press enter. This will have the same effect). Press enter a few times and you'll see that you have a writing prompt that looks like `PS C:\Users\ZacWylde\Desktop>`. Make sure that there is no whitespace in the path shown here, if repeat this step after selecting a different folder. This will allow us to run commands relative to this directory. 

	2. In this terminal, enter ```git clone git@bitbucket.org:apsyn/2021-13-bedbug-firmware-platformio.git``` and press enter. This will use the SSH key set up in previous steps to log in and download the code. If prompted, type 'yes' to accept the key fingerprint from the bitbucket server.

6. Install vscode [Download link](https://code.visualstudio.com/download)

7. In file explorer, open the project directory (the folder that was created when you ran the `git clone` step before), and open the file `bedbug-firmware.code-workspace` with vscode. The first time you open vscode, some popups may appear asking for further set up. Feel free to ignore these, and press 'yes' to trusting the authors.

*The following steps assume that you have opened the repository with vscode, as described in the previous step*

8. Open up this readme file in vscode, by navigating to `doc/0_computer_setup.md` in the file tree on the left hand window, and double clicking it. Install the `Markdown Preview Mermaid Support` extension by copying the actions in gif, this will allow displaying of some diagrams in this document. Then in the preview window that you produce by following all steps in the gif, under the `Table of contents` heading, click the `Setting up your computer` link to open this file.

![xx](./attachments/install_mermaid_extension.gif)

9. In the same way as the previous step, install the `PlatformIO IDE` extension for vscode.

10. Set up config files. These are files which are unique to your computer and so are not tracked by git. This means that these files do not exist until we make them, which is what we'll do now.

	1. Set up the `private_config.ini` file, which tells platformio how to connect to the jig over USB.

		In the vscode file tree, right click on the `private_config.ini.example` file, and make a copy of it, note that this will make a file called `private_config.ini.example.copy` and rename the copy to remove the `.example.copy` from the filename, so that we end up with a new file called `private_config.ini`. Now we need to add to this file which serial port connects to the programming jig. Plug in the jig to your development computer with a USB connection:

		``` mermaid
		flowchart LR
			%% elements
			pc(Development computer)
			jig(Programming jig)

			pc <-- USB connection --> jig
		```

		- If using windows: click `Start` and search for `Device manager`, and open it, and find the serial ports entry. Plug in the USB cable to the jig, and two new entries to the comms ports list should appear, such as `COM10` and `COM11`.

		- If using mac: ...

		- If using linux: plug in the USB connection to the jig, and in the terminal type `ls /dev/ttyUSB*`. Two serial ports should appear (e.g. `/dev/ttyUSB0`, `/dev/ttyUSB1`), make a note of the higher one (e.g. `/dev/ttyUSB1').

		In the `private_config.ini` file, replace all instances of `/dev/ttyUSB0` with the higher of the two found serial ports above, such as (on windows) `COM4` or `COM11` or (on linux) `/dev/ttyUSB1` or (on mac) ... .


	2. Set up the `lib/config/config.cpp` file, which specifies some options for device behaviour, such as wifi password and which server to connect to.

		In the vscode file tree, navigate to the `lib/config/config.cpp.example` file, and in the same way as the previous step, copy this file and rename it without the `.example` file, so that the `lib/config/config.cpp` file is made.

		The default content of this file will work, and if you'd like to change any of the settings within it, this is the place to make those changes.
	
11. Get access to the platformio command line tools


	- If using windows: this step is detailed in [this resource](https://docs.platformio.org/en/stable/core/installation/shell-commands.html#windows), which is:
		1. Check that one of 
		
			```C:\Users\UserName\.platformio\penv\Scripts;```
		
			(replacing `UserName` with your username) or
		
			```C:\.platformio\penv\Scripts;```
		 
		  	exists, and make a note of which one. To do this, it's easiest if you use your file browser to try to navigate to this directory. Note that you'll need to enable viewing hidden folders.

		2. Following [this guide](https://www.computerhope.com/issues/ch000549.htm), add the path found in the previous step to the system PATH. The red regions in this screenshot indicate the buttons to press, following that guide.

		![append to path windows](./attachments/append_to_path_windows.png)

	- If using mac: ...
	- If using linux: In termainal, run

		``` bash
		ln -s ~/.platformio/penv/bin/platformio ~/.local/bin/platformio
		ln -s ~/.platformio/penv/bin/pio ~/.local/bin/pio
		ln -s ~/.platformio/penv/bin/piodebuggdb ~/.local/bin/piodebuggdb
		```

		Then the command `pio` will become available in a terminal that has sourced `~/.profile`. Note that vscode doesn't do this, so this is why the tasks in `bedbug-firmware.code-workspace` have `source ~/.profile` in the command.

11. Optionally, to use the joulescope tool to measure power consumption, in a termainal window run ```pip3 install -U joulescope_ui```. To start the joulescope, click `Terminal`, then `Run task`, then `Start joulescope (if installed)`.

12. Test that you can compile and upload to the device, by following the next section of the documentation in [Firmware validation](./2_validation_of_firmware.md)


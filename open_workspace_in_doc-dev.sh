#!/usr/bin/env bash

# Copy the current git repo to the container, edit/build in vscode in the container, then on closing vscode, copy them back to the host.

# (why is this line needed? 15may22)
# change directory to current location of this .sh file, from https://stackoverflow.com/questions/3349105/how-can-i-set-the-current-working-directory-to-the-directory-of-the-script-in-ba
cd "${0%/*}" # yuck syntax


(cd $(git rev-parse --show-toplevel); lxdev rsync_to_container lxd_doc-dev delete)
remote_dir=$(lxdev get_remote_working_directory lxd_doc-dev keep)
lxc shell doc-dev -- sh -c "chown -R ubuntu:ubuntu ${remote_dir}" # although <user 1> and ubuntu both have uid=1000, <user 2> is 1001 so needs this to make copied files have the right permissions. todo - fix this in lxdev?
ssh lxd_doc-dev -- codium "${remote_dir}/*.code-workspace" # assuming there's only one .code-workspace file
(cd $(git rev-parse --show-toplevel); lxdev rsync_from_container lxd_doc-dev delete)

#read -p "Press any key to continue" x


# from lxdev import RemoteClient, myRemoteException, LOGGER
from .doc_resources import get_path_to_common_content
from .common import run_local_cmd, clear_terminal, remove_generated_files, debug_elem
from .build_default_doc import build_default_doc, test_rmii_sync
from .my_logging import loggerClass
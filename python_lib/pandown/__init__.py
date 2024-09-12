# from lxdev import RemoteClient, myRemoteException, LOGGER
from .doc_resources import get_path_to_common_content
from .common import run_local_cmd, clear_terminal, remove_generated_files, debug_elem
from .build_default_pdf import build_default_pdf, test_rmii_sync
from .build_default_html import build_default_html
from .build_default_odt import build_default_odt
from .my_logging import loggerClass
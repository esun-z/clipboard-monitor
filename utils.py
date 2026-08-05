import hashlib
from pathlib import Path
import winreg
import sys
from logging import getLogger
from PySide6.QtCore import QMimeData

logger = getLogger(__name__)

def compute_mime_hash(mime_data: QMimeData) -> str:
    h = hashlib.sha256()
    formats = sorted(mime_data.formats())
    for fmt in formats:
        h.update(fmt.encode('utf-8'))
        h.update(mime_data.data(fmt))
    return h.hexdigest()

def register_aumid_hkey(app_id: str, display_name: str, icon_path: Path):
    app_id = app_id.replace("\\", ".")
    if not icon_path.exists():
        logger.error(f"Could not register the application: File {icon_path} does not exist")
    elif icon_path.suffix != ".ico":
        logger.error(f"Could not register the application: File {icon_path} must be of type .ico")
    try:
        winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{app_id}"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as masterKey:
            winreg.SetValueEx(masterKey, "DisplayName", 0, winreg.REG_SZ, display_name)
            logger.info(f"Successfully registered the application ID '{app_id}' with display name '{display_name}'")
            if icon_path is not None:
                winreg.SetValueEx(masterKey, "IconUri", 0, winreg.REG_SZ, str(icon_path.resolve()))
    except Exception as e:
        logger.error(f"Failed to register AUMID in the registry: {e}")

def get_resource_path(relative_path: str) -> Path:
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent
    
    return base_path / relative_path

# def remove_aumid_hkey(app_id: str):
#     app_id = app_id.replace("\\", ".")
#     try:
#         winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
#         keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{app_id}"
#         with winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyPath, 0, winreg.KEY_ALL_ACCESS) as masterKey:
#             winreg.DeleteKey(masterKey, "")
#             logger.info(f"Successfully removed the application ID '{app_id}' from the registry")
#     except FileNotFoundError:
#         logger.warning(f"Application ID '{app_id}' not found in the registry")
#     except Exception as e:
#         logger.error(f"Failed to remove AUMID from the registry: {e}")
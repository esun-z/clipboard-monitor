from typing import Optional
from PySide6.QtWidgets import QApplication
from utils import compute_mime_hash
from notifier import Notifier

class Monitor:
    def __init__(self, notifier: Notifier):
        self._notifier = notifier
        self._last_hash: Optional[str] = None
        self._clipboard = QApplication.clipboard()
        self._clipboard.dataChanged.connect(self.on_data_changed)

    def on_data_changed(self):
        mime_data = self._clipboard.mimeData()
        
        if mime_data is None:
            return
            
        current_hash = compute_mime_hash(mime_data)
        
        if current_hash == self._last_hash:
            return
            
        self._last_hash = current_hash
        
        self._notifier.notify_clipboard_change(mime_data)
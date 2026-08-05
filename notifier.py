from typing import List
from windows_toasts import InteractableWindowsToaster, Toast, ToastDuration, ToastDisplayImage, ToastImage, ToastImagePosition
from PySide6.QtCore import QMimeData, QObject, QUrl, QTimer
from PySide6.QtGui import QImage
import filetype
from pathlib import Path
from logging import getLogger
from utils import register_aumid_hkey
import datetime

class Notifier(QObject):
    def __init__(self, aumid: str, display_name: str, icon_path: Path, parent: QObject = None):
        super().__init__(parent)
        self.display_name = display_name
        self.icon_path = icon_path
        self.aumid = aumid
        register_aumid_hkey(app_id=aumid, display_name=display_name, icon_path=icon_path)
        self.toaster = InteractableWindowsToaster(applicationText=display_name, notifierAUMID=aumid)
        self.logger = getLogger(__name__)
        self._freezed = False

    def notify_clipboard_change(self, mime_data: QMimeData):
        if self._freezed:
            return
        current_datetime = datetime.datetime.now()
        toast = Toast(
            duration=ToastDuration.Short,
            group=self.display_name,
            expiration_time=current_datetime + datetime.timedelta(minutes=5),
        )

        toast.tag = self.aumid

        if mime_data.hasImage():
            if mime_data.hasUrls():
                urls = mime_data.urls()
                url_list = self._get_url_str_list(urls)
                if self._is_url_list_image(url_list):
                    toast.AddImage(ToastDisplayImage(
                        image=ToastImage(imagePath=url_list[0]),
                        altText="Copied Image",
                        position=ToastImagePosition.Hero,
                    ))
                toast.text_fields.append("Image and URLs Copied")
                toast.text_fields.extend(url_list)
            else:
                # save that image to a temporary file and add it to the toast
                temp_image_path = "temp_clipboard_image.png"
                if self._save_temp_image(mime_data, temp_image_path):
                    toast.AddImage(ToastDisplayImage(
                        image=ToastImage(imagePath=temp_image_path),
                        altText="Copied Image",
                        position=ToastImagePosition.Hero,
                    ))
                toast.text_fields.append("Image Copied")
        elif mime_data.hasUrls():
            urls = mime_data.urls()
            url_list = self._get_url_str_list(urls)
            toast.text_fields.append("URLs Copied")
            toast.text_fields.extend(url_list)
        
        elif mime_data.hasText():
            text = mime_data.text()
            toast.text_fields.append("Text Copied")
            toast.text_fields.append(text)
        
        else:
            toast.text_fields.append("Clipboard Changed")
            toast.text_fields.append("Unknown content type")
            self.logger.info(f"Unknown content type in clipboard. Types: {", ".join(mime_data.formats())}")

        self.toaster.show_toast(toast)

        # freeze
        self._freezed = True
        QTimer.singleShot(0, self._unfreeze_notifier)

    def _save_temp_image(self, mime_data: QMimeData, output_path: str) -> bool:
        """将剪贴板中的图像保存为临时文件"""
        if not mime_data or not mime_data.hasImage():
            self.logger.error("No image data found in the clipboard.")
            return False

        image: QImage = mime_data.imageData()
        if image is None or image.isNull():
            self.logger.error("Failed to convert clipboard data to QImage.")
            return False

        success = image.save(output_path)
        if not success:
            self.logger.error(f"Failed to save image to {output_path}.")
        return success

    def _unfreeze_notifier(self):
        self._freezed = False
    
    @staticmethod
    def _is_url_list_image(url_list: list) -> bool:
        """检查 URL 列表中的第一个 URL 是否指向图像文件"""
        if not url_list:
            return False
        first_url = url_list[0]
        return filetype.is_image(first_url)

    @staticmethod
    def _get_url_str_list(url_list: List[QUrl]) -> List[str]:
        return [
            url.toLocalFile() if url.isLocalFile() else url.toString()
            for url in url_list
        ]
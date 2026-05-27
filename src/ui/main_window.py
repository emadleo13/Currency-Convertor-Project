from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt

from src.core.converter import CurrencyConverter
from src.i18n.language_manager import language_manager as lang
from src.ui.converter_widget import ConverterWidget
from src.ui.styles import get_stylesheet
from src.utils.constants import WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._converter = CurrencyConverter()
        self._setup_ui()
        lang.language_changed.connect(self._on_language_changed)
        self._apply_language()

    def _setup_ui(self):
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(540, 500)

        self._converter_widget = ConverterWidget(self._converter)
        self.setCentralWidget(self._converter_widget)

    def _on_language_changed(self, lang_code: str):
        self._apply_language()

    def _apply_language(self):
        self.setWindowTitle(lang.t("app_title"))
        direction = Qt.LayoutDirection.RightToLeft if lang.is_rtl else Qt.LayoutDirection.LeftToRight
        self.setLayoutDirection(direction)
        self.setStyleSheet(get_stylesheet(lang.is_rtl))

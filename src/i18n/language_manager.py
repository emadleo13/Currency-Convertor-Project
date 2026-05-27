from PyQt6.QtCore import QObject, pyqtSignal

from src.i18n.translations import TRANSLATIONS


class LanguageManager(QObject):
    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._current = "fa"

    @property
    def current(self) -> str:
        return self._current

    @property
    def is_rtl(self) -> bool:
        return self._current == "fa"

    def switch(self):
        self._current = "fa" if self._current == "en" else "en"
        self.language_changed.emit(self._current)

    def t(self, key: str, **kwargs) -> str:
        text = TRANSLATIONS.get(key, {}).get(self._current, key)
        if kwargs:
            text = text.format(**kwargs)
        return text


language_manager = LanguageManager()

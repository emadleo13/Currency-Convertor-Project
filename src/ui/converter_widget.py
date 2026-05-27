from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDoubleValidator

from src.core.converter import CurrencyConverter
from src.core.currencies import CURRENCIES, POPULAR_CURRENCIES
from src.i18n.language_manager import language_manager as lang


class FetchWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, converter: CurrencyConverter, from_code: str, to_code: str):
        super().__init__()
        self.converter = converter
        self.from_code = from_code
        self.to_code = to_code

    def run(self):
        try:
            involves_irr = self.from_code == "IRR" or self.to_code == "IRR"

            if involves_irr:
                self.converter.fetch_irr_rates()
                source = "tgju"
            else:
                last_updated = self.converter.fetch_exchange_rates(self.from_code)
                source = "api"

            rate = self.converter.get_rate(self.from_code, self.to_code)
            self.finished.emit({
                "rate": rate,
                "source": source,
                "last_updated": locals().get("last_updated", ""),
            })
        except Exception as e:
            self.error.emit(str(e))


class ConverterWidget(QWidget):
    def __init__(self, converter: CurrencyConverter):
        super().__init__()
        self._converter = converter
        self._worker = None
        self._setup_ui()
        self._connect_signals()
        lang.language_changed.connect(self._on_language_changed)
        self._apply_language()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(28, 20, 28, 20)

        # Header
        header = QHBoxLayout()
        self._title_label = QLabel()
        self._title_label.setObjectName("titleLabel")
        self._lang_btn = QPushButton()
        self._lang_btn.setObjectName("langBtn")
        self._lang_btn.setFixedWidth(80)
        header.addWidget(self._title_label)
        header.addStretch()
        header.addWidget(self._lang_btn)
        main_layout.addLayout(header)

        # Amount
        self._amount_label = QLabel()
        main_layout.addWidget(self._amount_label)

        self._amount_input = QLineEdit()
        self._amount_input.setObjectName("amountInput")
        validator = QDoubleValidator(0.0, 999_999_999_999.0, 6)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self._amount_input.setValidator(validator)
        main_layout.addWidget(self._amount_input)

        # Currency selectors
        currency_layout = QHBoxLayout()
        currency_layout.setSpacing(8)

        from_layout = QVBoxLayout()
        self._from_label = QLabel()
        self._from_combo = QComboBox()
        self._from_combo.setEditable(True)
        self._from_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._from_combo.completer().setCompletionMode(
            self._from_combo.completer().CompletionMode.PopupCompletion
        )
        from_layout.addWidget(self._from_label)
        from_layout.addWidget(self._from_combo)

        self._swap_btn = QPushButton("⇄")
        self._swap_btn.setObjectName("swapBtn")
        self._swap_btn.setFixedSize(50, 50)

        to_layout = QVBoxLayout()
        self._to_label = QLabel()
        self._to_combo = QComboBox()
        self._to_combo.setEditable(True)
        self._to_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._to_combo.completer().setCompletionMode(
            self._to_combo.completer().CompletionMode.PopupCompletion
        )
        to_layout.addWidget(self._to_label)
        to_layout.addWidget(self._to_combo)

        currency_layout.addLayout(from_layout, 1)
        currency_layout.addWidget(self._swap_btn, 0, Qt.AlignmentFlag.AlignBottom)
        currency_layout.addLayout(to_layout, 1)
        main_layout.addLayout(currency_layout)

        # Convert button
        self._convert_btn = QPushButton()
        self._convert_btn.setObjectName("convertBtn")
        main_layout.addWidget(self._convert_btn)

        # Result frame
        self._result_frame = QFrame()
        self._result_frame.setObjectName("resultFrame")
        self._result_frame.setVisible(False)
        result_layout = QVBoxLayout(self._result_frame)
        result_layout.setSpacing(6)

        self._result_amount_label = QLabel()
        self._result_amount_label.setObjectName("resultAmount")
        self._result_amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._rate_label = QLabel()
        self._rate_label.setObjectName("rateLabel")
        self._rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        result_layout.addWidget(self._result_amount_label)
        result_layout.addWidget(self._rate_label)
        main_layout.addWidget(self._result_frame)

        # Status
        self._status_label = QLabel()
        self._status_label.setObjectName("statusLabel")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._error_label = QLabel()
        self._error_label.setObjectName("errorLabel")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setVisible(False)

        main_layout.addStretch()
        main_layout.addWidget(self._error_label)
        main_layout.addWidget(self._status_label)

        self._populate_combos()
        self._from_combo.setCurrentIndex(self._find_currency_index(self._from_combo, "USD"))
        self._to_combo.setCurrentIndex(self._find_currency_index(self._to_combo, "IRR"))

    def _populate_combos(self):
        self._from_combo.blockSignals(True)
        self._to_combo.blockSignals(True)

        from_current = self._get_current_code(self._from_combo)
        to_current = self._get_current_code(self._to_combo)

        self._from_combo.clear()
        self._to_combo.clear()

        l = lang.current
        ordered = []
        for code in POPULAR_CURRENCIES:
            if code in CURRENCIES:
                info = CURRENCIES[code]
                label = f"{info['flag']} {code} - {info[l]}"
                ordered.append((code, label))

        for code in sorted(CURRENCIES.keys()):
            if code not in POPULAR_CURRENCIES:
                info = CURRENCIES[code]
                label = f"{info['flag']} {code} - {info[l]}"
                ordered.append((code, label))

        for code, label in ordered:
            self._from_combo.addItem(label, code)
            self._to_combo.addItem(label, code)

        if from_current:
            idx = self._find_currency_index(self._from_combo, from_current)
            if idx >= 0:
                self._from_combo.setCurrentIndex(idx)
        if to_current:
            idx = self._find_currency_index(self._to_combo, to_current)
            if idx >= 0:
                self._to_combo.setCurrentIndex(idx)

        self._from_combo.blockSignals(False)
        self._to_combo.blockSignals(False)

    def _find_currency_index(self, combo: QComboBox, code: str) -> int:
        for i in range(combo.count()):
            if combo.itemData(i) == code:
                return i
        return 0

    def _get_current_code(self, combo: QComboBox) -> str:
        idx = combo.currentIndex()
        if idx >= 0:
            return combo.itemData(idx) or ""
        return ""

    def _connect_signals(self):
        self._convert_btn.clicked.connect(self._on_convert)
        self._swap_btn.clicked.connect(self._on_swap)
        self._lang_btn.clicked.connect(lang.switch)
        self._amount_input.returnPressed.connect(self._on_convert)

    def _on_convert(self):
        text = self._amount_input.text().strip()
        if not text:
            self._show_error(lang.t("invalid_amount"))
            return

        try:
            amount = float(text)
        except ValueError:
            self._show_error(lang.t("invalid_amount"))
            return

        if amount <= 0:
            self._show_error(lang.t("invalid_amount"))
            return

        from_code = self._get_current_code(self._from_combo)
        to_code = self._get_current_code(self._to_combo)

        if not from_code or not to_code:
            return

        self._error_label.setVisible(False)
        self._convert_btn.setEnabled(False)
        self._convert_btn.setText(lang.t("fetching"))

        self._worker = FetchWorker(self._converter, from_code, to_code)
        self._worker.finished.connect(lambda data: self._on_fetch_done(data, amount, from_code, to_code))
        self._worker.error.connect(self._on_fetch_error)
        self._worker.start()

    def _on_fetch_done(self, data: dict, amount: float, from_code: str, to_code: str):
        self._convert_btn.setEnabled(True)
        self._convert_btn.setText(lang.t("convert"))

        try:
            result = self._converter.convert(amount, from_code, to_code)
        except Exception as e:
            self._show_error(str(e))
            return

        result_text = f"{self._format_number(result)} {to_code}"
        self._result_amount_label.setText(result_text)

        rate = data["rate"]
        rate_text = lang.t("rate_display",
                           from_c=from_code,
                           rate=self._format_number(rate),
                           to_c=to_code)
        self._rate_label.setText(rate_text)

        source_key = "source_tgju" if data["source"] == "tgju" else "source_api"
        self._status_label.setText(lang.t(source_key))

        self._result_frame.setVisible(True)

    def _on_fetch_error(self, error_msg: str):
        self._convert_btn.setEnabled(True)
        self._convert_btn.setText(lang.t("convert"))
        self._show_error(error_msg)

    def _show_error(self, msg: str):
        self._error_label.setText(msg)
        self._error_label.setVisible(True)

    def _on_swap(self):
        from_idx = self._from_combo.currentIndex()
        to_idx = self._to_combo.currentIndex()
        self._from_combo.setCurrentIndex(to_idx)
        self._to_combo.setCurrentIndex(from_idx)

    def _on_language_changed(self, lang_code: str):
        self._apply_language()

    def _apply_language(self):
        direction = Qt.LayoutDirection.RightToLeft if lang.is_rtl else Qt.LayoutDirection.LeftToRight
        self.setLayoutDirection(direction)

        self._title_label.setText(lang.t("app_title"))
        self._lang_btn.setText(lang.t("language_switch"))
        self._amount_label.setText(lang.t("amount"))
        self._amount_input.setPlaceholderText(lang.t("enter_amount"))
        self._from_label.setText(lang.t("from_currency"))
        self._to_label.setText(lang.t("to_currency"))
        self._swap_btn.setToolTip(lang.t("swap_tooltip"))
        self._convert_btn.setText(lang.t("convert"))

        self._populate_combos()

    @staticmethod
    def _format_number(value: float) -> str:
        if value >= 1:
            return f"{value:,.2f}"
        elif value >= 0.01:
            return f"{value:,.4f}"
        else:
            return f"{value:,.6f}"

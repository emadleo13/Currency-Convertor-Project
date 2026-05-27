def get_stylesheet(is_rtl: bool = False) -> str:
    if is_rtl:
        font_family = '"Vazirmatn", "Tahoma", "Segoe UI", sans-serif'
    else:
        font_family = '"Segoe UI", "Tahoma", sans-serif'

    return f"""
        * {{
            font-family: {font_family};
        }}

        QMainWindow {{
            background-color: #F8FAFC;
        }}

        QLabel {{
            color: #1E293B;
            font-size: 13px;
        }}

        QLabel#titleLabel {{
            font-size: 20px;
            font-weight: bold;
            color: #1E40AF;
        }}

        QLabel#resultAmount {{
            font-size: 22px;
            font-weight: bold;
            color: #1E40AF;
        }}

        QLabel#rateLabel {{
            font-size: 13px;
            color: #64748B;
        }}

        QLabel#statusLabel {{
            font-size: 11px;
            color: #94A3B8;
        }}

        QLabel#errorLabel {{
            font-size: 12px;
            color: #DC2626;
        }}

        QLineEdit {{
            padding: 10px 14px;
            border: 2px solid #CBD5E1;
            border-radius: 8px;
            font-size: 16px;
            background-color: #FFFFFF;
            color: #1E293B;
        }}

        QLineEdit:focus {{
            border-color: #2563EB;
        }}

        QComboBox {{
            padding: 8px 12px;
            border: 2px solid #CBD5E1;
            border-radius: 8px;
            font-size: 13px;
            background-color: #FFFFFF;
            color: #1E293B;
            min-width: 180px;
        }}

        QComboBox:focus {{
            border-color: #2563EB;
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #64748B;
            margin-right: 10px;
        }}

        QComboBox QAbstractItemView {{
            border: 1px solid #CBD5E1;
            border-radius: 4px;
            background-color: #FFFFFF;
            selection-background-color: #DBEAFE;
            selection-color: #1E293B;
            padding: 4px;
        }}

        QPushButton#convertBtn {{
            padding: 12px;
            background-color: #2563EB;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
        }}

        QPushButton#convertBtn:hover {{
            background-color: #1D4ED8;
        }}

        QPushButton#convertBtn:pressed {{
            background-color: #1E40AF;
        }}

        QPushButton#convertBtn:disabled {{
            background-color: #93C5FD;
        }}

        QPushButton#swapBtn {{
            padding: 8px 16px;
            background-color: #EFF6FF;
            color: #2563EB;
            border: 2px solid #BFDBFE;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
        }}

        QPushButton#swapBtn:hover {{
            background-color: #DBEAFE;
        }}

        QPushButton#langBtn {{
            padding: 6px 14px;
            background-color: transparent;
            color: #2563EB;
            border: 1px solid #BFDBFE;
            border-radius: 6px;
            font-size: 12px;
        }}

        QPushButton#langBtn:hover {{
            background-color: #EFF6FF;
        }}

        QFrame#resultFrame {{
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 10px;
            padding: 16px;
        }}
    """

#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request

from src.core.converter import CurrencyConverter
from src.core.currencies import CURRENCIES, POPULAR_CURRENCIES

app = Flask(__name__)
converter = CurrencyConverter()


@app.route("/")
def index():
    ordered = []
    for code in POPULAR_CURRENCIES:
        if code in CURRENCIES:
            ordered.append({"code": code, **CURRENCIES[code]})
    for code in sorted(CURRENCIES.keys()):
        if code not in POPULAR_CURRENCIES:
            ordered.append({"code": code, **CURRENCIES[code]})
    return render_template("index.html", currencies=ordered)


@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json()
    amount = data.get("amount", 0)
    from_code = data.get("from", "")
    to_code = data.get("to", "")

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "مبلغ باید بزرگتر از صفر باشد"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "مبلغ نامعتبر است"}), 400

    if from_code not in CURRENCIES or to_code not in CURRENCIES:
        return jsonify({"error": "ارز انتخاب‌شده نامعتبر است"}), 400

    try:
        involves_irr = from_code == "IRR" or to_code == "IRR"
        if involves_irr:
            converter.fetch_irr_rates()
            source = "tgju.org"
        else:
            converter.fetch_exchange_rates(from_code)
            source = "ExchangeRate-API"

        result = converter.convert(amount, from_code, to_code)
        rate = converter.get_rate(from_code, to_code)

        return jsonify({
            "result": result,
            "rate": rate,
            "source": source,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

let currentLang = "fa";

const translations = {
    "app_title":     { en: "Currency Converter", fa: "مبدل ارز" },
    "amount_label":  { en: "Amount", fa: "مبلغ" },
    "from_label":    { en: "From", fa: "از ارز" },
    "to_label":      { en: "To", fa: "به ارز" },
    "convert_btn":   { en: "Convert", fa: "تبدیل" },
    "fetching":      { en: "Fetching rates...", fa: "دریافت نرخ‌ها..." },
    "placeholder":   { en: "Enter amount...", fa: "مبلغ را وارد کنید..." },
    "swap_tooltip":  { en: "Swap currencies", fa: "جابجایی ارزها" },
    "lang_switch":   { en: "فارسی", fa: "English" },
    "footer":        { en: "IRR rates from tgju.org, other currencies from ExchangeRate-API",
                       fa: "نرخ ارزهای ریالی از tgju.org و سایر ارزها از ExchangeRate-API" },
    "source_label":  { en: "Source: ", fa: "منبع: " },
    "invalid":       { en: "Please enter a valid amount.", fa: "لطفاً مبلغ معتبر وارد کنید." },
    "error_network": { en: "Network error. Please try again.", fa: "خطای شبکه. لطفاً دوباره تلاش کنید." },
};

function t(key) {
    return translations[key]?.[currentLang] || key;
}

function formatNumber(value) {
    if (value >= 1) return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (value >= 0.01) return value.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 });
    return value.toLocaleString(undefined, { minimumFractionDigits: 6, maximumFractionDigits: 6 });
}

function toggleLanguage() {
    currentLang = currentLang === "fa" ? "en" : "fa";
    applyLanguage();
}

function applyLanguage() {
    const html = document.documentElement;
    html.lang = currentLang;
    html.dir = currentLang === "fa" ? "rtl" : "ltr";

    document.getElementById("app-title").textContent = t("app_title");
    document.getElementById("lang-btn").textContent = t("lang_switch");
    document.getElementById("amount-label").textContent = t("amount_label");
    document.getElementById("amount").placeholder = t("placeholder");
    document.getElementById("from-label").textContent = t("from_label");
    document.getElementById("to-label").textContent = t("to_label");
    document.getElementById("convert-btn").textContent = t("convert_btn");
    document.getElementById("swap-btn").title = t("swap_tooltip");
    document.getElementById("footer-text").textContent = t("footer");

    const fromSelect = document.getElementById("from-currency");
    const toSelect = document.getElementById("to-currency");
    const fromVal = fromSelect.value;
    const toVal = toSelect.value;

    [fromSelect, toSelect].forEach(select => {
        for (let i = 0; i < select.options.length; i++) {
            const code = select.options[i].value;
            const c = CURRENCIES_DATA.find(x => x.code === code);
            if (c) {
                select.options[i].textContent = `${c.flag} ${c.code} - ${c[currentLang]}`;
            }
        }
    });

    fromSelect.value = fromVal;
    toSelect.value = toVal;
}

function swapCurrencies() {
    const from = document.getElementById("from-currency");
    const to = document.getElementById("to-currency");
    const temp = from.value;
    from.value = to.value;
    to.value = temp;
}

async function convert() {
    const amountInput = document.getElementById("amount");
    const amount = parseFloat(amountInput.value);
    const fromCode = document.getElementById("from-currency").value;
    const toCode = document.getElementById("to-currency").value;

    const resultBox = document.getElementById("result-box");
    const errorBox = document.getElementById("error-box");

    resultBox.classList.add("hidden");
    errorBox.classList.add("hidden");

    if (!amount || amount <= 0) {
        errorBox.textContent = t("invalid");
        errorBox.classList.remove("hidden");
        return;
    }

    const btn = document.getElementById("convert-btn");
    btn.disabled = true;
    btn.textContent = t("fetching");

    try {
        const response = await fetch("/api/convert", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount, from: fromCode, to: toCode }),
        });

        const data = await response.json();

        if (!response.ok) {
            errorBox.textContent = data.error || t("error_network");
            errorBox.classList.remove("hidden");
            return;
        }

        document.getElementById("result-amount").textContent =
            `${formatNumber(data.result)} ${toCode}`;
        document.getElementById("result-rate").textContent =
            `1 ${fromCode} = ${formatNumber(data.rate)} ${toCode}`;
        document.getElementById("result-source").textContent =
            t("source_label") + data.source;

        resultBox.classList.remove("hidden");
    } catch (err) {
        errorBox.textContent = t("error_network");
        errorBox.classList.remove("hidden");
    } finally {
        btn.disabled = false;
        btn.textContent = t("convert_btn");
    }
}

document.getElementById("amount").addEventListener("keypress", function(e) {
    if (e.key === "Enter") convert();
});

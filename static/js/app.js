let currentLang = "fa";
let activeDropdown = null;

const translations = {
    "app_title":     { en: "💱 Currency Converter", fa: "💱 مبدل ارز" },
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
    "search":        { en: "Search...", fa: "جستجو..." },
};

function t(key) {
    return translations[key]?.[currentLang] || key;
}

function formatNumber(value) {
    if (value >= 1) return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (value >= 0.01) return value.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 });
    return value.toLocaleString(undefined, { minimumFractionDigits: 6, maximumFractionDigits: 6 });
}

function getCurrency(code) {
    return CURRENCIES_DATA.find(c => c.code === code);
}

function updateSelector(prefix, code) {
    const c = getCurrency(code);
    if (!c) return;
    document.getElementById(prefix + "-currency").value = code;
    document.getElementById(prefix + "-flag").textContent = c.flag;
    document.getElementById(prefix + "-code").textContent = c.code;
    document.getElementById(prefix + "-name").textContent = c[currentLang];
}

function openDropdown(prefix) {
    const dropdown = document.getElementById("currency-dropdown");
    const trigger = document.getElementById(prefix + "-trigger");
    const rect = trigger.getBoundingClientRect();
    const currentCode = document.getElementById(prefix + "-currency").value;

    activeDropdown = prefix;

    dropdown.style.top = (rect.bottom + window.scrollY + 4) + "px";
    dropdown.style.left = rect.left + "px";
    dropdown.style.width = Math.max(rect.width, 260) + "px";

    const search = document.getElementById("dropdown-search");
    search.value = "";
    search.placeholder = t("search");
    renderOptions("");
    dropdown.classList.add("open");

    const activeOpt = dropdown.querySelector(`.currency-option[data-code="${currentCode}"]`);
    if (activeOpt) {
        setTimeout(() => activeOpt.scrollIntoView({ block: "center", behavior: "instant" }), 50);
    }

    setTimeout(() => search.focus(), 100);
}

function closeDropdown() {
    document.getElementById("currency-dropdown").classList.remove("open");
    activeDropdown = null;
}

function renderOptions(filter) {
    const container = document.getElementById("dropdown-options");
    const currentCode = activeDropdown ? document.getElementById(activeDropdown + "-currency").value : "";
    const lowerFilter = filter.toLowerCase();

    let html = "";
    CURRENCIES_DATA.forEach(c => {
        const matchEn = c.en.toLowerCase().includes(lowerFilter);
        const matchFa = c.fa.includes(filter);
        const matchCode = c.code.toLowerCase().includes(lowerFilter);
        if (filter && !matchEn && !matchFa && !matchCode) return;

        const isActive = c.code === currentCode ? " active" : "";
        html += `<div class="currency-option${isActive}" data-code="${c.code}" onclick="selectCurrency('${c.code}')">
            <span class="flag-emoji">${c.flag}</span>
            <span class="opt-code">${c.code}</span>
            <span class="opt-name">${c[currentLang]}</span>
        </div>`;
    });
    container.innerHTML = html;
}

function selectCurrency(code) {
    if (activeDropdown) {
        updateSelector(activeDropdown, code);
    }
    closeDropdown();
}

function toggleLanguage() {
    currentLang = currentLang === "fa" ? "en" : "fa";
    applyLanguage();
}

function applyLanguage() {
    const html = document.documentElement;
    html.lang = currentLang;
    html.dir = currentLang === "fa" ? "rtl" : "ltr";

    document.getElementById("app-title").innerHTML = t("app_title");
    document.getElementById("lang-btn").textContent = t("lang_switch");
    document.getElementById("amount-label").textContent = t("amount_label");
    document.getElementById("amount").placeholder = t("placeholder");
    document.getElementById("from-label").textContent = t("from_label");
    document.getElementById("to-label").textContent = t("to_label");
    document.getElementById("convert-btn").textContent = t("convert_btn");
    document.getElementById("swap-btn").title = t("swap_tooltip");
    document.getElementById("footer-text").textContent = t("footer");

    updateSelector("from", document.getElementById("from-currency").value);
    updateSelector("to", document.getElementById("to-currency").value);
}

function swapCurrencies() {
    const fromCode = document.getElementById("from-currency").value;
    const toCode = document.getElementById("to-currency").value;
    updateSelector("from", toCode);
    updateSelector("to", fromCode);
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

        const fromC = getCurrency(fromCode);
        const toC = getCurrency(toCode);

        document.getElementById("result-flags").textContent =
            `${fromC?.flag || ""} → ${toC?.flag || ""}`;
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

document.getElementById("from-trigger").addEventListener("click", () => openDropdown("from"));
document.getElementById("to-trigger").addEventListener("click", () => openDropdown("to"));

document.getElementById("dropdown-search").addEventListener("input", function() {
    renderOptions(this.value);
});

document.addEventListener("click", function(e) {
    const dropdown = document.getElementById("currency-dropdown");
    if (!dropdown.contains(e.target) &&
        !e.target.closest(".selected-flag")) {
        closeDropdown();
    }
});

document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") closeDropdown();
});

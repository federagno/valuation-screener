# 📊 Valuation Screener

A Streamlit dashboard for equity valuation analysis. Enter any stock ticker and instantly get P/E, EV/EBITDA and P/FCF multiples compared against the sector median, with a visual chart and key financials summary.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Features

- **Live data** : fetches real-time fundamentals via Yahoo Finance (no API key required)
- **3 core multiples** : P/E, EV/EBITDA, P/FCF
- **Sector comparison** : automatically computes the median for ~10 sector peers and benchmarks your ticker against it
- **Valuation signal** : color-coded: 🟢 Undervalued / 🟡 Fair value / 🔴 Overvalued
- **Visual chart** : grouped bar chart (company vs. sector median)
- **Key financials panel** : Market Cap, Revenue, Net Income, Free Cash Flow, Beta
- **Works with international tickers** : e.g. `ENI.MI`, `ASML.AS`, `9984.T`

---

## 🖥️ Demo

```
Ticker: AAPL

P/E:        28.4x   |  Sector median: 31.2x  →  🟢 Undervalued
EV/EBITDA:  22.1x   |  Sector median: 20.8x  →  🟡 Fair value
P/FCF:      26.7x   |  Sector median: 29.4x  →  🟢 Undervalued
```

---

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/valuation-screener.git
cd valuation-screener
pip install -r requirements.txt
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## 🗂️ Project Structure

```
valuation-screener/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🔍 How it works

1. **Data source** : [yfinance](https://github.com/ranaroussi/yfinance) wraps the Yahoo Finance API. No keys, no signup.
2. **Sector peers** : each GICS sector maps to ~10 representative large-caps. The app fetches their multiples and takes the median.
3. **Valuation signals** : a company trades at a discount if its multiple is >15% below the sector median, and at a premium if >20% above.
4. **Caching** : `@st.cache_data(ttl=3600)` keeps API calls efficient; data refreshes every hour.

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. It does not constitute financial advice. Always conduct your own due diligence before making investment decisions.

---

## 👤 Author

**Federico** — Economics & Finance student  
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) · [GitHub](https://github.com/YOUR_USERNAME)

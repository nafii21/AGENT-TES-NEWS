import re, requests
from datetime import datetime, timedelta
from config import FRED_API

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# ---------- FRED API (data terstruktur) ----------
FRED_SERIES = {
    "jobless_claims":  "ICSA",
    "continuing_claims": "CCSA",
    "avg_hourly_earnings": "CES0500000003",
    "core_cpi_lag":    "CPILFESL",
    "shelter_cpi":     "CPIHOSSL",
    "gasoline_weekly": "GASREGW",
    "industrial_production": "INDPRO",
    "retail_sales_trend": "RSAFS",
    "unemployment_rate": "UNRATE",
    "oil_prices":      "DCOILWTICO",
}

def fred_fetch(series_id: str, days_back=21):
    url = "https://api.stlouisfed.org/geofred/series/observations"  # fallback below
    url = (f"https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={series_id}&api_key={FRED_API}&file_type=json"
           f"&sort_order=desc&limit=10")
    try:
        r = requests.get(url, timeout=15)
        obs = r.json().get("observations", [])
        vals = [(o["date"], float(o["value"])) for o in obs
                if o["value"] not in (".", "")]
        return vals  # [(date, value)] newest first
    except Exception:
        return []

def fred_trend(series_id: str, days_back=21):
    """Return (pct_change, latest) atau (None, None)."""
    data = fred_fetch(series_id, days_back)
    if len(data) < 2:
        return None, None
    latest = data[0][1]
    old = min((d for d, v in data if
               d >= (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")),
              default=data[-1][0])
    old_val = dict(data).get(old)
    if not old_val:
        return None, latest
    pct = (latest - old_val) / abs(old_val) * 100
    return pct, latest

# ---------- Web scraping (data non-FRED) ----------
def scrape_adp():
    """ADP employment report preview — dari situs berita."""
    try:
        r = requests.get("https://www.google.com/search?q=ADP+employment+report+actual",
                         headers=UA, timeout=15)
        m = re.search(r"ADP.*?([\d,]+)K", r.text)
        return m.group(1).replace(",", "") + "K" if m else None
    except Exception:
        return None

def scrape_ism():
    try:
        r = requests.get("https://www.ismworld.org/supply-management-news-and-reports/",
                         headers=UA, timeout=15)
        m = re.search(r"PMI.*?(\d\d\.\d)", r.text)
        return float(m.group(1)) if m else None
    except Exception:
        return None

def scrape_umich():
    try:
        r = requests.get("https://data.sca.isr.umich.edu/", headers=UA, timeout=15)
        m = re.search(r"Index.*?(\d\d\.\d)", r.text)
        return float(m.group(1)) if m else None
    except Exception:
        return None

def collect_all():
    """Kumpulkan semua indikator → dict {key: {"pct": x, "val": y, "src": "fred"}}"""
    out = {}
    for key, sid in FRED_SERIES.items():
        pct, val = fred_trend(sid)
        if pct is not None:
            out[key] = {"pct": round(pct, 3), "val": val, "src": f"FRED:{sid}"}
    # scraping tambahan
    for key, fn in [("adp_payrolls", scrape_adp),
                    ("ism_current", scrape_ism),
                    ("consumer_sentiment", scrape_umich)]:
        v = fn()
        if v is not None:
            out[key] = {"val": v, "src": "scrape"}
    return out

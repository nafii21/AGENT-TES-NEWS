EVENT_KB = {
    "non-farm": {
        "nama": "Non-Farm Employment Change",
        "komponen": {
            "jobless_claims":      {"bobot": 0.25, "arah": "inv"},
            "adp_payrolls":        {"bobot": 0.20, "arah": "dir"},
            "ism_manuf_emp":       {"bobot": 0.15, "arah": "dir"},
            "ism_services_emp":    {"bobot": 0.15, "arah": "dir"},
            "challenger_layoffs":  {"bobot": 0.10, "arah": "inv"},
            "avg_hourly_earnings": {"bobot": 0.15, "arah": "dir"},
        },
        "mekanisme": ("NFP tinggi = ekonomi kuat = Fed hawkish = USD naik. "
                      "Klaim awal mingguan adalah proxy terbaik NFP."),
    },
    "cpi": {
        "nama": "CPI y/y",
        "komponen": {
            "gasoline_weekly": {"bobot": 0.25, "arah": "dir"},
            "shelter_cpi":     {"bobot": 0.25, "arah": "dir"},
            "used_cars":       {"bobot": 0.10, "arah": "dir"},
            "airfare":         {"bobot": 0.05, "arah": "dir"},
            "food_commodity":  {"bobot": 0.10, "arah": "dir"},
            "pipeline_ppi":    {"bobot": 0.15, "arah": "dir"},
            "import_prices":   {"bobot": 0.10, "arah": "dir"},
        },
        "mekanisme": ("CPI tinggi = Fed hawkish = USD naik. "
                      "Shelter + bensin = driver terbesar headline CPI."),
    },
    "unemployment claims": {
        "nama": "Unemployment Claims",
        "komponen": {
            "continuing_claims": {"bobot": 0.30, "arah": "inv"},
            "claims_4wk_avg":    {"bobot": 0.25, "arah": "inv"},
            "layoff_news":       {"bobot": 0.15, "arah": "inv"},
            "seasonal_factor":   {"bobot": 0.10, "arah": "none"},
            "fed_speak_tone":    {"bobot": 0.20, "arah": "none"},
        },
        "mekanisme": ("Claims naik = pasar kerja melemah = Fed dovish = "
                      "USD turun. Waspada noise musiman/holiday."),
    },
    "ism manufacturing": {
        "nama": "ISM Manufacturing PMI",
        "komponen": {
            "emp_manuf_bls":    {"bobot": 0.20, "arah": "dir"},
            "philly_fed":       {"bobot": 0.20, "arah": "dir"},
            "empire_state":     {"bobot": 0.15, "arah": "dir"},
            "durable_orders":   {"bobot": 0.15, "arah": "dir"},
            "oil_prices_input": {"bobot": 0.10, "arah": "dir"},
            "chicago_pmi":      {"bobot": 0.20, "arah": "dir"},
        },
        "mekanisme": ("PMI > 50 = ekspansi = USD positif. Regional Fed "
                      "surveys adalah proxy langsung."),
    },
    "ism services": {
        "nama": "ISM Services PMI",
        "komponen": {
            "emp_services_bls":     {"bobot": 0.20, "arah": "dir"},
            "ism_manuf_lag":        {"bobot": 0.10, "arah": "dir"},
            "consumer_spending":    {"bobot": 0.20, "arah": "dir"},
            "retail_sales_proxy":   {"bobot": 0.20, "arah": "dir"},
            "jobless_claims_trend": {"bobot": 0.30, "arah": "inv"},
        },
        "mekanisme": "Sektor jasa = 80% ekonomi AS. PMI > 50 = USD positif.",
    },
    "retail sales": {
        "nama": "Retail Sales m/m",
        "komponen": {
            "gasoline_retail":    {"bobot": 0.20, "arah": "dir"},
            "auto_sales":         {"bobot": 0.25, "arah": "dir"},
            "ecommerce_trend":    {"bobot": 0.15, "arah": "dir"},
            "consumer_sentiment": {"bobot": 0.20, "arah": "dir"},
            "holiday_shopping":   {"bobot": 0.20, "arah": "dir"},
        },
        "mekanisme": "Konsumsi = 70% PDB. Angka kuat = USD naik.",
    },
    "fomc": {
        "nama": "FOMC Interest Rate Decision",
        "komponen": {
            "core_pce_trend":     {"bobot": 0.30, "arah": "dir"},
            "unemployment_trend": {"bobot": 0.30, "arah": "inv"},
            "core_cpi_trend":     {"bobot": 0.25, "arah": "dir"},
            "gdp_now":            {"bobot": 0.15, "arah": "dir"},
        },
        "mekanisme": ("Hawkish = USD naik, dovish = USD turun. "
                      "90% kasus = maintain (INLINE)."),
    },
    "gdp": {
        "nama": "GDP q/q",
        "komponen": {
            "retail_sales_trend":   {"bobot": 0.25, "arah": "dir"},
            "industrial_production":{"bobot": 0.20, "arah": "dir"},
            "trade_balance":        {"bobot": 0.15, "arah": "dir"},
            "housing_starts":       {"bobot": 0.15, "arah": "dir"},
            "philly_empire_avg":    {"bobot": 0.25, "arah": "dir"},
        },
        "mekanisme": "GDP kuat = USD positif. Advance release sering sudah diprice-in.",
    },
    "core pce": {
        "nama": "Core PCE Price Index m/m",
        "komponen": {
            "core_cpi_lag":     {"bobot": 0.35, "arah": "dir"},
            "shelter_cpi":      {"bobot": 0.20, "arah": "dir"},
            "pipeline_ppi":     {"bobot": 0.20, "arah": "dir"},
            "medical_services": {"bobot": 0.10, "arah": "dir"},
            "supercore_wage":   {"bobot": 0.15, "arah": "dir"},
        },
        "mekanisme": ("PCE = inflasi favorit Fed. Korelasi sangat tinggi "
                      "dengan core CPI bulan yang sama."),
    },
    "crude oil inventories": {
        "nama": "Crude Oil Inventories",
        "komponen": {
            "cushing_level":    {"bobot": 0.25, "arah": "inv"},
            "refinery_runs":    {"bobot": 0.20, "arah": "inv"},
            "oil_price_trend":  {"bobot": 0.20, "arah": "dir"},
            "production_trend": {"bobot": 0.20, "arah": "dir"},
            "import_trend":     {"bobot": 0.15, "arah": "dir"},
        },
        "mekanisme": "Draw = demand kuat. Dampak USD kontekstual.",
    },
}

def get_knowledge(title: str):
    t = title.lower()
    for key, kb in EVENT_KB.items():
        if key in t:
            return key, kb
    return None, None

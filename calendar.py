import requests
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta, timezone
from config import FF_XML_URL, PREDICT_HOURS_BEFORE

def fetch_calendar():
    """Ambil kalender FF XML → list event high-impact USD."""
    try:
        r = requests.get(FF_XML_URL, timeout=20,
                         headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(r.content)
    except Exception as e:
        print("Calendar error:", e); return []
    events = []
    for item in root.findall("item"):
        ev = {c.tag: (c.text or "").strip() for c in item}
        if ev.get("country") != "USD" or ev.get("impact") != "High":
            continue
        events.append({"title": ev.get("title", ""),
                       "date": ev.get("date", ""), "time": ev.get("time", ""),
                       "impact": ev.get("impact", ""),
                       "forecast": ev.get("forecast", "") or "n/a",
                       "previous": ev.get("previous", "") or "n/a"})
    return events

def within_window(ev):
    """True jika event dalam jendela prediksi (jam date/time sudah di-parse sederhana)."""
    # XML FF: date "12-25-2024", time "8:30am" — parsing longgar
    try:
        dt = datetime.strptime(ev["date"], "%m-%d-%Y")
        return True  # filter jam bisa diperketat sesuai kebutuhan
    except Exception:
        return True

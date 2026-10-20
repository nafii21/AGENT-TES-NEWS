from datetime import datetime
from database import init_db, save_prediction, get_pending, settle, get_stats
from data_sources import collect_all
from quant_scorer import score_event
from ai_predictor import ai_decide
from ff_calendar import fetch_calendar, within_window
from telegram_bot import send, format_prediction, format_accuracy_report

def run_predictor():
    print(f"[{datetime.utcnow():%H:%M}] === RUN PREDICTOR ===")
    events = [e for e in fetch_calendar() if within_window(e)]
    indicators = collect_all()
    print(f"Event high-impact: {len(events)} | Indikator: {len(indicators)}")
    for ev in events:
        q = score_event(ev["title"], indicators)
        if not q:
            print(f"  skip (no KB): {ev['title']}"); continue
        ai = ai_decide(ev, q, ev["forecast"], ev["previous"])
        save_prediction(ev, q, ai)
        send(format_prediction(ev, q, ai))
        print(f"  ✓ {ev['title']} → {ai['prediksi']} ({ai['confidence']}%)")

def run_reconcile():
    """Cek event yang sudah rilis di XML minggu ini → update actual & verdict."""
    print("=== RECONCILE ===")
    events = {e["title"]: e for e in fetch_calendar()}
    for row in get_pending():
        ev = events.get(row["event_title"])
        if not ev or ev["forecast"] == "n/a":
            continue
        # event dianggap sudah rilis kalau "previous" sudah terisi nilai baru
        # (di XML live, setelah rilis: previous = forecast lama, actual masuk)
        actual = ev.get("previous")
        if not actual or actual == row["previous"]:
            continue
        verdict = "BENAR" if row["prediksi"] == "INLINE" or \
                  (row["prediksi"] == "BEAT" and actual > row["forecast"]) or \
                  (row["prediksi"] == "MISS" and actual < row["forecast"]) \
                  else "SALAH"
        settle(row["id"], actual, verdict)
        print(f"  ✓ settled: {row['event_title']} actual={actual} → {verdict}")
    stats = get_stats()
    if stats["total"]:
        send(format_accuracy_report(stats))
        print("  stats:", stats)

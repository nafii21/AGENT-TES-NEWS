import time
from datetime import datetime
from database import init_db, save_prediction, get_pending, settle
from data_sources import collect_all
from quant_scorer import score_event
from ai_predictor import ai_decide
from calendar import fetch_calendar, within_window
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
    """Bandingkan prediksi vs actual. Verdict sederhana: cocok/tidak."""
    print("=== RECONCILE ===")
    for row in get_pending():
        # actual belum tersedia di XML historis — verdict manual/placeholder
        print(f"  pending: {row['event_title']}")
    # Contoh stats
    stats = {"total": 0, "benar": 0, "pct": 0, "beat": 0, "miss": 0, "inline": 0}
    # send(format_accuracy_report(stats)) — aktifkan saat sudah ada data actual

if __name__ == "__main__":
    init_db()
    while True:
        try:
            run_predictor()
            run_reconcile()
        except Exception as e:
            print("ERROR:", e)
        time.sleep(3600)  # tiap 1 jam

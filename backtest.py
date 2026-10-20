"""
BACKTEST — prediksi news masa lalu TANPA lihat actual.
Actual HANYA dipakai setelah prediksi selesai, untuk ngukur akurasi.

Cara pakai:
  1. Isi data historis di backtest_events.csv (lihat format di bawah)
  2. Run: python backtest.py
  3. Hasil: tabel akurasi di terminal + laporan ke Telegram

Format backtest_events.csv (judul harus match dengan knowledge_base.py):
title,date,forecast,previous,actual
Non-Farm Payrolls,2025-01-10,160K,212K,256K
CPI y/y,2025-01-15,2.9%,2.7%,2.9%
"""
import csv
import os
from datetime import datetime
from config import DB_PATH
from knowledge_base import KNOWLEDGE
from ai_predictor import ai_decide
from quant_scorer import score_event
from telegram_bot import send

CSV_FILE = "backtest_events.csv"


def load_events():
    if not os.path.exists(CSV_FILE):
        print(f"❌ File {CSV_FILE} tidak ada. Buat dulu, format:")
        print("title,date,forecast,previous,actual")
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("title")]
    print(f"Loaded {len(rows)} event historis dari {CSV_FILE}")
    return rows


def predict_without_actual(event):
    """Prediksi PAKAI data pre-release saja — actual tidak di-pass ke AI."""
    ev = {
        "title":    event["title"],
        "date":     event["date"],
        "time":     "-",
        "impact":   "High",
        "forecast": event["forecast"],
        "previous": event["previous"],
    }
    q = score_event(ev["title"], {})  # quant dari knowledge base
    if not q:
        return None
    # ai_decide hanya menerima ev (forecast/previous), quant, dan konteks
    # → TIDAK menerima event["actual"]
    return ai_decide(ev, q, ev["forecast"], ev["previous"])


def judge(prediksi, forecast, actual):
    """Bandingkan prediksi vs actual — dipanggil SETELAH prediksi."""
    try:
        f = float(forecast.replace("%", "").replace("K", "").replace("M", ""))
        a = float(actual.replace("%", "").replace("K", "").replace("M", ""))
    except (ValueError, AttributeError):
        return "SKIP"
    if prediksi == "INLINE":
        return abs(a - f) / abs(f) < 0.15 if f else abs(a - f) < 0.1
    if prediksi == "BEAT":
        return a > f
    if prediksi == "MISS":
        return a < f
    return False


def run_backtest():
    print("=" * 50)
    print("        BACKTEST FF AI PREDICTOR")
    print("=" * 50)
    events = load_events()
    if not events:
        return

    results = []
    for ev in events:
        ai = predict_without_actual(ev)
        if not ai:
            print(f"  ⚠️ skip (no KB): {ev['title']}")
            continue
        ok = judge(ai["prediksi"], ev["forecast"], ev["actual"])
        results.append({"ev": ev, "ai": ai, "ok": ok})
        mark = "✅" if ok else "❌"
        print(f"  {mark} {ev['date']} {ev['title']:<30} "
              f"pred={ai['prediksi']:<6} conf={ai['confidence']}% | "
              f"fc={ev['forecast']} act={ev['actual']}")

    # ── Ringkasan ──
    scored = [r for r in results if r["ok"] != "SKIP"]
    total = len(scored)
    benar = sum(1 for r in scored if r["ok"])
    pct = round(benar / total * 100) if total else 0
    print("-" * 50)
    print(f"  TOTAL: {total} | BENAR: {benar} | AKURASI: {pct}%")

    per_type = {}
    for r in scored:
        per_type.setdefault(r["ai"]["prediksi"], []).append(r["ok"])
    for p, oks in per_type.items():
        b = sum(1 for x in oks if x)
        print(f"  {p:<7}: {b}/{len(oks)} benar")

    # ── Kirim ke Telegram ──
    lines = [f"🔬 <b>HASIL BACKTEST</b>",
             f"Total: {total} | Benar: {benar} | <b>Akurasi: {pct}%</b>", ""]
    for r in results:
        mark = "✅" if r["ok"] else "❌"
        lines.append(f"{mark} {r['ev']['title']}: pred {r['ai']['prediksi']} "
                     f"→ fc {r['ev']['forecast']} vs act {r['ev']['actual']}")
    send("\n".join(lines))


if __name__ == "__main__":
    run_backtest()

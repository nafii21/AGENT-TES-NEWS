"""
BACKTEST — prediksi news masa lalu TANPA lihat actual.
Actual HANYA dipakai setelah prediksi selesai, untuk ngukur akurasi.

Cara pakai:
  1. Isi data historis di backtest_events.csv
  2. Run: python backtest.py (atau via GitHub Actions workflow "Backtest")
  3. Hasil: tabel akurasi di log + laporan ke Telegram
"""
import csv
import os

# ── Import knowledge base secara defensif ──
# Tidak peduli variabelnya bernama KNOWLEDGE / KB / DATABASE, otomatis kedetect.
import knowledge_base as kb
from ai_predictor import ai_decide
from quant_scorer import score_event
from telegram_bot import send

KNOWLEDGE = (
    getattr(kb, "KNOWLEDGE", None)
    or getattr(kb, "KB", None)
    or getattr(kb, "DATABASE", None)
    or getattr(kb, "KNOWLEDGE_BASE", None)
)

CSV_FILE = "backtest_events.csv"


def load_events():
    """Load data historis dari CSV."""
    if not os.path.exists(CSV_FILE):
        print(f"❌ File {CSV_FILE} tidak ada. Format:")
        print("title,date,forecast,previous,actual")
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("title") and r.get("actual")]
    print(f"✅ Loaded {len(rows)} event historis dari {CSV_FILE}")
    return rows


def title_in_kb(title):
    """Cek judul event ada di knowledge base (aman walau KB None / bentuk apapun)."""
    if not KNOWLEDGE:
        return False
    try:
        titles = KNOWLEDGE.keys() if isinstance(KNOWLEDGE, dict) else KNOWLEDGE
        t = title.lower()
        return any(t in str(k).lower() or str(k).lower() in t for k in titles)
    except Exception:
        return False


def predict_without_actual(event):
    """
    Prediksi PAKAI data pre-release saja.
    event['actual'] SENGAJA tidak di-pass ke AI — biar tidak bocor.
    """
    ev = {
        "title":    event["title"],
        "date":     event["date"],
        "time":     "-",
        "impact":   "High",
        "forecast": event.get("forecast", ""),
        "previous": event.get("previous", ""),
    }

    # Quant score — kalau gagal, lanjut dengan dict kosong
    try:
        q = score_event(ev["title"], {}) or {}
    except Exception as e:
        print(f"  ⚠️ quant score gagal utk '{ev['title']}': {e}")
        q = {}

    # Kalau judul tidak dikenali knowledge base → skip
    if not q and not title_in_kb(ev["title"]):
        print(f"  ⚠️ skip (tidak ada di KB): {ev['title']}")
        return None

    try:
        return ai_decide(ev, q, ev["forecast"], ev["previous"])
    except Exception as e:
        print(f"  ⚠️ AI gagal utk '{ev['title']}': {e}")
        return None


def to_number(text):
    """'2.9%' / '160K' / '12K' → float."""
    if text is None:
        return None
    t = str(text).strip().replace("%", "").replace("K", "").replace("M", "").replace(",", "")
    try:
        return float(t)
    except ValueError:
        return None


def judge(prediksi, forecast, actual):
    """Bandingkan prediksi vs actual — dipanggil SETELAH prediksi."""
    f = to_number(forecast)
    a = to_number(actual)
    if f is None or a is None:
        return "SKIP"

    if prediksi == "INLINE":
        # toleransi 15% dari forecast (atau 0.1 kalau forecast ~ 0)
        return abs(a - f) / abs(f) < 0.15 if f != 0 else abs(a - f) < 0.1
    if prediksi == "BEAT":
        return a > f
    if prediksi == "MISS":
        return a < f
    return False


def run_backtest():
    print("=" * 50)
    print("        BACKTEST FF AI PREDICTOR")
    print("=" * 50)

    if KNOWLEDGE is None:
        print("  ⚠️ WARNING: knowledge base tidak terdeteksi — semua event non-quant akan di-skip")
    else:
        print("  ✅ Knowledge base terdeteksi")

    events = load_events()
    if not events:
        print("❌ Tidak ada event untuk di-backtest.")
        return

    results = []
    for ev in events:
        ai = predict_without_actual(ev)
        if not ai:
            continue
        ok = judge(ai.get("prediksi"), ev["forecast"], ev["actual"])
        results.append({"ev": ev, "ai": ai, "ok": ok})
        mark = "✅" if ok is True else ("❌" if ok is False else "⏭️")
        print(f"  {mark} {ev['date']} {ev['title']:<28} "
              f"pred={ai.get('prediksi', '?'):<7} conf={ai.get('confidence', '?')}% | "
              f"fc={ev['forecast']} act={ev['actual']}")

    # ── Ringkasan ──
    scored = [r for r in results if r["ok"] != "SKIP"]
    total = len(scored)
    benar = sum(1 for r in scored if r["ok"] is True)
    pct = round(benar / total * 100) if total else 0

    print("-" * 50)
    print(f"  TOTAL: {total} | BENAR: {benar} | AKURASI: {pct}%")

    per_type = {}
    for r in scored:
        per_type.setdefault(r["ai"].get("prediksi", "?"), []).append(r["ok"])
    for p, oks in per_type.items():
        b = sum(1 for x in oks if x is True)
        print(f"  {p:<7}: {b}/{len(oks)} benar")

    # ── Kirim ke Telegram ──
    try:
        lines = [
            "🔬 <b>HASIL BACKTEST</b>",
            f"Total: {total} | Benar: {benar} | <b>Akurasi: {pct}%</b>",
            "",
        ]
        for r in results:
            mark = "✅" if r["ok"] is True else ("❌" if r["ok"] is False else "⏭️")
            lines.append(
                f"{mark} {r['ev']['title']}: pred {r['ai'].get('prediksi', '?')} "
                f"(conf {r['ai'].get('confidence', '?')}%) → "
                f"fc {r['ev']['forecast']} vs act {r['ev']['actual']}"
            )
        send("\n".join(lines))
    except Exception as e:
        print(f"  ⚠️ Gagal kirim ke Telegram: {e}")

    print("✅ Backtest selesai.")


if __name__ == "__main__":
    run_backtest()

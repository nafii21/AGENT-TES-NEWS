import requests
from config import TG_URL

ICONS = {"BEAT": "🟢", "MISS": "🔴", "INLINE": "🟡"}

def send(text: str):
    try:
        requests.post(TG_URL, data={"chat_id": CHAT_ID, "text": text,
                      "parse_mode": "HTML"}, timeout=15)
    except Exception as e:
        print("Telegram error:", e)

def format_prediction(event, quant, ai):
    cov = int(quant["coverage"] * 100)
    lines = [
        f"{ICONS.get(ai['prediksi'],'⚪')} <b>PREDIKSI: {ai['prediksi']}</b> "
        f"({ai['confidence']}%)",
        f"📊 <b>{event['title']}</b>",
        f"🕒 {event['date']} | Impact: {event['impact']}",
        f"🎯 Forecast: {event['forecast']} | Prev: {event['previous']}",
        f"🧮 Quant score: {quant['skor']} (coverage {cov}%)",
        f"💡 {ai['alasan']}",
    ]
    return "\n".join(lines)

def format_accuracy_report(stats):
    return (f"📈 <b>LAPORAN AKURASI</b>\n"
            f"Total settled: {stats['total']}\n"
            f"Benar: {stats['benar']} ({stats['pct']}%)\n"
            f"BEAT: {stats['beat']} | MISS: {stats['miss']} | INLINE: {stats['inline']}")

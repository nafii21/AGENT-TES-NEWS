import json, requests
from config import GROQ_API, MODEL, GROQ_URL
from quant_scorer import skor_to_bias

PROMPT = """Anda adalah ekonom makro senior yang memprediksi rilis data AS.
Gunakan HANYA logika ekonomi dari data yang diberikan. Jangan mengarang data.

EVENT: {nama}
FORECAST: {forecast} | PREVIOUS: {previous}
QUANT SCORE (weighted-sign model): {skor} → bias: {bias}
COVERAGE data leading: {coverage}

Rincian komponen:
{detail}

MEKANISME EKONOMI (pegangan):
{mekanisme}

Analisis, lalu jawab FINAL dengan format JSON persis:
{{"prediksi": "BEAT|MISS|INLINE", "confidence": 0-100,
  "estimasi_arah": "lebih tinggi|lebih rendah|sesuai forecast",
  "alasan": "maks 3 kalimat bahasa Indonesia"}}"""

def ai_decide(event, quant_result, forecast, previous):
    detail_str = "\n".join(
        f"- {d['komponen']}: {d.get('pct','?')}% ({d['status']}) "
        f"kontribusi {d['kontribusi']}" for d in quant_result["detail"])
    prompt = PROMPT.format(
        nama=event["title"], forecast=forecast, previous=previous,
        skor=quant_result["skor"], bias=skor_to_bias(quant_result["skor"]),
        coverage=f'{int(quant_result["coverage"]*100)}%',
        detail=detail_str, mekanisme=quant_result["mekanisme"])
    try:
        r = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API}",
                     "Content-Type": "application/json"},
            json={"model": MODEL,
                  "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.2, "max_tokens": 400},
            timeout=30)
        txt = r.json()["choices"][0]["message"]["content"]
        m = json.loads(txt[txt.find("{"): txt.rfind("}")+1])
        return m
    except Exception as e:
        return {"prediksi": "INLINE", "confidence": 30,
                "estimasi_arah": "sesuai forecast",
                "alasan": f"AI error: {e}"}

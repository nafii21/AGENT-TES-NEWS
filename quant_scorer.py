from knowledge_base import get_knowledge

def score_event(event_title: str, indicators: dict):
    """Hitung weighted-sign score. Return dict hasil, None jika event tidak dikenal."""
    key, kb = get_knowledge(event_title)
    if not kb:
        return None

    skor, detail, total_bobot = 0.0, [], 0.0
    for comp, spec in kb["komponen"].items():
        bobot, arah = spec["bobot"], spec["arah"]
        total_bobot += bobot
        data = indicators.get(comp)
        if not data or data.get("pct") is None:
            detail.append({"komponen": comp, "status": "NODATA",
                           "bobot": bobot, "kontribusi": 0.0})
            continue
        pct = data["pct"]
        s = pct * bobot * (1 if arah == "dir" else -1)
        skor += s
        detail.append({"komponen": comp, "pct": pct, "arah": arah,
                       "bobot": bobot, "kontribusi": round(s, 3),
                       "status": "OK", "src": data.get("src")})

    coverage = (total_bobot - sum(d["bobot"] for d in detail
                 if d["status"] == "NODATA")) / total_bobot
    return {"event_key": key, "nama": kb["nama"],
            "skor": round(skor, 3), "coverage": round(coverage, 2),
            "detail": detail, "mekanisme": kb["mekanisme"]}

def skor_to_bias(skor: float):
    """Skor → arah bias untuk prompt AI."""
    if skor > 0.15:  return "BEAT-leaning (data leading mengarah ke angka lebih kuat dari forecast)"
    if skor < -0.15: return "MISS-leaning (data leading mengarah ke angka lebih lemah dari forecast)"
    return "INLINE (data leading netral, kemungkinan sesuai forecast)"

import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, event_title TEXT, event_time TEXT,
        forecast TEXT, previous TEXT,
        quant_score REAL, coverage REAL,
        prediksi TEXT, confidence REAL, alasan TEXT,
        actual TEXT, verdict TEXT, settled_at TEXT)""")
    con.commit(); con.close()

def save_prediction(event, quant, ai):
    con = sqlite3.connect(DB_PATH)
    con.execute("INSERT INTO predictions (ts,event_title,event_time,forecast,"
        "previous,quant_score,coverage,prediksi,confidence,alasan) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (datetime.utcnow().isoformat(),
         event["title"], event["date"] + " " + event["time"],
         event["forecast"], event["previous"],
         quant["skor"], quant["coverage"], ai["prediksi"],
         ai["confidence"], ai["alasan"]))
    con.commit(); con.close()

def get_pending():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM predictions WHERE actual IS NULL").fetchall()
    con.close(); return [dict(r) for r in rows]

def settle(pid, actual, verdict):
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE predictions SET actual=?, verdict=?, settled_at=? WHERE id=?",
                (actual, verdict, datetime.utcnow().isoformat(), pid))
    con.commit(); con.close()

def get_stats():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    rows = con.execute("SELECT prediksi, verdict FROM predictions WHERE verdict IS NOT NULL").fetchall()
    con.close()
    total = len(rows)
    benar = sum(1 for r in rows if r["verdict"] == "BENAR")
    return {"total": total, "benar": benar,
            "pct": round(benar/total*100) if total else 0,
            "beat": sum(1 for r in rows if r["prediksi"] == "BEAT"),
            "miss": sum(1 for r in rows if r["prediksi"] == "MISS"),
            "inline": sum(1 for r in rows if r["prediksi"] == "INLINE")}

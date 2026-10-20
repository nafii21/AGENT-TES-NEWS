import sqlite3, json
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
        (json.dumps(datetime.utcnow().isoformat()) if False else datetime.utcnow().isoformat(),
         event["title"], event["date"], event["forecast"], event["previous"],
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

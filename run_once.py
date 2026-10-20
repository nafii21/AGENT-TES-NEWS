from database import init_db
from main import run_predictor, run_reconcile

init_db()
run_reconcile()   # settle dulu event lama
run_predictor()   # prediksi event baru

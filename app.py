# app.py (핵심만)
from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://skr-orthox.github.io"}})  # 본인 Pages 도메인

def get_price(ticker: str):
    t = yf.Ticker(ticker)
    try:
        df = t.history(period="1d", interval="1m", prepost=True)
        if not df.empty:
            return float(df["Close"].dropna().iloc[-1])
    except: pass
    try:
        df = t.history(period="5d", interval="1d")
        if not df.empty:
            return float(df["Close"].dropna().iloc[-1])
    except: pass
    fi = getattr(t, "fast_info", None)
    if fi and fi.get("last_price") is not None:
        return float(fi["last_price"])
    return None

@app.get("/quote")
def quote():
    raw = (request.args.get("code") or "").strip()
    if not raw:
        return jsonify({"error":"code parameter required"}), 400
    # 한국 6자리 자동 판별
    candidates = [raw] if not (raw.isdigit() and len(raw)==6) else [raw+".KS", raw+".KQ"]
    for tk in candidates:
        price = get_price(tk)
        if price is not None:
            return jsonify({"ticker": tk, "price": price})
    return jsonify({"error":"ticker not found"}), 404

# 배포 시 Start command: gunicorn app:app

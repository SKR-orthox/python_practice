from flask import Flask, render_template, request
import yfinance as yf

app = Flask(__name__)

def get_current_price_any(ticker_code: str):
    """
    사용자가 넣은 문자열을 티커로 간주하고 현재가(가장 최근 종가에 가까운 값)를 반환.
    - 1분봉(당일) → 5일 일봉 → fast_info 순으로 시도
    - 실패 시 None 반환
    """
    t = yf.Ticker(ticker_code)

    # 1) 당일 1분봉
    try:
        df = t.history(period="1d", interval="1m", prepost=True)
        if not df.empty and "Close" in df.columns:
            last_close = df["Close"].dropna()
            if not last_close.empty:
                # 타임스탬프도 같이 반환(표시용)
                ts = df.index[-1].to_pydatetime()
                return float(last_close.iloc[-1]), ts
    except Exception:
        pass

    # 2) 최근 5일 일봉
    try:
        df = t.history(period="5d", interval="1d")
        if not df.empty and "Close" in df.columns:
            last_close = df["Close"].dropna()
            if not last_close.empty:
                ts = df.index[-1].to_pydatetime()
                return float(last_close.iloc[-1]), ts
    except Exception:
        pass

    # 3) fast_info
    try:
        fi = getattr(t, "fast_info", None)
        if fi:
            lp = fi.get("last_price")
            if lp is not None:
                return float(lp), None
    except Exception:
        pass

    return None, None


def resolve_korean_code(code6: str):
    """
    6자리 한국 종목코드를 넣으면 .KS → .KQ 순서로 시도하여 성공한 티커 문자열을 돌려준다.
    둘 다 실패하면 None.
    """
    for suffix in (".KS", ".KQ"):
        ticker = code6 + suffix
        price, ts = get_current_price_any(ticker)
        if price is not None:
            return ticker, price, ts
    return None, None, None


@app.route("/", methods=["GET", "POST"])
def index():
    price, ts, final_ticker, error = None, None, None, None

    if request.method == "POST":
        raw = (request.form.get("code") or "").strip()

        if not raw:
            error = "티커(또는 6자리 한국 종목코드)를 입력하세요."
        else:
            # 6자리 숫자면 한국 코드로 가정해 자동 판별
            if raw.isdigit() and len(raw) == 6:
                final_ticker, price, ts = resolve_korean_code(raw)
                if final_ticker is None:
                    error = "코스피(.KS)/코스닥(.KQ) 어디에서도 찾지 못했습니다. 코드를 확인하세요."
            else:
                # 사용자가 직접 티커(AAPL, 7203.T 등)를 넣은 경우
                final_ticker = raw
                price, ts = get_current_price_any(final_ticker)
                if price is None:
                    error = "주가 정보를 불러오지 못했습니다. 티커를 확인하세요."

    return render_template("index.html",
                           price=price,
                           ts=ts,
                           final_ticker=final_ticker,
                           error=error)


if __name__ == "__main__":
    # 개발용 로컬 실행
    app.run(host="0.0.0.0", port=5000, debug=True)

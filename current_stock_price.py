import yfinance as yf

def get_current_price(code6: str):
    """
    한국 주식 6자리 코드를 입력하면 현재가(지연된 종가)를 반환.
    예: '005930' → 삼성전자
    """
    suffixes = [".KS", ".KQ"]  # 코스피, 코스닥 순서로 확인
    for suffix in suffixes:
        ticker = yf.Ticker(code6 + suffix)
        try:
            # 오늘 하루치 1분 간격 데이터 시도
            df = ticker.history(period="1d", interval="1m", prepost=True)
            if not df.empty and "Close" in df.columns:
                return float(df["Close"].iloc[-1])
        except Exception:
            pass

        # fallback: 최근 5일 일봉
        try:
            df = ticker.history(period="5d", interval="1d")
            if not df.empty and "Close" in df.columns:
                return float(df["Close"].iloc[-1])
        except Exception:
            pass

    return None  # 둘 다 실패한 경우


if __name__ == "__main__":
    code = input("조회할 주식번호(6자리): ").strip()
    price = get_current_price(code)
    if price is not None:
        print(f"{code}의 현재가는 {price:,.2f} 원입니다.")
    else:
        print("주가 정보를 불러오지 못했습니다. 코드나 시장을 확인하세요.")

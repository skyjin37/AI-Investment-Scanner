import pandas as pd
import yfinance as yf

df = pd.read_excel("data/watchlist.xlsx")

print("=" * 60)
print("오늘의 관심종목 현재가 + 52주 신고가 + 이동평균선")
print("=" * 60)

for _, row in df.iterrows():
    name = row["종목명"]
    ticker = row["티커"]
    sector = row["섹터"]

    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    price = hist["Close"].iloc[-1]
    high_52w = hist["High"].max()
    gap = (price - high_52w) / high_52w * 100
    flag = "🔥 신고가 근접" if gap >= -3 else ""

    # 이동평균선 계산 (최근 20/60/120일 종가 평균)
    ma20 = hist["Close"].rolling(20).mean().iloc[-1]
    ma60 = hist["Close"].rolling(60).mean().iloc[-1]
    ma120 = hist["Close"].rolling(120).mean().iloc[-1]

    # 정배열 여부 (단기>중기>장기 순으로 쌓여있는지)
    if ma20 > ma60 > ma120:
        arrangement = "✅ 정배열"
    elif ma20 < ma60 < ma120:
        arrangement = "❌ 역배열"
    else:
        arrangement = "🔄 혼조"

    print(f"[{sector}] {name} ({ticker})")
    print(f"   현재가: {price:,.2f}  |  52주 최고가: {high_52w:,.2f}  |  고점대비: {gap:+.2f}%  {flag}")
    print(f"   MA20: {ma20:,.2f}  |  MA60: {ma60:,.2f}  |  MA120: {ma120:,.2f}  |  {arrangement}")
    print("-" * 60)

print("=" * 60)
import pandas as pd
import yfinance as yf


def calculate_rsi(close_prices, period=14):
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


df = pd.read_excel("data/watchlist.xlsx")

print("=" * 60)
print("오늘의 관심종목 종합 분석 (현재가/52주/이평선/거래량/RSI)")
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

    ma20 = hist["Close"].rolling(20).mean().iloc[-1]
    ma60 = hist["Close"].rolling(60).mean().iloc[-1]
    ma120 = hist["Close"].rolling(120).mean().iloc[-1]

    if ma20 > ma60 > ma120:
        arrangement = "✅ 정배열"
    elif ma20 < ma60 < ma120:
        arrangement = "❌ 역배열"
    else:
        arrangement = "🔄 혼조"

    volume_today = hist["Volume"].iloc[-1]
    volume_avg20 = hist["Volume"].rolling(20).mean().iloc[-2]
    volume_ratio = volume_today / volume_avg20

    if volume_ratio >= 2:
        volume_flag = f"🚀 거래량 급증 ({volume_ratio:.1f}배)"
    elif volume_ratio >= 1.5:
        volume_flag = f"📈 거래량 증가 ({volume_ratio:.1f}배)"
    else:
        volume_flag = f"평상시 ({volume_ratio:.1f}배)"

    rsi = calculate_rsi(hist["Close"]).iloc[-1]
    if rsi >= 70:
        rsi_flag = "⚠️ 과매수"
    elif rsi <= 30:
        rsi_flag = "💡 과매도"
    else:
        rsi_flag = "보통"

    print(f"[{sector}] {name} ({ticker})")
    print(f"   현재가: {price:,.2f}  |  52주 최고가: {high_52w:,.2f}  |  고점대비: {gap:+.2f}%  {flag}")
    print(f"   MA20: {ma20:,.2f}  |  MA60: {ma60:,.2f}  |  MA120: {ma120:,.2f}  |  {arrangement}")
    print(f"   거래량: {volume_flag}")
    print(f"   RSI(14): {rsi:.1f}  {rsi_flag}")
    print("-" * 60)

print("=" * 60)
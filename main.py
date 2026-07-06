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


def calculate_macd(close_prices, short=12, long=26, signal=9):
    ema_short = close_prices.ewm(span=short, adjust=False).mean()
    ema_long = close_prices.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line


def calculate_ichimoku(hist):
    high = hist["High"]
    low = hist["Low"]

    # 전환선: 최근 9일 고가/저가 평균
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    # 기준선: 최근 26일 고가/저가 평균
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    # 선행스팬1: (전환선+기준선)/2, 26일 앞으로 이동
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    # 선행스팬2: 최근 52일 고가/저가 평균, 26일 앞으로 이동
    senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)

    return tenkan, kijun, senkou_a, senkou_b


df = pd.read_excel("data/watchlist.xlsx")

results = []

print("=" * 60)
print("오늘의 관심종목 종합 분석")
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

    # ---- MACD ----
    macd, signal_line = calculate_macd(hist["Close"])
    macd_today, signal_today = macd.iloc[-1], signal_line.iloc[-1]
    macd_yesterday, signal_yesterday = macd.iloc[-2], signal_line.iloc[-2]

    if macd_yesterday <= signal_yesterday and macd_today > signal_today:
        macd_flag = "✨ 골든크로스 발생"
    elif macd_today > signal_today:
        macd_flag = "🟢 상승 국면 (MACD>Signal)"
    else:
        macd_flag = "🔴 하락 국면 (MACD<Signal)"

    # ---- 일목균형표 ----
    tenkan, kijun, senkou_a, senkou_b = calculate_ichimoku(hist)
    cloud_top = max(senkou_a.iloc[-1], senkou_b.iloc[-1])
    cloud_bottom = min(senkou_a.iloc[-1], senkou_b.iloc[-1])

    if price > cloud_top:
        cloud_flag = "☀️ 구름 위 (상승추세)"
    elif price < cloud_bottom:
        cloud_flag = "🌧️ 구름 아래 (하락추세)"
    else:
        cloud_flag = "☁️ 구름 안 (혼조)"

    # ---- 점수 계산 ----
    score = 0
    if gap >= -3:
        score += 20
    if arrangement == "✅ 정배열":
        score += 20
    if volume_ratio >= 2:
        score += 15
    elif volume_ratio >= 1.5:
        score += 8
    if 40 <= rsi <= 60:
        score += 10
    elif rsi <= 30:
        score += 8
    if macd_flag == "✨ 골든크로스 발생":
        score += 15
    elif macd_flag == "🟢 상승 국면 (MACD>Signal)":
        score += 8
    if cloud_flag == "☀️ 구름 위 (상승추세)":
        score += 12

    results.append({
        "종목명": name, "티커": ticker, "섹터": sector,
        "점수": score,
    })

    print(f"[{sector}] {name} ({ticker})")
    print(f"   현재가: {price:,.2f}  |  52주 최고가: {high_52w:,.2f}  |  고점대비: {gap:+.2f}%  {flag}")
    print(f"   MA20: {ma20:,.2f}  |  MA60: {ma60:,.2f}  |  MA120: {ma120:,.2f}  |  {arrangement}")
    print(f"   거래량: {volume_flag}")
    print(f"   RSI(14): {rsi:.1f}  {rsi_flag}")
    print(f"   MACD: {macd_flag}")
    print(f"   일목균형표: {cloud_flag}")
    print(f"   👉 종합 점수: {score}점")
    print("-" * 60)

print("=" * 60)

result_df = pd.DataFrame(results).sort_values("점수", ascending=False)

print("\n📊 오늘의 관심종목 랭킹 (점수 높은 순)")
print("=" * 60)
for i, r in enumerate(result_df.itertuples(), start=1):
    print(f"{i}위. {r.종목명} ({r.티커})  -  {r.점수}점  [{r.섹터}]")
print("=" * 60)
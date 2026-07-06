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

results = []  # 종목별 결과를 담아둘 리스트

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

    # ---- 점수 계산 ----
    score = 0
    if gap >= -3:
        score += 30              # 52주 신고가 근접
    if arrangement == "✅ 정배열":
        score += 25              # 이동평균선 정배열
    if volume_ratio >= 2:
        score += 20              # 거래량 급증
    elif volume_ratio >= 1.5:
        score += 10              # 거래량 증가
    if 40 <= rsi <= 60:
        score += 15              # RSI 안정 구간 (추세 초입 가능성)
    elif rsi <= 30:
        score += 10              # 과매도(반등 기대)

    results.append({
        "종목명": name, "티커": ticker, "섹터": sector,
        "현재가": price, "고점대비": gap, "정배열": arrangement,
        "거래량": volume_flag, "RSI": rsi, "점수": score,
    })

    print(f"[{sector}] {name} ({ticker})")
    print(f"   현재가: {price:,.2f}  |  52주 최고가: {high_52w:,.2f}  |  고점대비: {gap:+.2f}%  {flag}")
    print(f"   MA20: {ma20:,.2f}  |  MA60: {ma60:,.2f}  |  MA120: {ma120:,.2f}  |  {arrangement}")
    print(f"   거래량: {volume_flag}")
    print(f"   RSI(14): {rsi:.1f}  {rsi_flag}")
    print(f"   👉 종합 점수: {score}점")
    print("-" * 60)

print("=" * 60)

# ---- 점수순 랭킹 출력 ----
result_df = pd.DataFrame(results).sort_values("점수", ascending=False)

print("\n📊 오늘의 관심종목 랭킹 (점수 높은 순)")
print("=" * 60)
for i, r in enumerate(result_df.itertuples(), start=1):
    print(f"{i}위. {r.종목명} ({r.티커})  -  {r.점수}점  [{r.섹터}]")
print("=" * 60)
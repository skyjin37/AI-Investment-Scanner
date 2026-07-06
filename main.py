import pandas as pd
import yfinance as yf
import os
from datetime import datetime


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

    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)

    return tenkan, kijun, senkou_a, senkou_b


df = pd.read_excel("data/watchlist.xlsx")

results = []

print("종목 데이터 분석 중...")

for _, row in df.iterrows():
    name = row["종목명"]
    ticker = row["티커"]
    sector = row["섹터"]

    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    price = hist["Close"].iloc[-1]
    high_52w = hist["High"].max()
    gap = (price - high_52w) / high_52w * 100
    near_high = gap >= -3

    ma20 = hist["Close"].rolling(20).mean().iloc[-1]
    ma60 = hist["Close"].rolling(60).mean().iloc[-1]
    ma120 = hist["Close"].rolling(120).mean().iloc[-1]

    if ma20 > ma60 > ma120:
        arrangement = "정배열"
    elif ma20 < ma60 < ma120:
        arrangement = "역배열"
    else:
        arrangement = "혼조"

    volume_today = hist["Volume"].iloc[-1]
    volume_avg20 = hist["Volume"].rolling(20).mean().iloc[-2]
    volume_ratio = volume_today / volume_avg20

    rsi = calculate_rsi(hist["Close"]).iloc[-1]

    macd, signal_line = calculate_macd(hist["Close"])
    macd_today, signal_today = macd.iloc[-1], signal_line.iloc[-1]
    macd_yesterday, signal_yesterday = macd.iloc[-2], signal_line.iloc[-2]

    if macd_yesterday <= signal_yesterday and macd_today > signal_today:
        macd_flag = "골든크로스"
    elif macd_today > signal_today:
        macd_flag = "상승국면"
    else:
        macd_flag = "하락국면"

    tenkan, kijun, senkou_a, senkou_b = calculate_ichimoku(hist)
    cloud_top = max(senkou_a.iloc[-1], senkou_b.iloc[-1])
    cloud_bottom = min(senkou_a.iloc[-1], senkou_b.iloc[-1])

    if price > cloud_top:
        cloud_flag = "구름 위"
    elif price < cloud_bottom:
        cloud_flag = "구름 아래"
    else:
        cloud_flag = "구름 안"

    score = 0
    if near_high:
        score += 20
    if arrangement == "정배열":
        score += 20
    if volume_ratio >= 2:
        score += 15
    elif volume_ratio >= 1.5:
        score += 8
    if 40 <= rsi <= 60:
        score += 10
    elif rsi <= 30:
        score += 8
    if macd_flag == "골든크로스":
        score += 15
    elif macd_flag == "상승국면":
        score += 8
    if cloud_flag == "구름 위":
        score += 12

    results.append({
        "종목명": name, "티커": ticker, "섹터": sector,
        "현재가": price, "52주최고가": high_52w, "고점대비": gap,
        "정배열": arrangement, "거래량배수": volume_ratio,
        "RSI": rsi, "MACD": macd_flag, "일목균형표": cloud_flag,
        "점수": score,
    })

result_df = pd.DataFrame(results).sort_values("점수", ascending=False)

# ---- HTML 생성 ----
today = datetime.now().strftime("%Y-%m-%d")

rows_html = ""
for i, r in enumerate(result_df.itertuples(), start=1):
    # 점수에 따라 색상 다르게
    if r.점수 >= 40:
        badge_color = "#2ecc71"  # 초록
    elif r.점수 >= 20:
        badge_color = "#f39c12"  # 주황
    else:
        badge_color = "#95a5a6"  # 회색

    rows_html += f"""
    <tr>
        <td>{i}</td>
        <td><b>{r.종목명}</b><br><span class="ticker">{r.티커}</span></td>
        <td>{r.섹터}</td>
        <td>{r.현재가:,.2f}</td>
        <td>{r.고점대비:+.2f}%</td>
        <td>{r.정배열}</td>
        <td>{r.거래량배수:.1f}배</td>
        <td>{r.RSI:.1f}</td>
        <td>{r.MACD}</td>
        <td>{r.일목균형표}</td>
        <td><span class="badge" style="background:{badge_color}">{r.점수}점</span></td>
    </tr>
    """

html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>AI Investment Scanner - {today}</title>
<style>
    body {{ font-family: 'Malgun Gothic', sans-serif; background: #1e1e1e; color: #eee; padding: 30px; }}
    h1 {{ color: #4fc3f7; }}
    .date {{ color: #999; margin-bottom: 20px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th, td {{ padding: 10px 12px; text-align: center; border-bottom: 1px solid #444; }}
    th {{ background: #2c2c2c; color: #4fc3f7; }}
    tr:hover {{ background: #2a2a2a; }}
    .ticker {{ color: #888; font-size: 12px; }}
    .badge {{ padding: 4px 10px; border-radius: 12px; color: white; font-weight: bold; }}
</style>
</head>
<body>
    <h1>📊 AI Investment Scanner</h1>
    <div class="date">기준일: {today}</div>
    <table>
        <tr>
            <th>순위</th><th>종목</th><th>섹터</th><th>현재가</th><th>52주고점대비</th>
            <th>이평선</th><th>거래량</th><th>RSI</th><th>MACD</th><th>일목균형표</th><th>점수</th>
        </tr>
        {rows_html}
    </table>
</body>
</html>
"""

os.makedirs("reports", exist_ok=True)
filepath = f"reports/report_{today}.html"

with open(filepath, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n✅ HTML 리포트 저장 완료: {filepath}")
print("파일을 더블클릭해서 브라우저로 열어보세요!")
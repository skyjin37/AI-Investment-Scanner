import pandas as pd
import yfinance as yf

# 엑셀에서 관심종목 불러오기
df = pd.read_excel("data/watchlist.xlsx")

print("=" * 50)
print("오늘의 관심종목 현재가")
print("=" * 50)

for _, row in df.iterrows():
    name = row["종목명"]
    ticker = row["티커"]
    sector = row["섹터"]

    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")["Close"].iloc[-1]

    print(f"[{sector}] {name} ({ticker}): {price:,.2f}")

print("=" * 50)
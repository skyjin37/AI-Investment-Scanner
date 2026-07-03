import yfinance as yf

# 관심종목 리스트 (일단 몇 개만 테스트)
# 미국 주식은 티커 그대로, 한국 주식은 종목코드 뒤에 .KS를 붙입니다
watchlist = {
    "Cisco (미국)": "CSCO",
    "LS ELECTRIC (한국)": "010120.KS",
    "삼성전자 (한국)": "005930.KS",
}

print("=" * 40)
print("오늘의 관심종목 현재가")
print("=" * 40)

for name, ticker in watchlist.items():
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")["Close"].iloc[-1]
    print(f"{name} ({ticker}): {price:,.2f}")

print("=" * 40)
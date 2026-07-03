import pandas as pd
import os

os.makedirs("data", exist_ok=True)

data = {
    "종목명": ["Cisco", "LS ELECTRIC", "삼성전자", "HD현대일렉트릭", "Vertiv"],
    "티커": ["CSCO", "010120.KS", "005930.KS", "267260.KS", "VRT"],
    "섹터": ["AI 네트워크", "전력", "반도체", "전력", "냉각/데이터센터"],
}

df = pd.DataFrame(data)
df.to_excel("data/watchlist.xlsx", index=False)

print("watchlist.xlsx 생성 완료!")
print(df)
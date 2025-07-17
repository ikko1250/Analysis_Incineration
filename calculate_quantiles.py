
import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('/home/ubuntu/cur/program/Analyisis_incineration/2022_1焼却施設.csv')

# '年間処理量_t/年度' 列を数値に変換し、無効な値をNaNにする
df['年間処理量_t/年度'] = pd.to_numeric(df['年間処理量_t/年度'], errors='coerce')

# NaNと0のデータを除外
df.dropna(subset=['年間処理量_t/年度'], inplace=True)
df = df[df['年間処理量_t/年度'] > 0]

# 3分位の境界値を計算
quantiles = df['年間処理量_t/年度'].quantile([1/3, 2/3])

# 結果の表示
print("年間処理量_t/年度の3分位点:")
print(f"下位1/3 (33.3パーセンタイル): {quantiles[1/3]:.2f} t/年度")
print(f"上位1/3 (66.7パーセンタイル): {quantiles[2/3]:.2f} t/年度")

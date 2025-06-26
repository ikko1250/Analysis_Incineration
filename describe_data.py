import pandas as pd

# CSVファイルを読み込み
df = pd.read_csv('/home/ubuntu/cur/program/Analyisis_incineration/2022_1焼却施設.csv', encoding='utf-8')

# 発電効率のカラム（インデックス40）
power_efficiency_col = df.iloc[:, 40]
print("発電能力_発電効率（仕様値・公称値）_％ の統計情報:")
print(f"カラム名: {df.columns[40]}")
print(f"データ型: {power_efficiency_col.dtype}")

# 数値に変換（エラーは無視してNaNにする）
power_efficiency_numeric = pd.to_numeric(power_efficiency_col, errors='coerce')

print(f"\n基本統計:")
print(f"総データ数: {len(power_efficiency_numeric)}")
print(f"有効データ数（非NaN）: {power_efficiency_numeric.notna().sum()}")
print(f"欠損値数: {power_efficiency_numeric.isna().sum()}")

# 有効データのみで統計計算
valid_data = power_efficiency_numeric.dropna()

if len(valid_data) > 0:
    print(f"\n発電効率の統計（有効データのみ）:")
    print(f"平均値: {valid_data.mean():.2f}%")
    print(f"中央値: {valid_data.median():.2f}%")
    print(f"標準偏差: {valid_data.std():.2f}%")
    print(f"最小値: {valid_data.min():.2f}%")
    print(f"最大値: {valid_data.max():.2f}%")
    print(f"25%分位: {valid_data.quantile(0.25):.2f}%")
    print(f"75%分位: {valid_data.quantile(0.75):.2f}%")
    
    print(f"\n発電効率の範囲別分布:")
    print(f"10%未満: {(valid_data < 10).sum()} 施設")
    print(f"10-15%: {((valid_data >= 10) & (valid_data < 15)).sum()} 施設")
    print(f"15-20%: {((valid_data >= 15) & (valid_data < 20)).sum()} 施設")
    print(f"20-25%: {((valid_data >= 20) & (valid_data < 25)).sum()} 施設")
    print(f"25%以上: {(valid_data >= 25).sum()} 施設")
    
    # 発電効率が10%未満の施設一覧
    low_efficiency_mask = power_efficiency_numeric < 10
    low_efficiency_facilities = df[low_efficiency_mask & power_efficiency_numeric.notna()]
    
    print(f"\n=== 発電効率が10%未満の焼却場一覧 ===")
    print(f"該当施設数: {len(low_efficiency_facilities)}")
    
    if len(low_efficiency_facilities) > 0:
        for i, (idx, row) in enumerate(low_efficiency_facilities.iterrows(), 1):
            prefecture = row.iloc[0]  # 都道府県名
            municipality = row.iloc[3]  # 地方公共団体名
            facility_name = row.iloc[4]  # 施設名称
            start_year = row.iloc[26]  # 使用開始年度
            efficiency = power_efficiency_numeric.iloc[idx]
            
            print(f"{i:2d}. {prefecture} {municipality} - {facility_name}")
            print(f"    発電効率: {efficiency:.2f}% | 使用開始年度: {start_year}")
            print()
else:
    print("有効なデータがありません")
import pandas as pd

# CSVファイルを読み込み
df = pd.read_csv('/home/ubuntu/cur/program/Analyisis_incineration/2022_1焼却施設.csv', encoding='utf-8')

# 発電能力のカラム（インデックス39）
power_capacity_col = df.iloc[:, 39]
print("発電能力_発電能力_kW の統計情報:")
print(f"カラム名: {df.columns[39]}")
print(f"データ型: {power_capacity_col.dtype}")

# 数値に変換（エラーは無視してNaNにする）
power_capacity_numeric = pd.to_numeric(power_capacity_col, errors='coerce')

print(f"\n基本統計:")
print(f"総データ数: {len(power_capacity_numeric)}")
print(f"有効データ数（非NaN）: {power_capacity_numeric.notna().sum()}")
print(f"欠損値数: {power_capacity_numeric.isna().sum()}")

# 有効データのみで統計計算
valid_data = power_capacity_numeric.dropna()

if len(valid_data) > 0:
    print(f"\n発電能力の統計（有効データのみ）:")
    print(f"平均値: {valid_data.mean():.2f} kW")
    print(f"中央値: {valid_data.median():.2f} kW")
    print(f"標準偏差: {valid_data.std():.2f} kW")
    print(f"最小値: {valid_data.min():.2f} kW")
    print(f"最大値: {valid_data.max():.2f} kW")
    print(f"25%分位: {valid_data.quantile(0.25):.2f} kW")
    print(f"75%分位: {valid_data.quantile(0.75):.2f} kW")
    
    print(f"\n発電能力の範囲別分布:")
    print(f"1,000kW未満: {(valid_data < 1000).sum()} 施設")
    print(f"1,000-3,000kW: {((valid_data >= 1000) & (valid_data < 3000)).sum()} 施設")
    print(f"3,000-5,000kW: {((valid_data >= 3000) & (valid_data < 5000)).sum()} 施設")
    print(f"5,000-10,000kW: {((valid_data >= 5000) & (valid_data < 10000)).sum()} 施設")
    print(f"10,000kW以上: {(valid_data >= 10000).sum()} 施設")
    
    # 発電能力が4000kW～6000kWの施設
    capacity_range_mask = (power_capacity_numeric >= 4000) & (power_capacity_numeric <= 6000) & power_capacity_numeric.notna()
    capacity_range_facilities = df[capacity_range_mask].copy()
    capacity_range_facilities['power_capacity'] = power_capacity_numeric[capacity_range_mask]
    capacity_range_facilities = capacity_range_facilities.sort_values('power_capacity', ascending=False)
    
    print(f"\n=== 発電能力4000kW～6000kWの施設一覧 ===")
    print(f"該当施設数: {len(capacity_range_facilities)}")
    
    if len(capacity_range_facilities) > 0:
        for i, (idx, row) in enumerate(capacity_range_facilities.iterrows(), 1):
            prefecture = row.iloc[0]  # 都道+府県名
            municipality = row.iloc[3]  # 地方公共団体名
            facility_name = row.iloc[4]  # 施設名称
            annual_treatment = row.iloc[5]  # 年間処理量_t/年度
            start_year = row.iloc[26]  # 使用開始年度
            capacity = row['power_capacity']
            
            print(f"{i:2d}. {prefecture} {municipality} - {facility_name}")
            print(f"    発電能力: {capacity:,.0f} kW | 年間処理量: {annual_treatment:,.0f} t/年 | 使用開始年度: {start_year}")
            print()
else:
    print("有効なデータがありません")
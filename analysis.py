import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# 日本語フォントの設定
mpl.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 12

# CSVファイルを読み込み
df = pd.read_csv('/home/ubuntu/cur/univ7/ゼミナール/2022_1焼却施設.csv', encoding='utf-8')

print("データの形状:", df.shape)
print("\nカラム名:")
for i, col in enumerate(df.columns):
    print(f"{i+1}: {col}")

# 必要なカラムのインデックスを確認
# 2022年データの正しいカラムのインデックス
print("\n年間処理量のカラム:", df.columns[5])     # 年間処理量_t/年度 (6列目、インデックス5)
print("低位発熱量のカラム:", df.columns[94])      # 低位発熱量_(計算値)_kJ/kg (95列目、インデックス94)
print("余熱利用量のカラム:", df.columns[37])      # 余熱利用量（実績値）_余熱利用量_MJ (38列目、インデックス37)

# データの一部を表示
print("\n最初の5行のデータ:")
print(df.iloc[:5, [5, 37, 94]])

# データの型を確認
print("\nデータ型:")
print("年間処理量:", df.iloc[:, 5].dtype)
print("余熱利用量:", df.iloc[:, 37].dtype)  
print("低位発熱量:", df.iloc[:, 94].dtype)

# 欠損値の確認
print("\n欠損値の数:")
print("年間処理量:", df.iloc[:, 5].isnull().sum())
print("余熱利用量:", df.iloc[:, 37].isnull().sum())
print("低位発熱量:", df.iloc[:, 94].isnull().sum())

# 必要なデータを抽出
annual_treatment = df.iloc[:, 5]  # 年間処理量_t/年度
heat_utilization = df.iloc[:, 37]  # 余熱利用量（実績値）_余熱利用量_MJ
low_heat_value_calc = df.iloc[:, 94]   # 低位発熱量_(計算値)_kJ/kg
low_heat_value_measured = df.iloc[:, 95]   # 低位発熱量_(実測値)_kJ/kg

# 余熱利用量の数値変換（文字列の場合）
heat_utilization = pd.to_numeric(heat_utilization, errors='coerce')

# 低位発熱量の選択ロジック: 実測値を優先し、なければ計算値を使用
# ただし、両方とも0またはNaNの場合は除外
low_heat_value = low_heat_value_measured.copy()
mask_use_calc = (low_heat_value_measured.isnull()) | (low_heat_value_measured <= 0)
low_heat_value[mask_use_calc] = low_heat_value_calc[mask_use_calc]

print(f"\n=== 低位発熱量の修正結果 ===")
print(f"実測値を使用: {(~mask_use_calc).sum()} 施設")
print(f"計算値を使用: {mask_use_calc.sum()} 施設")
print(f"有効な低位発熱量: {(low_heat_value > 0).sum()} 施設")
print(f"無効な低位発熱量 (0またはNaN): {((low_heat_value <= 0) | low_heat_value.isnull()).sum()} 施設")

# 年間発熱量の計算: 年間処理量(t) × 低位発熱量(kJ/kg) × 1000 (kg/t)
# 結果はMJに変換: ÷1000
annual_heat = annual_treatment * low_heat_value * 1000 / 1000  # MJ

# 利用率の計算: 余熱利用量 / 年間発熱量
utilization_rate = heat_utilization / annual_heat

# 有効なデータのみを抽出（欠損値を除く）
valid_mask = ~(annual_treatment.isnull() | heat_utilization.isnull() | 
               low_heat_value.isnull() | (annual_treatment == 0) | 
               (low_heat_value <= 0) | (annual_heat == 0))

# 低位発熱量の外れ値除去（1.5σ基準）
valid_low_heat_value = low_heat_value[valid_mask]
heat_value_mean = valid_low_heat_value.mean()
heat_value_std = valid_low_heat_value.std()
heat_value_outlier_mask = (valid_low_heat_value >= heat_value_mean - 1.5*heat_value_std) & (valid_low_heat_value <= heat_value_mean + 1.5*heat_value_std)

print(f"\n=== 低位発熱量の外れ値除去 ===")
print(f"低位発熱量の平均: {heat_value_mean:.2f} kJ/kg")
print(f"低位発熱量の標準偏差: {heat_value_std:.2f} kJ/kg")
print(f"除去基準範囲: {heat_value_mean - 1.5*heat_value_std:.2f} - {heat_value_mean + 1.5*heat_value_std:.2f} kJ/kg")
print(f"低位発熱量外れ値除去前: {len(valid_low_heat_value)} 施設")
print(f"低位発熱量外れ値除去後: {heat_value_outlier_mask.sum()} 施設")
print(f"低位発熱量外れ値として除去: {len(valid_low_heat_value) - heat_value_outlier_mask.sum()} 施設")

# valid_maskを低位発熱量の外れ値除去結果で更新
temp_valid_indices = valid_mask[valid_mask].index
low_heat_outlier_indices = temp_valid_indices[heat_value_outlier_mask]
valid_mask_updated = pd.Series(False, index=valid_mask.index)
valid_mask_updated[low_heat_outlier_indices] = True
valid_mask = valid_mask_updated

print(f"\n低位発熱量外れ値除去後の有効データ数: {valid_mask.sum()}")

# 有効なデータのみを抽出
valid_annual_heat = annual_heat[valid_mask]
valid_utilization_rate = utilization_rate[valid_mask]
valid_heat_utilization = heat_utilization[valid_mask]
valid_low_heat_final = low_heat_value[valid_mask]

print(f"年間発熱量の範囲: {valid_annual_heat.min():.2e} - {valid_annual_heat.max():.2e} MJ")
print(f"利用率の範囲: {valid_utilization_rate.min():.4f} - {valid_utilization_rate.max():.4f}")
print(f"低位発熱量の範囲: {valid_low_heat_final.min():.2f} - {valid_low_heat_final.max():.2f} kJ/kg")

# 追加の外れ値の排除（1.5σ基準）- 年間発熱量と利用率
# 年間発熱量の外れ値排除
heat_mean = valid_annual_heat.mean()
heat_std = valid_annual_heat.std()
heat_outlier_mask = (valid_annual_heat >= heat_mean - 1.5*heat_std) & (valid_annual_heat <= heat_mean + 1.5*heat_std)

# 利用率の外れ値排除
rate_mean = valid_utilization_rate.mean()
rate_std = valid_utilization_rate.std()
rate_outlier_mask = (valid_utilization_rate >= rate_mean - 1.5*rate_std) & (valid_utilization_rate <= rate_mean + 1.5*rate_std)

# 両方の条件を満たすデータのみを抽出
outlier_removed_mask = heat_outlier_mask & rate_outlier_mask

# 外れ値除去後のデータ
filtered_annual_heat = valid_annual_heat[outlier_removed_mask]
filtered_utilization_rate = valid_utilization_rate[outlier_removed_mask]
filtered_heat_utilization = valid_heat_utilization[outlier_removed_mask]

print(f"\n年間発熱量・利用率の外れ値除去前のデータ数: {len(valid_annual_heat)}")
print(f"年間発熱量・利用率の外れ値除去後のデータ数: {len(filtered_annual_heat)}")
print(f"除去されたデータ数: {len(valid_annual_heat) - len(filtered_annual_heat)}")

# 外れ値除去後の低位発熱量も取得
filtered_low_heat_value = valid_low_heat_final[outlier_removed_mask]

print(f"\n最終的な外れ値除去後の範囲:")
print(f"  年間発熱量: {filtered_annual_heat.min():.2e} - {filtered_annual_heat.max():.2e} MJ")
print(f"  利用率: {filtered_utilization_rate.min():.4f} - {filtered_utilization_rate.max():.4f}")
print(f"  低位発熱量: {filtered_low_heat_value.min():.2f} - {filtered_low_heat_value.max():.2f} kJ/kg")

# プロット作成（外れ値除去前と除去後を比較）
plt.figure(figsize=(16, 12))

# 外れ値除去前の散布図
plt.subplot(3, 2, 1)
plt.scatter(valid_annual_heat, valid_utilization_rate, alpha=0.6, color='red', label='All data')
plt.xlabel('Annual Heat Generation (MJ)')
plt.ylabel('Utilization Rate')
plt.title('Before Outlier Removal')
plt.grid(True, alpha=0.3)
plt.legend()

# 外れ値除去後の散布図
plt.subplot(3, 2, 2)
plt.scatter(filtered_annual_heat, filtered_utilization_rate, alpha=0.6, color='blue', label='Filtered data')
plt.xlabel('Annual Heat Generation (MJ)')
plt.ylabel('Utilization Rate')
plt.title('After Outlier Removal (1.5σ)')
plt.grid(True, alpha=0.3)
plt.legend()

# 外れ値除去前の対数スケール
plt.subplot(3, 2, 3)
plt.scatter(valid_annual_heat, valid_utilization_rate, alpha=0.6, color='red')
plt.xlabel('Annual Heat Generation (MJ)')
plt.ylabel('Utilization Rate')
plt.title('Before Outlier Removal (Log Scale)')
plt.xscale('log')
plt.grid(True, alpha=0.3)

# 外れ値除去後の対数スケール
plt.subplot(3, 2, 4)
plt.scatter(filtered_annual_heat, filtered_utilization_rate, alpha=0.6, color='blue')
plt.xlabel('Annual Heat Generation (MJ)')
plt.ylabel('Utilization Rate')
plt.title('After Outlier Removal (Log Scale)')
plt.xscale('log')
plt.grid(True, alpha=0.3)

# 年間発熱量のヒストグラム比較
plt.subplot(3, 2, 5)
plt.hist(valid_annual_heat, bins=30, alpha=0.5, color='red', label='Before', edgecolor='black')
plt.hist(filtered_annual_heat, bins=30, alpha=0.5, color='blue', label='After', edgecolor='black')
plt.xlabel('Annual Heat Generation (MJ)')
plt.ylabel('Frequency')
plt.title('Heat Generation Distribution')
plt.legend()
plt.grid(True, alpha=0.3)

# 利用率のヒストグラム（After のみ）
plt.subplot(3, 2, 6)
plt.hist(filtered_utilization_rate, bins=30, alpha=0.7, color='blue', edgecolor='black')
plt.xlabel('Utilization Rate')
plt.ylabel('Frequency')
plt.title('Utilization Rate Distribution (After Outlier Removal)')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/ubuntu/cur/univ7/ゼミナール/heat_utilization_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# 計算結果をCSVファイルに出力（外れ値除去前）
valid_indices = valid_mask[valid_mask].index

output_df_all = pd.DataFrame({
    '都道府県名': df.iloc[valid_indices, 0].values,
    '地方公共団体名': df.iloc[valid_indices, 3].values, 
    '施設名称': df.iloc[valid_indices, 4].values,
    '年間処理量_t': df.iloc[valid_indices, 5].values,
    '低位発熱量_kJ_per_kg': valid_low_heat_final.values,
    '年間発熱量_MJ': valid_annual_heat.values,
    '余熱利用量_MJ': valid_heat_utilization.values,
    '余熱利用率': valid_utilization_rate.values
})

# 外れ値除去後のデータをCSVファイルに出力
filtered_indices = valid_indices[outlier_removed_mask]

output_df_filtered = pd.DataFrame({
    '都道府県名': df.iloc[filtered_indices, 0].values,
    '地方公共団体名': df.iloc[filtered_indices, 3].values, 
    '施設名称': df.iloc[filtered_indices, 4].values,
    '年間処理量_t': df.iloc[filtered_indices, 5].values,
    '低位発熱量_kJ_per_kg': filtered_low_heat_value.values,
    '年間発熱量_MJ': filtered_annual_heat.values,
    '余熱利用量_MJ': filtered_heat_utilization.values,
    '余熱利用率': filtered_utilization_rate.values
})

# CSVファイルに出力
output_csv_path_all = '/home/ubuntu/cur/univ7/ゼミナール/heat_utilization_results_all.csv'
output_csv_path_filtered = '/home/ubuntu/cur/univ7/ゼミナール/heat_utilization_results_filtered.csv'

output_df_all.to_csv(output_csv_path_all, index=False, encoding='utf-8-sig')
output_df_filtered.to_csv(output_csv_path_filtered, index=False, encoding='utf-8-sig')

print(f"\n全データを {output_csv_path_all} に出力しました。")
print(f"出力データ数: {len(output_df_all)} 件")
print(f"\n外れ値除去後データを {output_csv_path_filtered} に出力しました。")
print(f"出力データ数: {len(output_df_filtered)} 件")

# 統計情報の表示
print("\n=== 外れ値除去前の統計情報 ===")
print(f"年間発熱量 (MJ):")
print(f"  平均: {valid_annual_heat.mean():.2e}")
print(f"  中央値: {valid_annual_heat.median():.2e}")
print(f"  標準偏差: {valid_annual_heat.std():.2e}")

print(f"\n利用率:")
print(f"  平均: {valid_utilization_rate.mean():.4f}")
print(f"  中央値: {valid_utilization_rate.median():.4f}")
print(f"  標準偏差: {valid_utilization_rate.std():.4f}")

print(f"\n余熱利用量 (MJ):")
print(f"  平均: {valid_heat_utilization.mean():.2e}")
print(f"  中央値: {valid_heat_utilization.median():.2e}")
print(f"  標準偏差: {valid_heat_utilization.std():.2e}")

print("\n=== 外れ値除去後の統計情報 ===")
print(f"年間発熱量 (MJ):")
print(f"  平均: {filtered_annual_heat.mean():.2e}")
print(f"  中央値: {filtered_annual_heat.median():.2e}")
print(f"  標準偏差: {filtered_annual_heat.std():.2e}")

print(f"\n利用率:")
print(f"  平均: {filtered_utilization_rate.mean():.4f}")
print(f"  中央値: {filtered_utilization_rate.median():.4f}")
print(f"  標準偏差: {filtered_utilization_rate.std():.4f}")

print(f"\n余熱利用量 (MJ):")
print(f"  平均: {filtered_heat_utilization.mean():.2e}")
print(f"  中央値: {filtered_heat_utilization.median():.2e}")
print(f"  標準偏差: {filtered_heat_utilization.std():.2e}")

# 利用率が1を超える施設の確認
high_utilization_before = valid_utilization_rate > 1.0
high_utilization_after = filtered_utilization_rate > 1.0

print(f"\n利用率が100%を超える施設数:")
print(f"  除去前: {high_utilization_before.sum()}")
print(f"  除去後: {high_utilization_after.sum()}")

if high_utilization_before.sum() > 0:
    print(f"除去前の最大利用率: {valid_utilization_rate.max():.4f}")
if high_utilization_after.sum() > 0:
    print(f"除去後の最大利用率: {filtered_utilization_rate.max():.4f}")

# 余熱利用の状況に関する条件付き確率の算出
print(f"\n=== 余熱利用の状況に関する条件付き確率 ===")

# 関連するカラムを特定
steam_columns = [col for col in df.columns if '場内蒸気' in col]
power_internal_columns = [col for col in df.columns if '発電' in col and '場内利用' in col]
power_external_columns = [col for col in df.columns if '発電' in col and '場外利用' in col]

print(f"場内蒸気関連カラム: {steam_columns}")
print(f"発電(場内利用)関連カラム: {power_internal_columns}")
print(f"発電(場外利用)関連カラム: {power_external_columns}")

if steam_columns and power_internal_columns and power_external_columns:
    # 最初に見つかったカラムを使用
    steam_col = steam_columns[0]
    power_internal_col = power_internal_columns[0]
    power_external_col = power_external_columns[0]
    
    print(f"\n使用するカラム:")
    print(f"  場内蒸気: {steam_col}")
    print(f"  発電(場内利用): {power_internal_col}")
    print(f"  発電(場外利用): {power_external_col}")
    
    # データを取得（欠損値以外の値があるかチェック）
    steam_data = df[steam_col]
    power_internal_data = df[power_internal_col]
    power_external_data = df[power_external_col]
    
    # 場内蒸気に要素がある（非空・非NaN・非ゼロ）条件
    steam_has_value = (~steam_data.isnull()) & (steam_data != '') & (steam_data != 0)
    
    # 発電(場内利用)に要素がある条件
    power_internal_has_value = (~power_internal_data.isnull()) & (power_internal_data != '') & (power_internal_data != 0)
    
    # 発電(場外利用)に要素がある条件
    power_external_has_value = (~power_external_data.isnull()) & (power_external_data != '') & (power_external_data != 0)
    
    # 発電(場内利用)と(場外利用)の両方に要素がある条件
    both_power_has_value = power_internal_has_value & power_external_has_value
    
    # 条件付き確率の計算
    # P(発電場内&場外に要素あり | 場内蒸気に要素あり)
    steam_count = steam_has_value.sum()
    both_power_given_steam_count = (steam_has_value & both_power_has_value).sum()
    
    if steam_count > 0:
        conditional_probability = both_power_given_steam_count / steam_count
        
        print(f"\n=== 結果 ===")
        print(f"場内蒸気に要素がある施設数: {steam_count}")
        print(f"場内蒸気に要素があり、かつ発電(場内利用)と(場外利用)の両方に要素がある施設数: {both_power_given_steam_count}")
        print(f"条件付き確率: {conditional_probability:.4f} ({conditional_probability*100:.2f}%)")
        
        # 参考情報
        print(f"\n=== 参考情報 ===")
        print(f"全施設数: {len(df)}")
        print(f"発電(場内利用)に要素がある施設数: {power_internal_has_value.sum()}")
        print(f"発電(場外利用)に要素がある施設数: {power_external_has_value.sum()}")
        print(f"発電(場内利用)と(場外利用)の両方に要素がある施設数: {both_power_has_value.sum()}")
        
        # データの一部を表示
        print(f"\n=== データ例 ===")
        sample_mask = steam_has_value & both_power_has_value
        if sample_mask.sum() > 0:
            sample_indices = df[sample_mask].index[:5]  # 最初の5件
            for idx in sample_indices:
                print(f"施設名: {df.iloc[idx, 4]}")  # 施設名称は5列目（インデックス4）
                print(f"  場内蒸気: {df.iloc[idx][steam_col]}")
                print(f"  発電(場内利用): {df.iloc[idx][power_internal_col]}")
                print(f"  発電(場外利用): {df.iloc[idx][power_external_col]}")
                print()
    else:
        print("場内蒸気に要素がある施設が見つかりませんでした。")
        
else:
    print("指定されたカラムが見つかりませんでした。")
    print("利用可能なカラム名:")
    for i, col in enumerate(df.columns):
        if any(keyword in col for keyword in ['蒸気', '発電', '利用']):
            print(f"  {i+1}: {col}")

import pandas as pd
import numpy as np
import os

# 設定定数
CONFIG = {
    'input_file': '/home/ubuntu/cur/program/Analyisis_incineration/2022_1焼却施設.csv',
    'output_dir': '/home/ubuntu/cur/program/Analyisis_incineration/result',
    'encoding': 'utf-8',
    'outlier_sigma': 1.5,
    'columns': {
        'prefecture': 0,
        'municipality': 3,
        'facility_name': 4,
        'annual_treatment': 5,
        'heat_utilization': 37,
        'low_heat_calc': 94,
        'low_heat_measured': 95,
        'heat_use_internal_hot_water': 27,
        'heat_use_internal_steam': 28,
        'heat_use_internal_power': 29,
        'heat_use_external_hot_water': 30,
        'heat_use_external_steam': 31,
        'heat_use_external_power': 32
    }
}

def ensure_output_directory(output_dir):
    """出力ディレクトリの存在を確認し、必要に応じて作成"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        return True
    except Exception as e:
        print(f"出力ディレクトリの作成に失敗しました: {e}")
        return False

def remove_outliers(data, sigma_threshold=1.5):
    """外れ値を除去するマスクを返す"""
    mean_val = data.mean()
    std_val = data.std()
    lower_bound = mean_val - sigma_threshold * std_val
    upper_bound = mean_val + sigma_threshold * std_val
    mask = (data >= lower_bound) & (data <= upper_bound)
    
    print(f"平均: {mean_val:.2f}")
    print(f"標準偏差: {std_val:.2f}")
    print(f"除去基準範囲: {lower_bound:.2f} - {upper_bound:.2f}")
    print(f"外れ値除去前: {len(data)} 件")
    print(f"外れ値除去後: {mask.sum()} 件")
    print(f"外れ値として除去: {len(data) - mask.sum()} 件")
    
    return mask

def safe_to_csv(df, filepath, **kwargs):
    """CSVファイルの安全な書き込み"""
    try:
        df.to_csv(filepath, **kwargs)
        print(f"データを {filepath} に出力しました。")
        print(f"出力データ数: {len(df)} 件")
        return True
    except Exception as e:
        print(f"CSV出力に失敗しました: {filepath} - {e}")
        return False

# 出力ディレクトリの確認
if not ensure_output_directory(CONFIG['output_dir']):
    exit(1)

# CSVファイルを読み込み
try:
    df = pd.read_csv(CONFIG['input_file'], encoding=CONFIG['encoding'])
except FileNotFoundError:
    print(f"入力ファイルが見つかりません: {CONFIG['input_file']}")
    exit(1)
except Exception as e:
    print(f"ファイル読み込みエラー: {e}")
    exit(1)

print("データの形状:", df.shape)
print("\nカラム名:")
for i, col in enumerate(df.columns):
    print(f"{i+1}: {col}")

# 必要なカラムのインデックスを確認
print(f"\n年間処理量のカラム: {df.columns[CONFIG['columns']['annual_treatment']]}")
print(f"低位発熱量のカラム: {df.columns[CONFIG['columns']['low_heat_calc']]}")
print(f"余熱利用量のカラム: {df.columns[CONFIG['columns']['heat_utilization']]}")

# データの一部を表示
print("\n最初の5行のデータ:")
print(df.iloc[:5, [CONFIG['columns']['annual_treatment'], CONFIG['columns']['heat_utilization'], CONFIG['columns']['low_heat_calc']]])

# データの型を確認
print("\nデータ型:")
print("年間処理量:", df.iloc[:, CONFIG['columns']['annual_treatment']].dtype)
print("余熱利用量:", df.iloc[:, CONFIG['columns']['heat_utilization']].dtype)
print("低位発熱量:", df.iloc[:, CONFIG['columns']['low_heat_calc']].dtype)

# 欠損値の確認
print("\n欠損値の数:")
print("年間処理量:", df.iloc[:, CONFIG['columns']['annual_treatment']].isnull().sum())
print("余熱利用量:", df.iloc[:, CONFIG['columns']['heat_utilization']].isnull().sum())
print("低位発熱量:", df.iloc[:, CONFIG['columns']['low_heat_calc']].isnull().sum())

# 必要なデータを抽出
annual_treatment = df.iloc[:, CONFIG['columns']['annual_treatment']]
heat_utilization = df.iloc[:, CONFIG['columns']['heat_utilization']]
low_heat_value_calc = df.iloc[:, CONFIG['columns']['low_heat_calc']]
low_heat_value_measured = df.iloc[:, CONFIG['columns']['low_heat_measured']]

# 余熱利用量の数値変換
heat_utilization = pd.to_numeric(heat_utilization, errors='coerce')

# 低位発熱量の選択ロジック: 実測値を優先し、なければ計算値を使用
low_heat_value = low_heat_value_measured.copy()
mask_use_calc = (low_heat_value_measured.isnull()) | (low_heat_value_measured <= 0)
low_heat_value[mask_use_calc] = low_heat_value_calc[mask_use_calc]

print(f"\n=== 低位発熱量の修正結果 ===")
print(f"実測値を使用: {(~mask_use_calc).sum()} 施設")
print(f"計算値を使用: {mask_use_calc.sum()} 施設")
print(f"有効な低位発熱量: {(low_heat_value > 0).sum()} 施設")
print(f"無効な低位発熱量 (0またはNaN): {((low_heat_value <= 0) | low_heat_value.isnull()).sum()} 施設")

# 年間発熱量の計算（単位変換: t * kJ/kg = MJ）
annual_heat = annual_treatment * low_heat_value

# 利用率の計算
utilization_rate = heat_utilization / annual_heat

# 有効なデータのみを抽出（欠損値を除く）
valid_mask = ~(annual_treatment.isnull() | heat_utilization.isnull() |
               low_heat_value.isnull() | (annual_treatment == 0) |
               (low_heat_value <= 0) | (annual_heat == 0))

# 低位発熱量の外れ値除去
valid_low_heat_value = low_heat_value[valid_mask]
print(f"\n=== 低位発熱量の外れ値除去 ===")
heat_value_outlier_mask = remove_outliers(valid_low_heat_value, CONFIG['outlier_sigma'])

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

# 年間発熱量と利用率の外れ値排除
print(f"\n=== 年間発熱量の外れ値除去 ===")
heat_outlier_mask = remove_outliers(valid_annual_heat, CONFIG['outlier_sigma'])

print(f"\n=== 利用率の外れ値除去 ===")
rate_outlier_mask = remove_outliers(valid_utilization_rate, CONFIG['outlier_sigma'])

outlier_removed_mask = heat_outlier_mask & rate_outlier_mask

# 外れ値除去後のデータ
filtered_annual_heat = valid_annual_heat[outlier_removed_mask]
filtered_utilization_rate = valid_utilization_rate[outlier_removed_mask]
filtered_heat_utilization = valid_heat_utilization[outlier_removed_mask]
filtered_low_heat_value = valid_low_heat_final[outlier_removed_mask]

print(f"\n最終的な外れ値除去後の範囲:")
print(f"  年間発熱量: {filtered_annual_heat.min():.2e} - {filtered_annual_heat.max():.2e} MJ")
print(f"  利用率: {filtered_utilization_rate.min():.4f} - {filtered_utilization_rate.max():.4f}")
print(f"  低位発熱量: {filtered_low_heat_value.min():.2f} - {filtered_low_heat_value.max():.2f} kJ/kg")

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
output_csv_path_all = '/home/ubuntu/cur/program/Analyisis_incineration/result/heat_utilization_results_all.csv'
output_df_all.to_csv(output_csv_path_all, index=False, encoding='utf-8-sig')
print(f"\n全データを {output_csv_path_all} に出力しました。")
print(f"出力データ数: {len(output_df_all)} 件")

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
    '余熱利用率': filtered_utilization_rate.values,
    '余熱利用_場内温水': df.iloc[filtered_indices, 27].values,
    '余熱利用_場内蒸気': df.iloc[filtered_indices, 28].values,
    '余熱利用_発電場内': df.iloc[filtered_indices, 29].values,
    '余熱利用_場外温水': df.iloc[filtered_indices, 30].values,
    '余熱利用_場外蒸気': df.iloc[filtered_indices, 31].values,
    '余熱利用_発電場外': df.iloc[filtered_indices, 32].values
})
output_csv_path_filtered = '/home/ubuntu/cur/program/Analyisis_incineration/result/heat_utilization_results_filtered.csv'
output_df_filtered.to_csv(output_csv_path_filtered, index=False, encoding='utf-8-sig')
print(f"\n外れ値除去後データを {output_csv_path_filtered} に出力しました。")
print(f"出力データ数: {len(output_df_filtered)} 件")

# 統計情報の表示
print("\n=== 外れ値除去後の統計情報 ===")
print(f"年間発熱量 (MJ):")
print(f"  平均: {filtered_annual_heat.mean():.2e}")
print(f"  中央値: {filtered_annual_heat.median():.2e}")
print(f"  標準偏差: {filtered_annual_heat.std():.2e}")
print(f"\n利用率:")
print(f"  平均: {filtered_utilization_rate.mean():.4f}")
print(f"  中央値: {filtered_utilization_rate.median():.4f}")
print(f"  標準偏差: {filtered_utilization_rate.std():.4f}")

# 条件付き確率の算出
print(f"\n=== 余熱利用の状況に関する条件付き確率 ===")
steam_col = '余熱利用の状況_場内蒸気'
power_internal_col = '余熱利用の状況_発電（場内利用）'
power_external_col = '余熱利用の状況_発電（場外利用）'

steam_has_value = (~df[steam_col].isnull()) & (df[steam_col] != '') & (df[steam_col] != 0)
power_internal_has_value = (~df[power_internal_col].isnull()) & (df[power_internal_col] != '') & (df[power_internal_col] != 0)
power_external_has_value = (~df[power_external_col].isnull()) & (df[power_external_col] != '') & (df[power_external_col] != 0)
both_power_has_value = power_internal_has_value & power_external_has_value

steam_count = steam_has_value.sum()
both_power_given_steam_count = (steam_has_value & both_power_has_value).sum()

if steam_count > 0:
    conditional_probability = both_power_given_steam_count / steam_count
    print(f"場内蒸気に要素がある施設数: {steam_count}")
    print(f"場内蒸気があり、かつ発電(場内・場外)に要素がある施設数: {both_power_given_steam_count}")
    print(f"条件付き確率: {conditional_probability:.4f} ({conditional_probability*100:.2f}%)")

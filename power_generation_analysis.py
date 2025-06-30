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
        'power_capacity': 39, # 発電能力_発電能力_kW
        'power_generation': 41, # 発電能力_総発電量（実績値）_MWh
        'low_heat_calc': 94,
        'low_heat_measured': 95,
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

# 必要なデータを抽出
annual_treatment = df.iloc[:, CONFIG['columns']['annual_treatment']]
power_capacity_kw = pd.to_numeric(df.iloc[:, CONFIG['columns']['power_capacity']], errors='coerce')
power_generation_mwh = pd.to_numeric(df.iloc[:, CONFIG['columns']['power_generation']], errors='coerce')
low_heat_value_calc = df.iloc[:, CONFIG['columns']['low_heat_calc']]
low_heat_value_measured = df.iloc[:, CONFIG['columns']['low_heat_measured']]

# 単位変換
power_generation_mj = power_generation_mwh * 3600
theoretical_max_power_mwh = power_capacity_kw * 24 * 365 / 1000 # MWh

# 低位発熱量の選択
low_heat_value = low_heat_value_measured.copy()
mask_use_calc = (low_heat_value_measured.isnull()) | (low_heat_value_measured <= 0)
low_heat_value[mask_use_calc] = low_heat_value_calc[mask_use_calc]

# 計算
annual_heat = annual_treatment * low_heat_value
power_utilization_rate = power_generation_mj / annual_heat
facility_utilization_rate = power_generation_mwh / theoretical_max_power_mwh

# 有効データのマスク
valid_mask = ~(
    annual_treatment.isnull() | 
    power_generation_mj.isnull() | 
    low_heat_value.isnull() | 
    power_capacity_kw.isnull() | 
    (annual_treatment == 0) | 
    (low_heat_value <= 0) | 
    (annual_heat == 0) | 
    (power_generation_mj <= 0) | 
    (power_capacity_kw <= 0)
)

# 外れ値除去
valid_low_heat_value = low_heat_value[valid_mask]
heat_value_outlier_mask = remove_outliers(valid_low_heat_value, CONFIG['outlier_sigma'])
temp_valid_indices = valid_mask[valid_mask].index
low_heat_outlier_indices = temp_valid_indices[heat_value_outlier_mask]
valid_mask_updated = pd.Series(False, index=valid_mask.index)
valid_mask_updated[low_heat_outlier_indices] = True
valid_mask = valid_mask_updated

valid_annual_heat = annual_heat[valid_mask]
valid_power_utilization_rate = power_utilization_rate[valid_mask]
valid_facility_utilization_rate = facility_utilization_rate[valid_mask]

heat_outlier_mask = remove_outliers(valid_annual_heat, CONFIG['outlier_sigma'])
rate_outlier_mask = remove_outliers(valid_power_utilization_rate, CONFIG['outlier_sigma'])
facility_rate_outlier_mask = remove_outliers(valid_facility_utilization_rate, CONFIG['outlier_sigma'])

outlier_removed_mask = heat_outlier_mask & rate_outlier_mask & facility_rate_outlier_mask

# CSV出力
filtered_indices = valid_mask[valid_mask].index[outlier_removed_mask]

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
        'power_capacity': 39, # 発電能力_発電能力_kW
        'power_generation': 41, # 発電能力_総発電量（実績値）_MWh
        'low_heat_calc': 94,
        'low_heat_measured': 95,
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

# 必要なデータを抽出
annual_treatment = df.iloc[:, CONFIG['columns']['annual_treatment']]
power_capacity_kw = pd.to_numeric(df.iloc[:, CONFIG['columns']['power_capacity']], errors='coerce')
power_generation_mwh = pd.to_numeric(df.iloc[:, CONFIG['columns']['power_generation']], errors='coerce')
low_heat_value_calc = df.iloc[:, CONFIG['columns']['low_heat_calc']]
low_heat_value_measured = df.iloc[:, CONFIG['columns']['low_heat_measured']]

# 単位変換
power_generation_mj = power_generation_mwh * 3600
theoretical_max_power_mwh = power_capacity_kw * 24 * 365 / 1000 # MWh

# 低位発熱量の選択
low_heat_value = low_heat_value_measured.copy()
mask_use_calc = (low_heat_value_measured.isnull()) | (low_heat_value_measured <= 0)
low_heat_value[mask_use_calc] = low_heat_value_calc[mask_use_calc]

# 計算
annual_heat = annual_treatment * low_heat_value
power_utilization_rate = power_generation_mj / annual_heat
facility_utilization_rate = power_generation_mwh / theoretical_max_power_mwh

# 有効データのマスク
valid_mask = ~(
    annual_treatment.isnull() | 
    power_generation_mj.isnull() | 
    low_heat_value.isnull() | 
    power_capacity_kw.isnull() | 
    (annual_treatment == 0) | 
    (low_heat_value <= 0) | 
    (annual_heat == 0) | 
    (power_generation_mj <= 0) | 
    (power_capacity_kw <= 0)
)

# 外れ値除去
valid_low_heat_value = low_heat_value[valid_mask]
heat_value_outlier_mask = remove_outliers(valid_low_heat_value, CONFIG['outlier_sigma'])
temp_valid_indices = valid_mask[valid_mask].index
low_heat_outlier_indices = temp_valid_indices[heat_value_outlier_mask]
valid_mask_updated = pd.Series(False, index=valid_mask.index)
valid_mask_updated[low_heat_outlier_indices] = True
valid_mask = valid_mask_updated

valid_annual_heat = annual_heat[valid_mask]
valid_power_utilization_rate = power_utilization_rate[valid_mask]
valid_facility_utilization_rate = facility_utilization_rate[valid_mask]

heat_outlier_mask = remove_outliers(valid_annual_heat, CONFIG['outlier_sigma'])
rate_outlier_mask = remove_outliers(valid_power_utilization_rate, CONFIG['outlier_sigma'])
facility_rate_outlier_mask = remove_outliers(valid_facility_utilization_rate, CONFIG['outlier_sigma'])

outlier_removed_mask = heat_outlier_mask & rate_outlier_mask & facility_rate_outlier_mask

# CSV出力
filtered_indices = valid_mask[valid_mask].index[outlier_removed_mask]

output_df_filtered = pd.DataFrame({
    '都道府県名': df.iloc[filtered_indices, CONFIG['columns']['prefecture']].values,
    '地方公共団体名': df.iloc[filtered_indices, CONFIG['columns']['municipality']].values,
    '施設名称': df.iloc[filtered_indices, CONFIG['columns']['facility_name']].values,
    '年間処理量_t': df.iloc[filtered_indices, CONFIG['columns']['annual_treatment']].values,
    '発電能力_kW': power_capacity_kw[filtered_indices].values,
    '総発電量_MWh': power_generation_mwh[filtered_indices].values,
    '低位発熱量_kJ_per_kg': low_heat_value[filtered_indices].values,
    '年間発熱量_MJ': annual_heat[filtered_indices].values,
    '発電量_MJ': power_generation_mj[filtered_indices].values,
    '発電利用率': power_utilization_rate[filtered_indices].values,
    '設備利用率': facility_utilization_rate[filtered_indices].values
})

output_csv_path_filtered = os.path.join(CONFIG['output_dir'], 'power_generation_results_filtered.csv')
safe_to_csv(output_df_filtered, output_csv_path_filtered, index=False, encoding='utf-8-sig')

valid_indices_all = valid_mask[valid_mask].index
output_df_all = pd.DataFrame({
    '都道府県名': df.iloc[valid_indices_all, CONFIG['columns']['prefecture']].values,
    '地方公共団体名': df.iloc[valid_indices_all, CONFIG['columns']['municipality']].values,
    '施設名称': df.iloc[valid_indices_all, CONFIG['columns']['facility_name']].values,
    '年間処理量_t': df.iloc[valid_indices_all, CONFIG['columns']['annual_treatment']].values,
    '発電能力_kW': power_capacity_kw[valid_indices_all].values,
    '総発電量_MWh': power_generation_mwh[valid_indices_all].values,
    '低位発熱量_kJ_per_kg': low_heat_value[valid_indices_all].values,
    '年間発熱量_MJ': annual_heat[valid_indices_all].values,
    '発電量_MJ': power_generation_mj[valid_indices_all].values,
    '発電利用率': power_utilization_rate[valid_indices_all].values,
    '設備利用率': facility_utilization_rate[valid_indices_all].values
})

output_csv_path_all = os.path.join(CONFIG['output_dir'], 'power_generation_results_all.csv')
safe_to_csv(output_df_all, output_csv_path_all, index=False, encoding='utf-8-sig')


output_csv_path_all = os.path.join(CONFIG['output_dir'], 'power_generation_results_all.csv')
safe_to_csv(output_df_all, output_csv_path_all, index=False, encoding='utf-8-sig')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
焼却施設データから発電効率の統計情報を取得するスクリプト
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 日本語フォント設定
plt.rcParams['font.family'] = 'M+ 1c'

def load_and_analyze_power_efficiency():
    """
    CSVファイルを読み込み、発電効率の統計情報を取得する
    """
    # CSVファイルの読み込み
    file_path = "2022_1焼却施設.csv"
    
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"データを正常に読み込みました。データ形状: {df.shape}")
        
    except UnicodeDecodeError:
        # エンコーディングエラーの場合、shift_jisで再試行
        df = pd.read_csv(file_path, encoding='shift_jis')
        print(f"データを正常に読み込みました（shift_jis）。データ形状: {df.shape}")
    
    # 発電効率のカラム名を確認
    power_efficiency_column = "発電能力_発電効率（仕様値・公称値）_％"
    
    if power_efficiency_column not in df.columns:
        print("発電効率のカラムが見つかりません。利用可能なカラム:")
        for col in df.columns:
            if "発電" in col and "効率" in col:
                print(f"  - {col}")
        return None
    
    # 発電効率データの抽出
    power_efficiency = df[power_efficiency_column]
    
    print(f"\n=== 発電効率の統計情報 ===")
    print(f"カラム名: {power_efficiency_column}")
    print(f"データ型: {power_efficiency.dtype}")
    print(f"総データ数: {len(power_efficiency)}")
    print(f"欠損値数: {power_efficiency.isnull().sum()}")
    print(f"有効データ数: {power_efficiency.notna().sum()}")
    
    # 数値型に変換（エラーは NaN に変換）
    power_efficiency_numeric = pd.to_numeric(power_efficiency, errors='coerce')
    
    print(f"\n=== 数値変換後の情報 ===")
    print(f"数値変換後の有効データ数: {power_efficiency_numeric.notna().sum()}")
    print(f"数値変換で失われたデータ数: {power_efficiency_numeric.isna().sum() - power_efficiency.isna().sum()}")
    
    # 有効なデータのみでdescribe()を実行
    valid_data = power_efficiency_numeric.dropna()
    
    if len(valid_data) > 0:
        print(f"\n=== 発電効率の基本統計量（describe()） ===")
        print(valid_data.describe())
        
        # 追加の統計情報
        print(f"\n=== 追加統計情報 ===")
        print(f"分散: {valid_data.var():.4f}")
        print(f"標準偏差: {valid_data.std():.4f}")
        print(f"歪度（skewness）: {valid_data.skew():.4f}")
        print(f"尖度（kurtosis）: {valid_data.kurtosis():.4f}")
        
        # 0より大きい値のみの統計（発電効率が0は実質的に発電していない）
        positive_efficiency = valid_data[valid_data > 0]
        if len(positive_efficiency) > 0:
            print(f"\n=== 発電効率 > 0 のデータの統計量 ===")
            print(f"データ数: {len(positive_efficiency)}")
            print(positive_efficiency.describe())
        
        return valid_data
    else:
        print("有効な発電効率データが見つかりませんでした。")
        return None

def analyze_power_generation_facilities():
    """
    余熱利用で発電を行っている施設の数と割合を分析する
    """
    # CSVファイルの読み込み
    file_path = "2022_1焼却施設.csv"
    
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"データを正常に読み込みました。データ形状: {df.shape}")
        
    except UnicodeDecodeError:
        # エンコーディングエラーの場合、shift_jisで再試行
        df = pd.read_csv(file_path, encoding='shift_jis')
        print(f"データを正常に読み込みました（shift_jis）。データ形状: {df.shape}")
    
    # 発電関連の列名
    power_gen_inside = "余熱利用の状況_発電（場内利用）"
    power_gen_outside = "余熱利用の状況_発電（場外利用）"
    
    # 列の存在確認
    if power_gen_inside not in df.columns or power_gen_outside not in df.columns:
        print("発電関連の列が見つかりません。利用可能なカラム:")
        for col in df.columns:
            if "発電" in col:
                print(f"  - {col}")
        return None
    
    # 総施設数
    total_facilities = len(df)
    
    # 発電を行っている施設の特定
    # 場内利用または場外利用で発電している施設（○が入っている）
    power_generation_facilities = df[
        (df[power_gen_inside] == '○') | (df[power_gen_outside] == '○')
    ]
    
    # 発電施設数
    power_facility_count = len(power_generation_facilities)
    
    # 発電施設の割合
    power_facility_ratio = (power_facility_count / total_facilities) * 100
    
    print(f"\n=== 余熱利用発電施設の統計情報 ===")
    print(f"総焼却施設数: {total_facilities:,} 施設")
    print(f"発電を行っている施設数: {power_facility_count:,} 施設")
    print(f"発電施設の割合: {power_facility_ratio:.2f}%")
    
    # 詳細分析
    inside_only = df[
        (df[power_gen_inside] == '○') & (df[power_gen_outside] != '○')
    ]
    outside_only = df[
        (df[power_gen_inside] != '○') & (df[power_gen_outside] == '○')
    ]
    both = df[
        (df[power_gen_inside] == '○') & (df[power_gen_outside] == '○')
    ]
    
    print(f"\n=== 発電利用の詳細内訳 ===")
    print(f"場内利用のみ: {len(inside_only):,} 施設 ({len(inside_only)/total_facilities*100:.2f}%)")
    print(f"場外利用のみ: {len(outside_only):,} 施設 ({len(outside_only)/total_facilities*100:.2f}%)")
    print(f"場内・場外両方: {len(both):,} 施設 ({len(both)/total_facilities*100:.2f}%)")
    
    # 発電能力が記載されている施設の分析
    power_capacity_column = "発電能力_発電能力_kW"
    if power_capacity_column in df.columns:
        # 発電施設で発電能力が記載されている施設
        power_gen_with_capacity = power_generation_facilities[
            power_generation_facilities[power_capacity_column].notna() &
            (power_generation_facilities[power_capacity_column] != '') &
            (pd.to_numeric(power_generation_facilities[power_capacity_column], errors='coerce') > 0)
        ]
        
        print(f"\n=== 発電能力データ保有状況 ===")
        print(f"発電施設のうち発電能力データあり: {len(power_gen_with_capacity):,} 施設")
        print(f"発電施設での発電能力データ保有率: {len(power_gen_with_capacity)/power_facility_count*100:.2f}%")
        
        if len(power_gen_with_capacity) > 0:
            capacity_data = pd.to_numeric(power_gen_with_capacity[power_capacity_column], errors='coerce')
            print(f"発電能力の統計（kW）:")
            print(f"  平均: {capacity_data.mean():.2f} kW")
            print(f"  中央値: {capacity_data.median():.2f} kW")
            print(f"  最小値: {capacity_data.min():.2f} kW")
            print(f"  最大値: {capacity_data.max():.2f} kW")
            print(f"  合計: {capacity_data.sum():.2f} kW")
    
    return power_generation_facilities

def analyze_heat_utilization_facilities():
    """
    温水・蒸気による余熱利用を行っている施設の数と割合、熱利用量の統計情報を分析する
    """
    # CSVファイルの読み込み
    file_path = "2022_1焼却施設.csv"
    
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"データを正常に読み込みました。データ形状: {df.shape}")
        
    except UnicodeDecodeError:
        # エンコーディングエラーの場合、shift_jisで再試行
        df = pd.read_csv(file_path, encoding='shift_jis')
        print(f"データを正常に読み込みました（shift_jis）。データ形状: {df.shape}")
    
    # 温水・蒸気利用関連の列名
    inside_hot_water = "余熱利用の状況_場内温水"
    inside_steam = "余熱利用の状況_場内蒸気"
    outside_hot_water = "余熱利用の状況_場外温水"
    outside_steam = "余熱利用の状況_場外蒸気"
    heat_utilization_amount = "余熱利用量（実績値）_余熱利用量_MJ"
    
    # 列の存在確認
    required_columns = [inside_hot_water, inside_steam, outside_hot_water, outside_steam]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print("温水・蒸気利用関連の列が見つかりません:")
        for col in missing_columns:
            print(f"  - {col}")
        print("\n利用可能なカラム:")
        for col in df.columns:
            if "温水" in col or "蒸気" in col:
                print(f"  - {col}")
        return None
    
    # 総施設数
    total_facilities = len(df)
    
    # 温水・蒸気利用を行っている施設の特定
    # 場内または場外で温水または蒸気を利用している施設（○が入っている）
    heat_utilization_facilities = df[
        (df[inside_hot_water] == '○') | 
        (df[inside_steam] == '○') | 
        (df[outside_hot_water] == '○') | 
        (df[outside_steam] == '○')
    ]
    
    # 温水・蒸気利用施設数
    heat_facility_count = len(heat_utilization_facilities)
    
    # 温水・蒸気利用施設の割合
    heat_facility_ratio = (heat_facility_count / total_facilities) * 100
    
    print(f"\n=== 温水・蒸気による余熱利用施設の統計情報 ===")
    print(f"総焼却施設数: {total_facilities:,} 施設")
    print(f"温水・蒸気利用を行っている施設数: {heat_facility_count:,} 施設")
    print(f"温水・蒸気利用施設の割合: {heat_facility_ratio:.2f}%")
    
    # 詳細分析（種類別）
    inside_hot_water_count = len(df[df[inside_hot_water] == '○'])
    inside_steam_count = len(df[df[inside_steam] == '○'])
    outside_hot_water_count = len(df[df[outside_hot_water] == '○'])
    outside_steam_count = len(df[df[outside_steam] == '○'])
    
    print(f"\n=== 温水・蒸気利用の詳細内訳 ===")
    print(f"場内温水利用: {inside_hot_water_count:,} 施設 ({inside_hot_water_count/total_facilities*100:.2f}%)")
    print(f"場内蒸気利用: {inside_steam_count:,} 施設 ({inside_steam_count/total_facilities*100:.2f}%)")
    print(f"場外温水利用: {outside_hot_water_count:,} 施設 ({outside_hot_water_count/total_facilities*100:.2f}%)")
    print(f"場外蒸気利用: {outside_steam_count:,} 施設 ({outside_steam_count/total_facilities*100:.2f}%)")
    
    # 場内・場外での利用パターン分析
    inside_only = df[
        ((df[inside_hot_water] == '○') | (df[inside_steam] == '○')) &
        ((df[outside_hot_water] != '○') & (df[outside_steam] != '○'))
    ]
    outside_only = df[
        ((df[inside_hot_water] != '○') & (df[inside_steam] != '○')) &
        ((df[outside_hot_water] == '○') | (df[outside_steam] == '○'))
    ]
    both = df[
        ((df[inside_hot_water] == '○') | (df[inside_steam] == '○')) &
        ((df[outside_hot_water] == '○') | (df[outside_steam] == '○'))
    ]
    
    print(f"\n=== 場内・場外利用パターン ===")
    print(f"場内のみ: {len(inside_only):,} 施設 ({len(inside_only)/total_facilities*100:.2f}%)")
    print(f"場外のみ: {len(outside_only):,} 施設 ({len(outside_only)/total_facilities*100:.2f}%)")
    print(f"場内・場外両方: {len(both):,} 施設 ({len(both)/total_facilities*100:.2f}%)")
    
    # 熱利用量の統計分析
    if heat_utilization_amount in df.columns:
        print(f"\n=== 熱利用量（実績値）の統計情報 ===")
        print(f"カラム名: {heat_utilization_amount}")
        
        # 全施設の熱利用量分析
        all_heat_data = pd.to_numeric(df[heat_utilization_amount], errors='coerce')
        valid_heat_data = all_heat_data.dropna()
        
        print(f"\n--- 全施設（熱利用量データあり）---")
        print(f"熱利用量データ保有施設数: {len(valid_heat_data):,} 施設")
        print(f"熱利用量データ保有率: {len(valid_heat_data)/total_facilities*100:.2f}%")
        
        if len(valid_heat_data) > 0:
            print(f"熱利用量の基本統計量（MJ）:")
            print(valid_heat_data.describe())
            
            print(f"\n追加統計情報:")
            print(f"分散: {valid_heat_data.var():.2f}")
            print(f"標準偏差: {valid_heat_data.std():.2f}")
            print(f"歪度（skewness）: {valid_heat_data.skew():.4f}")
            print(f"尖度（kurtosis）: {valid_heat_data.kurtosis():.4f}")
        
        # 温水・蒸気利用施設の熱利用量分析
        heat_util_heat_data = pd.to_numeric(heat_utilization_facilities[heat_utilization_amount], errors='coerce')
        valid_heat_util_data = heat_util_heat_data.dropna()
        
        print(f"\n--- 温水・蒸気利用施設（熱利用量データあり）---")
        print(f"温水・蒸気利用施設での熱利用量データ保有数: {len(valid_heat_util_data):,} 施設")
        print(f"温水・蒸気利用施設での熱利用量データ保有率: {len(valid_heat_util_data)/heat_facility_count*100:.2f}%")
        
        if len(valid_heat_util_data) > 0:
            print(f"温水・蒸気利用施設の熱利用量統計（MJ）:")
            print(valid_heat_util_data.describe())
            
            # 0より大きい値のみの統計（実際に熱利用を行っている）
            positive_heat_util = valid_heat_util_data[valid_heat_util_data > 0]
            if len(positive_heat_util) > 0:
                print(f"\n--- 熱利用量 > 0 の温水・蒸気利用施設 ---")
                print(f"実際に熱利用している施設数: {len(positive_heat_util):,} 施設")
                print(positive_heat_util.describe())
        
        # 熱利用の効率性分析（処理能力あたりの熱利用量）
        if "施設全体の処理能力_t/日" in df.columns:
            capacity_col = "施設全体の処理能力_t/日"
            capacity_data = pd.to_numeric(df[capacity_col], errors='coerce')
            
            # 処理能力と熱利用量の両方にデータがある施設
            both_data_mask = (all_heat_data.notna()) & (capacity_data.notna()) & (capacity_data > 0)
            
            if both_data_mask.sum() > 0:
                heat_efficiency = all_heat_data[both_data_mask] / capacity_data[both_data_mask]
                print(f"\n--- 処理能力あたりの熱利用量（MJ/t・日）---")
                print(f"分析対象施設数: {len(heat_efficiency):,} 施設")
                print(heat_efficiency.describe())
    
    else:
        print(f"\n熱利用量のカラム（{heat_utilization_amount}）が見つかりません。")
    
    return heat_utilization_facilities

def detect_outliers_and_validate_data(df_calc):
    """
    外れ値検出とデータ検証を行う
    """
    print(f"\n=== 外れ値検出とデータ検証 ===")
    
    # 1. 入力データの外れ値検出
    print(f"\n--- 入力データの検証 ---")
    
    # 年間処理量の外れ値（負の値や異常に大きな値）
    annual_outliers = df_calc[
        (df_calc['annual_processing_numeric'] < 0) | 
        (df_calc['annual_processing_numeric'] > 1000000)  # 100万トン/年を超える場合
    ]
    if len(annual_outliers) > 0:
        print(f"年間処理量の異常値: {len(annual_outliers)} 施設")
        print(annual_outliers[['施設名称', 'annual_processing_numeric']].head())
    
    # 定位発熱量の外れ値（負の値や異常に大きな/小さな値）
    lcv_outliers = df_calc[
        (df_calc['lcv_used'] < 0) | 
        (df_calc['lcv_used'] > 50000) |  # 50,000 kJ/kg を超える場合
        (df_calc['lcv_used'] < 1000)     # 1,000 kJ/kg を下回る場合
    ]
    if len(lcv_outliers) > 0:
        print(f"定位発熱量の異常値: {len(lcv_outliers)} 施設")
        print(lcv_outliers[['施設名称', 'lcv_used']].head())
    
    # 余熱利用量の外れ値（負の値）
    heat_util_outliers = df_calc[df_calc['heat_utilization_numeric'] < 0]
    if len(heat_util_outliers) > 0:
        print(f"余熱利用量の負の値: {len(heat_util_outliers)} 施設")
    
    # 発電量の外れ値（負の値）
    power_outliers = df_calc[df_calc['power_generation_numeric'] < 0]
    if len(power_outliers) > 0:
        print(f"発電量の負の値: {len(power_outliers)} 施設")
    
    # 2. 熱利用率の物理的妥当性検証
    print(f"\n--- 熱利用率の物理的妥当性検証 ---")
    
    # 100%を超える熱利用率（物理的に不可能）
    over_100_percent = df_calc[df_calc['heat_utilization_ratio'] > 100]
    if len(over_100_percent) > 0:
        print(f"熱利用率100%超の施設: {len(over_100_percent)} 施設")
        print("詳細:")
        cols_to_show = ['施設名称', 'annual_processing_numeric', 'lcv_used', 
                       'generated_heat_mj', 'total_heat_utilization', 'heat_utilization_ratio']
        print(over_100_percent[cols_to_show].head(10))
        
        # 最も高い熱利用率の施設
        max_ratio_facility = over_100_percent.loc[over_100_percent['heat_utilization_ratio'].idxmax()]
        print(f"\n最高熱利用率: {max_ratio_facility['heat_utilization_ratio']:.2f}% - {max_ratio_facility['施設名称']}")
    
    # 50%を超える熱利用率（非常に高い効率）
    over_50_percent = df_calc[
        (df_calc['heat_utilization_ratio'] > 50) & 
        (df_calc['heat_utilization_ratio'] <= 100)
    ]
    if len(over_50_percent) > 0:
        print(f"熱利用率50%超〜100%以下の施設: {len(over_50_percent)} 施設")
    
    # 3. 統計的外れ値検出（IQR法）
    print(f"\n--- 統計的外れ値検出（IQR法）---")
    
    # 有効な熱利用率データのみを使用
    valid_ratios = df_calc[df_calc['heat_utilization_ratio'].notna()]['heat_utilization_ratio']
    
    if len(valid_ratios) > 0:
        Q1 = valid_ratios.quantile(0.25)
        Q3 = valid_ratios.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        print(f"Q1: {Q1:.2f}%, Q3: {Q3:.2f}%, IQR: {IQR:.2f}%")
        print(f"外れ値の境界: {lower_bound:.2f}% 〜 {upper_bound:.2f}%")
        
        # 統計的外れ値
        statistical_outliers = df_calc[
            (df_calc['heat_utilization_ratio'] < lower_bound) | 
            (df_calc['heat_utilization_ratio'] > upper_bound)
        ]
        print(f"統計的外れ値の施設数: {len(statistical_outliers)} 施設")
        
        if len(statistical_outliers) > 0:
            print("上位10施設の外れ値:")
            top_outliers = statistical_outliers.nlargest(10, 'heat_utilization_ratio')
            print(top_outliers[['施設名称', 'heat_utilization_ratio']].to_string())
    
    # 4. データ品質に関する推奨事項
    print(f"\n--- データ品質に関する推奨事項 ---")
    
    # 外れ値除去のオプション提供
    recommendations = []
    
    if len(over_100_percent) > 0:
        recommendations.append("熱利用率100%超の施設はデータエラーの可能性が高いため除外を推奨")
    
    if len(lcv_outliers) > 0:
        recommendations.append("定位発熱量が異常な施設は測定エラーの可能性があるため確認が必要")
    
    if len(annual_outliers) > 0:
        recommendations.append("年間処理量が異常な施設は入力エラーの可能性があるため確認が必要")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    return {
        'over_100_percent': over_100_percent,
        'over_50_percent': over_50_percent,
        'statistical_outliers': statistical_outliers,
        'annual_outliers': annual_outliers,
        'lcv_outliers': lcv_outliers,
        'iqr_bounds': (lower_bound, upper_bound) if len(valid_ratios) > 0 else None
    }

def calculate_heat_utilization_ratio():
    """
    定位発熱量と年間処理量から発生熱量を計算し、熱利用率を算出してヒストグラムを作成する
    """
    # CSVファイルの読み込み
    file_path = "2022_1焼却施設.csv"
    
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"データを正常に読み込みました。データ形状: {df.shape}")
        
    except UnicodeDecodeError:
        # エンコーディングエラーの場合、shift_jisで再試行
        df = pd.read_csv(file_path, encoding='shift_jis')
        print(f"データを正常に読み込みました（shift_jis）。データ形状: {df.shape}")
    
    # 必要な列名
    annual_processing = "年間処理量_t/年度"
    lcv_actual = "低位発熱量_(実測値)_kJ/kg"
    lcv_calculated = "低位発熱量_(計算値)_kJ/kg"
    heat_utilization_actual = "余熱利用量（実績値）_余熱利用量_MJ"
    power_generation_actual = "発電能力_総発電量（実績値）_MWh"
    
    # 列の存在確認
    required_columns = [annual_processing, lcv_actual, lcv_calculated, heat_utilization_actual]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print("必要な列が見つかりません:")
        for col in missing_columns:
            print(f"  - {col}")
        return None
    
    print(f"\n=== 熱利用率の計算 ===")
    
    # データの前処理
    df_calc = df.copy()
    
    # 年間処理量を数値型に変換
    df_calc['annual_processing_numeric'] = pd.to_numeric(df_calc[annual_processing], errors='coerce')
    
    # 定位発熱量の選択（実測値を優先、なければ計算値）
    df_calc['lcv_actual_numeric'] = pd.to_numeric(df_calc[lcv_actual], errors='coerce')
    df_calc['lcv_calculated_numeric'] = pd.to_numeric(df_calc[lcv_calculated], errors='coerce')
    
    # 実測値を優先して使用、なければ計算値
    df_calc['lcv_used'] = df_calc['lcv_actual_numeric'].fillna(df_calc['lcv_calculated_numeric'])
    
    # 余熱利用量を数値型に変換
    df_calc['heat_utilization_numeric'] = pd.to_numeric(df_calc[heat_utilization_actual], errors='coerce')
    
    # 発電量を数値型に変換（MWh → MJ変換: 1 MWh = 3600 MJ）
    if power_generation_actual in df_calc.columns:
        df_calc['power_generation_numeric'] = pd.to_numeric(df_calc[power_generation_actual], errors='coerce')
        df_calc['power_generation_mj'] = df_calc['power_generation_numeric'] * 3600  # MWh to MJ
    else:
        df_calc['power_generation_mj'] = 0
        print(f"警告: {power_generation_actual} 列が見つかりません。発電量を0として計算します。")
    
    # 発生熱量の計算（年間処理量 × 定位発熱量）
    # 年間処理量: t/年, 定位発熱量: kJ/kg → MJ/年に変換
    df_calc['generated_heat_mj'] = (df_calc['annual_processing_numeric'] * 1000 * df_calc['lcv_used']) / 1000
    
    # 全体の熱利用量（余熱利用 + 発電）
    df_calc['total_heat_utilization'] = df_calc['heat_utilization_numeric'].fillna(0) + df_calc['power_generation_mj'].fillna(0)
    
    # 熱利用率の計算
    df_calc['heat_utilization_ratio'] = np.where(
        (df_calc['generated_heat_mj'] > 0),
        df_calc['total_heat_utilization'] / df_calc['generated_heat_mj'] * 100,
        np.nan  # 0の代わりにNaNを設定
    )
    
    # 計算に必要なデータが揃っている施設の抽出
    valid_data_mask = (
        df_calc['annual_processing_numeric'].notna() &
        df_calc['lcv_used'].notna() &
        (df_calc['annual_processing_numeric'] > 0) &
        (df_calc['lcv_used'] > 0)
    )
    
    # 余熱利用または発電利用を行っている施設のみを抽出
    heat_utilization_mask = (
        (df_calc['heat_utilization_numeric'].notna() & (df_calc['heat_utilization_numeric'] > 0)) |
        (df_calc['power_generation_numeric'].notna() & (df_calc['power_generation_numeric'] > 0))
    )
    
    # 両方の条件を満たす施設のみを対象とする
    final_mask = valid_data_mask & heat_utilization_mask
    
    valid_data = df_calc[final_mask]
    
    print(f"計算対象施設数: {len(valid_data):,} 施設（余熱利用または発電利用を行っている施設のみ）")
    print(f"全施設数: {len(df):,} 施設")
    
    # 外れ値検出とデータ検証
    outlier_results = detect_outliers_and_validate_data(valid_data)
    
    # 統計情報の表示
    if len(valid_data) > 0:
        print(f"\n=== 熱利用率の統計情報 ===")
        print(valid_data['heat_utilization_ratio'].describe())
        
        print(f"\n=== 発生熱量の統計情報（MJ/年）===")
        print(valid_data['generated_heat_mj'].describe())
        
        print(f"\n=== 総熱利用量の統計情報（MJ/年）===")
        print(valid_data['total_heat_utilization'].describe())
        
        # 利用率別の施設数分析
        ratio_ranges = [
            (0, 10),     # 低利用
            (10, 20),    # 中利用
            (20, 30),    # 高利用
            (30, 50),    # 非常に高利用
            (50, 100),   # 超高利用
            (100, float('inf'))  # 物理的に不可能
        ]
        
        print(f"\n=== 熱利用率の分布 ===")
        for i, (min_val, max_val) in enumerate(ratio_ranges):
            if max_val == float('inf'):
                count = len(valid_data[valid_data['heat_utilization_ratio'] > min_val])
                print(f"{min_val}%超: {count:,} 施設 ({count/len(valid_data)*100:.1f}%)")
            else:
                count = len(valid_data[
                    (valid_data['heat_utilization_ratio'] > min_val) & 
                    (valid_data['heat_utilization_ratio'] <= max_val)
                ])
                print(f"{min_val}%超〜{max_val}%以下: {count:,} 施設 ({count/len(valid_data)*100:.1f}%)")
        
        # クリーンなデータでの分析オプション
        print(f"\n=== クリーンデータでの分析 ===")
        
        # 物理的に妥当なデータのみを使用（熱利用率 <= 100%）
        clean_data = valid_data[valid_data['heat_utilization_ratio'] <= 100]
        print(f"物理的に妥当なデータ: {len(clean_data):,} 施設")
        
        if len(clean_data) > 0:
            print("クリーンデータの熱利用率統計:")
            print(clean_data['heat_utilization_ratio'].describe())
        
        # 統計的外れ値を除外したデータ
        if outlier_results['iqr_bounds'] is not None:
            lower_bound, upper_bound = outlier_results['iqr_bounds']
            no_outliers_data = valid_data[
                (valid_data['heat_utilization_ratio'] >= lower_bound) & 
                (valid_data['heat_utilization_ratio'] <= upper_bound)
            ]
            print(f"\n統計的外れ値除外データ: {len(no_outliers_data):,} 施設")
            
            if len(no_outliers_data) > 0:
                print("外れ値除外後の熱利用率統計:")
                print(no_outliers_data['heat_utilization_ratio'].describe())
        
        # ヒストグラムの作成（物理的に妥当なデータのみ）
        plt.figure(figsize=(10, 6))
        
        # 物理的に妥当なデータ（≤100%）のみをプロット
        clean_data = valid_data[valid_data['heat_utilization_ratio'] <= 100]
        
        # 統計情報の計算
        mean_val = clean_data['heat_utilization_ratio'].mean()
        median_val = clean_data['heat_utilization_ratio'].median()
        std_val = clean_data['heat_utilization_ratio'].std()
        
        plt.hist(clean_data['heat_utilization_ratio'], bins=30, alpha=0.8, color='lightgreen', edgecolor='black')
        
        plt.title(f'Figure 3: Distribution of Waste Heat Utilization Rate (Overall)\n(Mean: {mean_val:.1f}%, Median: {median_val:.1f}%, Standard Deviation: {std_val:.1f}%, n={len(clean_data)})')
        plt.xlabel('Waste Heat Utilization Rate (%)')
        plt.ylabel('Number of Facilities')
        plt.grid(True)
        
        plt.savefig('result/heat_utilization_ratio_histogram.png')
        plt.close()
        print("グラフ 'result/heat_utilization_ratio_histogram.png' を保存しました。")
        print(f"余熱利用率統計: 平均 = {mean_val:.1f}%, 中央値 = {median_val:.1f}%, 標準偏差 = {std_val:.1f}%")
        print()
        
        # 詳細データの保存（外れ値情報も含む）
        output_data = valid_data[[
            '都道府県名', '地方公共団体名', '施設名称',
            'annual_processing_numeric', 'lcv_used', 'generated_heat_mj',
            'heat_utilization_numeric', 'power_generation_mj', 'total_heat_utilization',
            'heat_utilization_ratio'
        ]].copy()
        
        # 外れ値フラグの追加
        output_data['is_over_100_percent'] = output_data['heat_utilization_ratio'] > 100
        
        if outlier_results['iqr_bounds'] is not None:
            lower_bound, upper_bound = outlier_results['iqr_bounds']
            output_data['is_statistical_outlier'] = (
                (output_data['heat_utilization_ratio'] < lower_bound) | 
                (output_data['heat_utilization_ratio'] > upper_bound)
            )
        else:
            output_data['is_statistical_outlier'] = False
        
        # 利用種別の分類
        output_data['utilization_type'] = np.where(
            (output_data['heat_utilization_numeric'] > 0) & (output_data['power_generation_mj'] > 0),
            '余熱+発電',
            np.where(
                output_data['heat_utilization_numeric'] > 0,
                '余熱のみ',
                '発電のみ'
            )
        )
        
        output_data.columns = [
            '都道府県名', '地方公共団体名', '施設名称',
            '年間処理量_t', '使用定位発熱量_kJ/kg', '発生熱量_MJ',
            '余熱利用量_MJ', '発電量_MJ', '総熱利用量_MJ',
            '熱利用率_%', '100%超フラグ', '統計的外れ値フラグ', '利用種別'
        ]
        
        output_csv = "result/heat_utilization_ratio_results_filtered.csv"
        output_data.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"詳細データを {output_csv} に保存しました。")
        
        # 利用種別の統計
        print(f"\n=== 利用種別の分析 ===")
        utilization_counts = output_data['利用種別'].value_counts()
        for util_type, count in utilization_counts.items():
            print(f"{util_type}: {count:,} 施設 ({count/len(output_data)*100:.1f}%)")
        
        # 外れ値のみのデータ保存
        over_100_data = output_data[output_data['100%超フラグ'] == True]
        if len(over_100_data) > 0:
            outlier_csv = "result/heat_utilization_ratio_outliers_filtered.csv"
            over_100_data.to_csv(outlier_csv, index=False, encoding='utf-8-sig')
            print(f"100%超外れ値データを {outlier_csv} に保存しました。")
        
        return valid_data
    
    else:
        print("計算に必要なデータが不足しています。")
        return None

def main():
    """
    メイン関数
    """
    print("焼却施設の発電効率統計分析を開始します...")
    
    # 発電効率の統計分析を実行
    power_efficiency_data = load_and_analyze_power_efficiency()
    
    print("\n" + "="*60)
    print("余熱利用発電施設の分析を開始します...")
    
    # 発電施設の分析を実行
    power_facilities = analyze_power_generation_facilities()
    
    print("\n" + "="*60)
    print("温水・蒸気による余熱利用施設の分析を開始します...")
    
    # 温水・蒸気利用施設の分析を実行
    heat_facilities = analyze_heat_utilization_facilities()
    
    print("\n" + "="*60)
    print("熱利用率の計算とヒストグラム作成を開始します...")
    
    # 熱利用率の計算とヒストグラム作成
    heat_ratio_data = calculate_heat_utilization_ratio()
    
    if all([power_efficiency_data is not None, power_facilities is not None, 
            heat_facilities is not None, heat_ratio_data is not None]):
        print("\n" + "="*60)
        print("全ての分析が完了しました。")
    else:
        print("\n分析に失敗しました。")

if __name__ == "__main__":
    main()

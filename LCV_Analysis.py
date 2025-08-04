
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

# Matplotlibで日本語フォントを表示するための設定
plt.rcParams['font.sans-serif'] = ['M+ 1C']
plt.rcParams['axes.unicode_minus'] = False

def remove_outliers_iqr(df, column):
    """
    IQR法を使用して外れ値を除外する。
    
    Args:
        df (DataFrame): 対象のデータフレーム
        column (str): 外れ値を除外する列名
        
    Returns:
        DataFrame: 外れ値を除外したデータフレーム
        dict: 外れ値除外の統計情報
    """
    # 熱力学的に妥当な範囲での事前フィルタリング
    # 低位発熱量の物理的に妥当な範囲: 1,000 - 25,000 kJ/kg
    PHYSICAL_MIN = 1000  # kJ/kg - 極めて低い有機物含有量でも燃焼可能な最低値
    PHYSICAL_MAX = 25000  # kJ/kg - 高カロリー燃料（プラスチック多含有）の上限
    
    print(f"--- 物理的妥当性チェック ---")
    print(f"妥当な範囲: {PHYSICAL_MIN} - {PHYSICAL_MAX} kJ/kg")
    
    # 物理的に不可能な値を除外
    physical_outliers = df[(df[column] < PHYSICAL_MIN) | (df[column] > PHYSICAL_MAX)]
    df_physical = df[(df[column] >= PHYSICAL_MIN) & (df[column] <= PHYSICAL_MAX)]
    
    print(f"物理的異常値: {len(physical_outliers)}件")
    if len(physical_outliers) > 0:
        print(f"除外された値の範囲: {physical_outliers[column].min():.2f} - {physical_outliers[column].max():.2f} kJ/kg")
    print(f"物理的妥当性チェック後: {len(df_physical)}件")
    print()
    
    # IQR法による統計的外れ値除外
    Q1 = df_physical[column].quantile(0.25)
    Q3 = df_physical[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # 外れ値の検出
    statistical_outliers = df_physical[(df_physical[column] < lower_bound) | (df_physical[column] > upper_bound)]
    
    # 外れ値を除外
    df_cleaned = df_physical[(df_physical[column] >= lower_bound) & (df_physical[column] <= upper_bound)]
    
    total_outliers = len(physical_outliers) + len(statistical_outliers)
    
    outlier_info = {
        'total_records': len(df),
        'physical_outliers': len(physical_outliers),
        'statistical_outliers': len(statistical_outliers),
        'total_outliers': total_outliers,
        'outliers_percentage': (total_outliers / len(df)) * 100,
        'remaining_records': len(df_cleaned),
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'physical_min': PHYSICAL_MIN,
        'physical_max': PHYSICAL_MAX
    }
    
    return df_cleaned, outlier_info

def analyze_lcv(file_path):
    """
    CSVファイルを分析し、低位発熱量の統計分析と相関プロットを行う。
    外れ値除外機能を含む。

    Args:
        file_path (str): 分析対象のCSVファイルパス
    """
    try:
        # CSVファイルの読み込み
        df = pd.read_csv(file_path, encoding='utf-8')

        # 必要な列を抽出
        lcv_col = '低位発熱量_(実測値)_kJ/kg'
        capacity_col = '施設全体の処理能力_t/日'
        start_year_col = '使用開始年度'

        # データのクリーニングと型変換
        df[lcv_col] = pd.to_numeric(df[lcv_col], errors='coerce')
        df[capacity_col] = pd.to_numeric(df[capacity_col], errors='coerce')
        df[start_year_col] = pd.to_numeric(df[start_year_col], errors='coerce')

        # 欠損値の除去
        df.dropna(subset=[lcv_col, capacity_col, start_year_col], inplace=True)

        # 稼働年数の計算 (データが2022年度のものと仮定)
        current_year = 2022
        df['稼働年数'] = current_year - df[start_year_col]
        
        # 稼働年数が0未満のデータを除外
        df = df[df['稼働年数'] >= 0]

        # 外れ値の除外（低位発熱量）
        print("--- 外れ値除外前の低位発熱量データ ---")
        print(f"レコード数: {len(df)}")
        print(f"低位発熱量の範囲: {df[lcv_col].min():.2f} - {df[lcv_col].max():.2f} kJ/kg")
        print()

        df_cleaned, outlier_info = remove_outliers_iqr(df, lcv_col)

        print("--- 外れ値除外結果 ---")
        print(f"総レコード数: {outlier_info['total_records']}")
        print(f"物理的異常値: {outlier_info['physical_outliers']}")
        print(f"統計的外れ値: {outlier_info['statistical_outliers']}")
        print(f"総外れ値数: {outlier_info['total_outliers']}")
        print(f"外れ値割合: {outlier_info['outliers_percentage']:.2f}%")
        print(f"除外後レコード数: {outlier_info['remaining_records']}")
        print(f"物理的妥当範囲: {outlier_info['physical_min']} - {outlier_info['physical_max']} kJ/kg")
        print(f"統計的下限値: {outlier_info['lower_bound']:.2f} kJ/kg")
        print(f"統計的上限値: {outlier_info['upper_bound']:.2f} kJ/kg")
        print(f"Q1 (25%): {outlier_info['Q1']:.2f} kJ/kg")
        print(f"Q3 (75%): {outlier_info['Q3']:.2f} kJ/kg")
        print(f"IQR: {outlier_info['IQR']:.2f} kJ/kg")
        print()

        # 以降の分析は外れ値除外後のデータを使用
        df = df_cleaned


        # 1. 低位発熱量の数値分析（外れ値除外後）
        print("--- 低位発熱量_(実測値)_kJ/kg の統計分析（外れ値除外後） ---")
        print(df[lcv_col].describe())
        print(f"中央値: {df[lcv_col].median()}")
        print("\n")

        # 2. 施設全体の処理能力との相関プロット
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x=capacity_col, y=lcv_col)
        
        # 相関係数とP値の計算
        correlation_capacity, p_value_capacity = stats.pearsonr(df[capacity_col], df[lcv_col])
        
        # 統計的有意性の判定
        significance_capacity = ""
        if p_value_capacity < 0.001:
            significance_capacity = "***"
        elif p_value_capacity < 0.01:
            significance_capacity = "**"
        elif p_value_capacity < 0.05:
            significance_capacity = "*"
        else:
            significance_capacity = "n.s."
        
        # P値の適切な表示形式
        if p_value_capacity < 0.001:
            p_display_capacity = f"{p_value_capacity:.2e}"
        else:
            p_display_capacity = f"{p_value_capacity:.3f}"
        
        plt.title(f'低位発熱量 vs 施設全体の処理能力\n(相関係数: {correlation_capacity:.3f}, P値: {p_display_capacity} {significance_capacity})')
        plt.xlabel('施設全体の処理能力 (t/日)')
        plt.ylabel('低位発熱量 (実測値) (kJ/kg)')
        plt.grid(True)
        plt.savefig('result/lcv_vs_capacity.png')
        plt.close()
        print("グラフ 'result/lcv_vs_capacity.png' を保存しました。")
        print(f"処理能力との相関: r = {correlation_capacity:.3f}, p = {p_display_capacity} {significance_capacity}")
        print()


        # 3. 稼働年数との相関プロット
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x='稼働年数', y=lcv_col)
        
        # 相関係数とP値の計算
        correlation_years, p_value_years = stats.pearsonr(df['稼働年数'], df[lcv_col])
        
        # 統計的有意性の判定
        significance_years = ""
        if p_value_years < 0.001:
            significance_years = "***"
        elif p_value_years < 0.01:
            significance_years = "**"
        elif p_value_years < 0.05:
            significance_years = "*"
        else:
            significance_years = "n.s."
        
        # P値の適切な表示形式
        if p_value_years < 0.001:
            p_display_years = f"{p_value_years:.2e}"
        else:
            p_display_years = f"{p_value_years:.3f}"
        
        plt.title(f'低位発熱量 vs 稼働年数\n(相関係数: {correlation_years:.3f}, P値: {p_display_years} {significance_years})')
        plt.xlabel('稼働年数 (年)')
        plt.ylabel('低位発熱量 (実測値) (kJ/kg)')
        plt.grid(True)
        plt.savefig('result/lcv_vs_years.png')
        plt.close()
        print("グラフ 'result/lcv_vs_years.png' を保存しました。")
        print(f"稼働年数との相関: r = {correlation_years:.3f}, p = {p_display_years} {significance_years}")
        print()

        # 相関分析のまとめ
        print("--- 相関分析まとめ ---")
        print(f"処理能力との相関: r = {correlation_capacity:.3f}, p = {p_display_capacity} {significance_capacity}")
        print(f"稼働年数との相関: r = {correlation_years:.3f}, p = {p_display_years} {significance_years}")
        print()
        print("統計的有意性の記号:")
        print("*** p < 0.001 (非常に有意)")
        print("**  p < 0.01  (高度に有意)")
        print("*   p < 0.05  (有意)")
        print("n.s. p ≥ 0.05 (有意ではない)")
        print()
        print("注意: P値が非常に小さい場合は科学的記数法（例: 1.23e-05）で表示されます")


    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    csv_file = '2022_1焼却施設.csv'
    analyze_lcv(csv_file)

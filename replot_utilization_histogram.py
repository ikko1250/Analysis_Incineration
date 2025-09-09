

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# 日本語フォントの設定
mpl.rcParams['font.family'] = 'DejaVu Sans, M+ 1C'
plt.rcParams['font.size'] = 12

def replot_power_generation_utilization_histogram():
    """
    元のCSVデータから発電利用率を計算し、外れ値を除外した上でヒストグラムを作成する。
    """
    try:
        # 元データの読み込み
        df = pd.read_csv('/home/ubuntu/cur/program/Analyisis_incineration/2022_1焼却施設.csv', encoding='utf-8-sig')

        # 発電を行っている施設をフィルタリング
        df_power = df[
            (df['余熱利用の状況_発電（場内利用）'] == '○') |
            (df['余熱利用の状況_発電（場外利用）'] == '○')
        ].copy()

        # 必要な列を数値に変換
        df_power['発電能力_kW'] = pd.to_numeric(df_power['発電能力_発電能力_kW'], errors='coerce')
        df_power['総発電量_MWh'] = pd.to_numeric(df_power['発電能力_総発電量（実績値）_MWh'], errors='coerce')

        # 計算に必要なデータが揃っている施設に絞る
        df_power.dropna(subset=['発電能力_kW', '総発電量_MWh'], inplace=True)
        df_power = df_power[(df_power['発電能力_kW'] > 0) & (df_power['総発電量_MWh'] > 0)]

        # 発電利用率を計算 (年間最大発電量に対する割合)
        # 利用率 = (年間総発電量[kWh]) / (発電能力[kW] * 24時間 * 365日)
        # 総発電量はMWhなのでkWhに変換するために1000を掛ける
        df_power['発電利用率'] = (df_power['総発電量_MWh'] * 1000) / (df_power['発電能力_kW'] * 24 * 365)
        
        # 計算上の外れ値（利用率が1.5を超えるなど、物理的に考えにくいもの）を除外
        utilization_rate = df_power['発電利用率']
        utilization_rate = utilization_rate[utilization_rate <= 1.5]

        # IQR法による外れ値の検出と除外
        Q1 = utilization_rate.quantile(0.25)
        Q3 = utilization_rate.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        utilization_rate_filtered = utilization_rate[
            (utilization_rate >= lower_bound) & (utilization_rate <= upper_bound)
        ]

        # 1. 統計情報の計算
        mean_val = utilization_rate_filtered.mean()
        median_val = utilization_rate_filtered.median()
        std_val = utilization_rate_filtered.std()
        count_val = len(utilization_rate_filtered)
        original_count = len(df_power)
        outlier_count = original_count - count_val

        # 2. ヒストグラムのプロット
        plt.figure(figsize=(12, 7))
        
        plt.hist(utilization_rate_filtered, bins=25, alpha=0.75, color='deepskyblue', edgecolor='black')

        plt.title('Figure 2: Distribution of Capacity Factor')
        plt.xlabel('Capacity Factor (%)')
        plt.ylabel('Number of Facilities')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 統計情報をテキストとしてプロットに追加
        stats_text = (
            f"Number of facilities analyzed: {original_count}\n"
            f" (Number of outliers removed: {outlier_count})\n"
            f"Number of facilities plotted: {count_val}\n"
            f"Mean: {mean_val:.3f}\n"
            f"Median: {median_val:.3f}\n"
            f"Standard Deviation: {std_val:.3f}"
        )
        plt.text(0.97, 0.97, stats_text, transform=plt.gca().transAxes,
                 fontsize=11, verticalalignment='top', horizontalalignment='right',

                 bbox=dict(boxstyle='round,pad=0.5', fc='aliceblue', alpha=0.8))

        # 3. グラフの保存と表示
        output_path = '/home/ubuntu/cur/program/Analyisis_incineration/result/recalculated_utilization_histogram.png'
        plt.savefig(output_path)
        plt.close()
        
        print(f"新しいグラフ '{output_path}' を保存しました。")
        print("\n--- 発電利用率の統計情報（再計算後） ---")
        print(f"計算対象となった施設数: {original_count}")
        print(f"外れ値として除外された施設数: {outlier_count}")
        print(f"最終的なプロット対象施設数: {count_val}")
        print(f"平均値: {mean_val:.3f}")
        print(f"中央値: {median_val:.3f}")
        print(f"標準偏差: {std_val:.3f}")
        print()

    except FileNotFoundError:
        print(f"エラー: ファイル /home/ubuntu/cur/program/Analyisis_incineration/2022_1焼却施設.csv が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    replot_power_generation_utilization_histogram()

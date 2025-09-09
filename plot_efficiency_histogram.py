import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# 日本語フォントの設定
mpl.rcParams['font.family'] = 'DejaVu Sans, M+ 1C'
plt.rcParams['font.size'] = 12

def plot_power_generation_efficiency_histogram():
    """
    元のCSVデータから発電効率をプロットし、外れ値を除外した上でヒストグラムを作成する。
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
        df_power['発電効率'] = pd.to_numeric(df_power['発電能力_発電効率（仕様値・公称値）_％'], errors='coerce')

        # データが揃っている施設に絞る
        df_power.dropna(subset=['発電効率'], inplace=True)
        # 物理的にありえない値（0以下や100を超えるなど）を除外
        df_power = df_power[(df_power['発電効率'] > 0) & (df_power['発電効率'] < 100)]

        efficiency = df_power['発電効率']

        # IQR法による外れ値の検出と除外
        Q1 = efficiency.quantile(0.25)
        Q3 = efficiency.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        efficiency_filtered = efficiency[
            (efficiency >= lower_bound) & (efficiency <= upper_bound)
        ]

        # 1. 統計情報の計算
        mean_val = efficiency_filtered.mean()
        median_val = efficiency_filtered.median()
        std_val = efficiency_filtered.std()
        count_val = len(efficiency_filtered)
        original_count = len(efficiency)
        outlier_count = original_count - count_val

        # 2. ヒストグラムのプロット
        plt.figure(figsize=(12, 7))
        
        plt.hist(efficiency_filtered, bins=25, alpha=0.75, color='forestgreen', edgecolor='black')

        plt.title(f'Figure 1: Distribution of Power Generation Efficiency (Specification/Nameplate Values)')
        plt.xlabel('Power Generation Efficiency (Specification/Nameplate Values) [%]')
        plt.ylabel('Number of Facilities')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 統計情報をテキストとしてプロットに追加
        stats_text = (
            f"Number of facilities analyzed: {original_count}\n"
            f" (outliers excluded: {outlier_count})\n"
            f"Number of facilities plotted: {count_val}\n"
            f"Mean: {mean_val:.2f} %\n"
            f"Median: {median_val:.2f} %\n"
            f"Standard Deviation: {std_val:.2f} %"
        )
        plt.text(0.97, 0.97, stats_text, transform=plt.gca().transAxes,
                 fontsize=11, verticalalignment='top', horizontalalignment='right',
                 bbox=dict(boxstyle='round,pad=0.5', fc='honeydew', alpha=0.8))

        # 3. グラフの保存と表示
        output_path = '/home/ubuntu/cur/program/Analyisis_incineration/result/power_generation_efficiency_histogram.png'
        plt.savefig(output_path)
        plt.close()
        
        print(f"新しいグラフ '{output_path}' を保存しました。")
        print("\n--- 発電効率（仕様値・公称値）の統計情報 ---")
        print(f"計算対象となった施設数: {original_count}")
        print(f"外れ値として除外された施設数: {outlier_count}")
        print(f"最終的なプロット対象施設数: {count_val}")
        print(f"平均値: {mean_val:.2f} %")
        print(f"中央値: {median_val:.2f} %")
        print(f"標準偏差: {std_val:.2f} %")
        print()

    except FileNotFoundError:
        print(f"エラー: ファイル /home/ubuntu/cur/program/Analyisis_incineration/2022_1焼却施設.csv が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    plot_power_generation_efficiency_histogram()

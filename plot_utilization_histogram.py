import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# 日本語フォントの設定
mpl.rcParams['font.family'] = 'DejaVu Sans, M+ 1C'
plt.rcParams['font.size'] = 12

def plot_power_generation_utilization_histogram():
    """
    発電利用率のヒストグラムを作成し、統計情報を表示する。
    """
    try:
        # CSVファイルの読み込み
        df_filtered = pd.read_csv('/home/ubuntu/cur/program/Analyisis_incineration/result/power_generation_results_filtered.csv', encoding='utf-8-sig')

        # '発電利用率' のデータを抽出
        utilization_rate = df_filtered['発電利用率']

        # 1. 統計情報の計算
        mean_val = utilization_rate.mean()
        median_val = utilization_rate.median()
        std_val = utilization_rate.std()
        count_val = len(utilization_rate)

        # 2. ヒストグラムのプロット
        plt.figure(figsize=(10, 6))
        
        plt.hist(utilization_rate, bins=20, alpha=0.7, color='green', edgecolor='black')

        plt.title(f'図1: 発電利用率の分布')
        plt.xlabel('発電利用率')
        plt.ylabel('施設数')
        plt.grid(True)

        # 統計情報をテキストとしてプロットに追加
        stats_text = (
            f"施設数: {count_val}\n"
            f"平均値: {mean_val:.3f}\n"
            f"中央値: {median_val:.3f}\n"
            f"標準偏差: {std_val:.3f}"
        )
        plt.text(0.95, 0.95, stats_text, transform=plt.gca().transAxes,
                 fontsize=10, verticalalignment='top', horizontalalignment='right',
                 bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.6))

        # 3. グラフの保存と表示
        output_path = '/home/ubuntu/cur/program/Analyisis_incineration/result/power_generation_utilization_rate_histogram.png'
        plt.savefig(output_path)
        plt.close()
        
        print(f"グラフ '{output_path}' を保存しました。")
        print("\n--- 発電利用率の統計情報 ---")
        print(f"施設数: {count_val}")
        print(f"平均値: {mean_val:.3f}")
        print(f"中央値: {median_val:.3f}")
        print(f"標準偏差: {std_val:.3f}")
        print()

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    plot_power_generation_utilization_histogram()
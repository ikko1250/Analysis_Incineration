import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import pearsonr

# 日本語フォントの設定
mpl.rcParams['font.family'] = 'DejaVu Sans, M+ 1C'
plt.rcParams['font.size'] = 12

# CSVファイルを読み込み
df_filtered = pd.read_csv('/home/ubuntu/cur/program/Analyisis_incineration/result/heat_utilization_results_filtered.csv', encoding='utf-8-sig')
df_all = pd.read_csv('/home/ubuntu/cur/program/Analyisis_incineration/result/heat_utilization_results_all.csv', encoding='utf-8-sig')

# 分類マスクの作成
hot_water_steam_mask = ((~df_filtered['余熱利用_場内温水'].isnull()) & (df_filtered['余熱利用_場内温水'] != '')) | \
                       ((~df_filtered['余熱利用_場内蒸気'].isnull()) & (df_filtered['余熱利用_場内蒸気'] != ''))

power_mask = ((~df_filtered['余熱利用_発電場内'].isnull()) & (df_filtered['余熱利用_発電場内'] != '')) | \
             ((~df_filtered['余熱利用_発電場外'].isnull()) & (df_filtered['余熱利用_発電場外'] != ''))

external_heat_mask = ((~df_filtered['余熱利用_場外温水'].isnull()) & (df_filtered['余熱利用_場外温水'] != '')) | \
                     ((~df_filtered['余熱利用_場外蒸気'].isnull()) & (df_filtered['余熱利用_場外蒸気'] != ''))

# 分類データの準備
categories = ['Hot Water/Steam', 'Power Generation', 'External Heat']
category_masks = [hot_water_steam_mask, power_mask, external_heat_mask]
colors = ['red', 'green', 'blue']

print(f"\n=== 余熱利用状況による分類結果 ===")
print(f"総施設数（外れ値除去後）: {len(df_filtered)}")
for i, (cat, mask) in enumerate(zip(categories, category_masks)):
    print(f"{cat}: {mask.sum()} 施設 ({mask.sum()/len(df_filtered)*100:.1f}%)")

# プロット作成（縦3行 × 横5列）
plt.figure(figsize=(25, 18))

for row, (category, mask, color) in enumerate(zip(categories, category_masks, colors)):
    # データの抽出
    cat_annual_heat = df_filtered['年間発熱量_MJ'][mask]
    cat_utilization_rate = df_filtered['余熱利用率'][mask]

    # 列1: 外れ値除去前の散布図（全データ）
    plt.subplot(3, 5, row*5 + 1)
    plt.scatter(df_all['年間発熱量_MJ'], df_all['余熱利用率'], alpha=0.3, color='lightgray', label='All data')
    plt.scatter(cat_annual_heat, cat_utilization_rate, alpha=0.6, color=color, label=category)
    plt.xlabel('Annual Heat Generation (MJ)')
    plt.ylabel('Utilization Rate')
    plt.title(f'{category}\nBefore Outlier Removal')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # 列2: 外れ値除去後の散布図
    plt.subplot(3, 5, row*5 + 2)
    plt.scatter(df_filtered['年間発熱量_MJ'], df_filtered['余熱利用率'], alpha=0.3, color='lightgray', label='All filtered')
    plt.scatter(cat_annual_heat, cat_utilization_rate, alpha=0.6, color=color, label=category)
    plt.xlabel('Annual Heat Generation (MJ)')
    plt.ylabel('Utilization Rate')
    plt.title(f'{category}\nAfter Outlier Removal')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # 列3: 外れ値除去後の散布図（通常スケール）
    plt.subplot(3, 5, row*5 + 3)
    plt.scatter(cat_annual_heat, cat_utilization_rate, alpha=0.6, color=color)
    plt.xlabel('Annual Heat Generation (MJ)')
    plt.ylabel('Utilization Rate')

    if len(cat_annual_heat) > 1 and len(cat_utilization_rate) > 1:
        corr, p_value = pearsonr(cat_annual_heat, cat_utilization_rate)
        plt.title(f'{category}\nAfter Removal (Normal Scale)\nCorr: {corr:.2f}, P: {p_value:.3f}')
    else:
        plt.title(f'{category}\nAfter Removal (Normal Scale)')
    plt.grid(True, alpha=0.3)

    # 列4: 外れ値除去後の散布図（対数スケール）
    plt.subplot(3, 5, row*5 + 4)
    plt.scatter(cat_annual_heat, cat_utilization_rate, alpha=0.6, color=color)
    plt.xlabel('Annual Heat Generation (MJ)')
    plt.ylabel('Utilization Rate')
    if len(cat_annual_heat) > 1 and len(cat_utilization_rate) > 1:
        corr, p_value = pearsonr(cat_annual_heat, cat_utilization_rate)
        plt.title(f'{category}\nAfter Removal (Log Scale)\nCorr: {corr:.2f}, P: {p_value:.3f}')
    else:
        plt.title(f'{category}\nAfter Removal (Log Scale)')
    plt.xscale('log')
    plt.grid(True, alpha=0.3)

    # 列5: 利用率のヒストグラム
    plt.subplot(3, 5, row*5 + 5)
    plt.hist(cat_utilization_rate, bins=20, alpha=0.7, color=color, edgecolor='black')
    plt.xlabel('Utilization Rate')
    plt.ylabel('Frequency')
    plt.title(f'{category}\nUtilization Rate Distribution')
    plt.grid(True, alpha=0.3)

    # 統計情報の表示
    if len(cat_annual_heat) > 0:
        print(f"\n=== {category} 統計情報 ===")
        print(f"施設数: {len(cat_annual_heat)}")
        print(f"年間発熱量平均: {cat_annual_heat.mean():.2e} MJ")
        print(f"利用率平均: {cat_utilization_rate.mean():.4f}")
        print(f"利用率中央値: {cat_utilization_rate.median():.4f}")
        print(f"利用率標準偏差: {cat_utilization_rate.std():.4f}")

plt.tight_layout()
plt.savefig('/home/ubuntu/cur/program/Analyisis_incineration/result/heat_utilization_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

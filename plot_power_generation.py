import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import pearsonr

# 日本語フォントの設定
mpl.rcParams['font.family'] = 'DejaVu Sans, M+ 1C'
plt.rcParams['font.size'] = 12

# CSVファイルを読み込み
df_filtered = pd.read_csv('/home/ubuntu/cur/program/Analyisis_incineration/result/power_generation_results_filtered.csv', encoding='utf-8-sig')
df_all = pd.read_csv('/home/ubuntu/cur/program/Analyisis_incineration/result/power_generation_results_all.csv', encoding='utf-8-sig')

# プロット作成（縦2行 × 横5列）
fig, axes = plt.subplots(2, 5, figsize=(25, 12))
fig.suptitle('Power Generation Analysis', fontsize=16)

# --- 1行目: 発電利用率 ---

# データの抽出
annual_heat_all = df_all['年間発熱量_MJ']
utilization_rate_all = df_all['発電利用率']
annual_heat_filtered = df_filtered['年間発熱量_MJ']
utilization_rate_filtered = df_filtered['発電利用率']

# 列1: 外れ値除去前の散布図（全データ）
axes[0, 0].scatter(annual_heat_all, utilization_rate_all, alpha=0.5)
axes[0, 0].set_xlabel('Annual Heat Generation (MJ)')
axes[0, 0].set_ylabel('Power Generation Utilization Rate')
axes[0, 0].set_title('All Data\nBefore Outlier Removal')
axes[0, 0].grid(True, alpha=0.3)

# 列2: 外れ値除去後の散布図
axes[0, 1].scatter(annual_heat_filtered, utilization_rate_filtered, alpha=0.5, color='green')
axes[0, 1].set_xlabel('Annual Heat Generation (MJ)')
axes[0, 1].set_ylabel('Power Generation Utilization Rate')
axes[0, 1].set_title('Filtered Data\nAfter Outlier Removal')
axes[0, 1].grid(True, alpha=0.3)

# 列3: 外れ値除去後の散布図（通常スケール）
axes[0, 2].scatter(annual_heat_filtered, utilization_rate_filtered, alpha=0.6, color='green')
axes[0, 2].set_xlabel('Annual Heat Generation (MJ)')
axes[0, 2].set_ylabel('Power Generation Utilization Rate')
corr, p_value = pearsonr(annual_heat_filtered, utilization_rate_filtered)
axes[0, 2].set_title(f'Filtered Data (Normal Scale)\nCorr: {corr:.2f}, P: {p_value:.3f}')
axes[0, 2].grid(True, alpha=0.3)

# 列4: 外れ値除去後の散布図（対数スケール）
axes[0, 3].scatter(annual_heat_filtered, utilization_rate_filtered, alpha=0.6, color='green')
axes[0, 3].set_xlabel('Annual Heat Generation (MJ)')
axes[0, 3].set_ylabel('Power Generation Utilization Rate')
axes[0, 3].set_xscale('log')
corr, p_value = pearsonr(annual_heat_filtered, utilization_rate_filtered)
axes[0, 3].set_title(f'Filtered Data (Log Scale)\nCorr: {corr:.2f}, P: {p_value:.3f}')
axes[0, 3].grid(True, alpha=0.3)

# 列5: 利用率のヒストグラム
axes[0, 4].hist(utilization_rate_filtered, bins=20, alpha=0.7, color='green', edgecolor='black')
axes[0, 4].set_xlabel('Power Generation Utilization Rate')
axes[0, 4].set_ylabel('Frequency')
axes[0, 4].set_title('Utilization Rate Distribution')
axes[0, 4].grid(True, alpha=0.3)

# --- 2行目: 設備利用率 ---

# データの抽出
facility_utilization_rate_all = df_all['設備利用率']
facility_utilization_rate_filtered = df_filtered['設備利用率']

# 列1: 外れ値除去前の散布図（全データ）
axes[1, 0].scatter(annual_heat_all, facility_utilization_rate_all, alpha=0.5, color='purple')
axes[1, 0].set_xlabel('Annual Heat Generation (MJ)')
axes[1, 0].set_ylabel('Facility Utilization Rate')
axes[1, 0].set_title('All Data\nBefore Outlier Removal')
axes[1, 0].grid(True, alpha=0.3)

# 列2: 外れ値除去後の散布図
axes[1, 1].scatter(annual_heat_filtered, facility_utilization_rate_filtered, alpha=0.5, color='orange')
axes[1, 1].set_xlabel('Annual Heat Generation (MJ)')
axes[1, 1].set_ylabel('Facility Utilization Rate')
axes[1, 1].set_title('Filtered Data\nAfter Outlier Removal')
axes[1, 1].grid(True, alpha=0.3)

# 列3: 外れ値除去後の散布図（通常スケール）
axes[1, 2].scatter(annual_heat_filtered, facility_utilization_rate_filtered, alpha=0.6, color='orange')
axes[1, 2].set_xlabel('Annual Heat Generation (MJ)')
axes[1, 2].set_ylabel('Facility Utilization Rate')
corr, p_value = pearsonr(annual_heat_filtered, facility_utilization_rate_filtered)
axes[1, 2].set_title(f'Filtered Data (Normal Scale)\nCorr: {corr:.2f}, P: {p_value:.3f}')
axes[1, 2].grid(True, alpha=0.3)

# 列4: 外れ値除去後の散布図（対数スケール）
axes[1, 3].scatter(annual_heat_filtered, facility_utilization_rate_filtered, alpha=0.6, color='orange')
axes[1, 3].set_xlabel('Annual Heat Generation (MJ)')
axes[1, 3].set_ylabel('Facility Utilization Rate')
axes[1, 3].set_xscale('log')
corr, p_value = pearsonr(annual_heat_filtered, facility_utilization_rate_filtered)
axes[1, 3].set_title(f'Filtered Data (Log Scale)\nCorr: {corr:.2f}, P: {p_value:.3f}')
axes[1, 3].grid(True, alpha=0.3)

# 列5: 利用率のヒストグラム
axes[1, 4].hist(facility_utilization_rate_filtered, bins=20, alpha=0.7, color='orange', edgecolor='black')
axes[1, 4].set_xlabel('Facility Utilization Rate')
axes[1, 4].set_ylabel('Frequency')
axes[1, 4].set_title('Facility Utilization Rate Distribution')
axes[1, 4].grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('/home/ubuntu/cur/program/Analyisis_incineration/result/power_generation_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

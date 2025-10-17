import os
from datetime import datetime

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import japanize_matplotlib


def pick_existing(cols, options):
    for name in options:
        if name in cols:
            return name
    return None


def main():
    # CSVのフルパス（必要に応じて書き換えてください）
    CSV_ABS_PATH = "/home/ubuntu/cur/program/Analyisis_incineration/神戸電鉄_乗降客数.csv"

    if not os.path.exists(CSV_ABS_PATH):
        raise FileNotFoundError(f"CSVが見つかりません: {CSV_ABS_PATH}")

    # 結果出力ディレクトリ
    out_dir = os.path.join(os.path.dirname(__file__), "result")
    os.makedirs(out_dir, exist_ok=True)

    # 指定フォント設定（簡潔）
    plt.rcParams['font.sans-serif'] = ['M+ 1C']
    plt.rcParams['axes.unicode_minus'] = False

    # 読み込み
    df = pd.read_csv(CSV_ABS_PATH, encoding="utf-8")

    # 対象列名（存在するものを使用）
    x_options = ["年間処理量(t/day)", "年間処理量(t/year)"]
    y_options = ["発電量実績(MWh/year)"]

    x_col = pick_existing(df.columns, x_options)
    y_col = pick_existing(df.columns, y_options)
    if x_col is None or y_col is None:
        raise KeyError(
            f"必要な列が見つかりません。x候補: {x_options} / y候補: {y_options} / 実列: {list(df.columns)}"
        )

    # 数値化 & 欠損除外
    x = pd.to_numeric(df[x_col], errors="coerce")
    y = pd.to_numeric(df[y_col], errors="coerce")
    valid = pd.DataFrame({x_col: x, y_col: y}).dropna()

    # 相関係数（Pearson）
    corr = valid[x_col].corr(valid[y_col]) if not valid.empty else float("nan")

    # 可視化（散布図: seaborn.relplot）
    sns.set_theme(style="whitegrid")
    g = sns.relplot(
        data=valid,
        x=x_col,
        y=y_col,
        kind="scatter",
        height=5,
        aspect=1.3,
        color="#1f77b4",
    )
    title = f"{x_col} と {y_col} の関係 (n={len(valid)})\nPearson r = {corr:.3f}"
    g.set_axis_labels(x_col, y_col)
    g.figure.suptitle(title, y=1.03)

    # 保存
    stem = os.path.splitext(os.path.basename(CSV_ABS_PATH))[0]
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(out_dir, f"{stem}_relplot_{ts}.png")
    g.figure.savefig(out_path, bbox_inches="tight", dpi=150)
    print(f"相関係数 (Pearson): {corr:.4f}")
    print(f"散布図を保存しました: {out_path}")


if __name__ == "__main__":
    main()

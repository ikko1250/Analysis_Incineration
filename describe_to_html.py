import os
from datetime import datetime
import pandas as pd


def main():
    # 入力CSV（既定: リポジトリのデータ）
    # フルパスをベタ書き（必要に応じて書き換えてください）
    CSV_ABS_PATH = "/home/ubuntu/cur/program/Analyisis_incineration/神戸電鉄_乗降客数.csv"

    csv_path = CSV_ABS_PATH

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSVが見つかりません: {csv_path}")

    # 出力先
    out_dir = os.path.join(os.path.dirname(__file__), "result")
    os.makedirs(out_dir, exist_ok=True)
    # 出力ファイル名: CSV名 + 日付時刻（重複回避）
    csv_base = os.path.basename(csv_path)
    csv_stem, _ = os.path.splitext(csv_base)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_filename = f"{csv_stem}_{ts}_describe.html"
    out_path = os.path.join(out_dir, out_filename)

    # 読み込み
    df = pd.read_csv(csv_path, encoding="utf-8")

    # 数値化を試みる（列ごとに to_numeric）
    df_num = df.apply(pd.to_numeric, errors="coerce")

    # describe（数値列のみ）
    desc = df_num.describe().transpose()

    # 特定列（発電効率: インデックス40）があれば個別の統計も出力
    extra_html = ""
    if df.shape[1] > 40:
        col_name = df.columns[40]
        series_num = pd.to_numeric(df.iloc[:, 40], errors="coerce")
        valid = series_num.dropna()
        if not valid.empty:
            sdesc = valid.describe()
            # 範囲別分布
            bins_count = {
                "10%未満": (valid < 10).sum(),
                "10-15%": ((valid >= 10) & (valid < 15)).sum(),
                "15-20%": ((valid >= 15) & (valid < 20)).sum(),
                "20-25%": ((valid >= 20) & (valid < 25)).sum(),
                "25%以上": (valid >= 25).sum(),
            }
            bins_df = (
                pd.Series(bins_count, name="施設数")
                .rename_axis("発電効率の範囲")
                .reset_index()
            )

            extra_html = f"""
            <h2>発電効率の詳細 ({col_name})</h2>
            <p>有効データ数: {valid.size} / 総行数: {series_num.size}</p>
            {sdesc.to_frame(name=col_name).to_html(classes='data', border=0)}
            <h3>範囲別分布</h3>
            {bins_df.to_html(index=False, classes='data', border=0)}
            """

    # HTML組み立て
    html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="utf-8" />
        <title>describe レポート</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', Meiryo, Arial, sans-serif; margin: 24px; }}
            h1 {{ margin-bottom: 8px; }}
            .path {{ color: #666; font-size: 0.9em; margin-bottom: 24px; }}
            table.data {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
            table.data th, table.data td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: right; }}
            table.data th {{ background: #f7f7f7; text-align: center; }}
            .note {{ color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>describe レポート</h1>
        <div class="path">CSV: {csv_path}</div>

        <h2>数値列の基本統計</h2>
        {desc.to_html(classes='data', border=0)}

        {extra_html}

        <p class="note">本レポートは pandas.DataFrame.describe() に基づいて自動生成されています。</p>
    </body>
    </html>
    """

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTMLを書き出しました: {out_path}")


if __name__ == "__main__":
    main()

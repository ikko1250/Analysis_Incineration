import os
import argparse
import pandas as pd


# Defaults aligned with 運営体分析.py
DATA_PATH = "/home/ubuntu/cur/program/Analyisis_incineration/2022_1焼却施設.csv"
OUT_DIR = "/home/ubuntu/cur/program/Analyisis_incineration/result"
TARGET_COL = "ごみ処理事業実施方式"


def load_data(path: str) -> pd.DataFrame:
    # UTF-8 with or without BOM
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="utf-8")


def extract_main_scheme(val: str) -> str:
    """Return the main scheme before '（...）'.

    Examples:
      - "DB（公設公営、運転委託）" -> "DB"
      - "PFI（DBO）" -> "PFI"
    Empty/NaN -> "不明・未記載"
    """
    if not isinstance(val, str) or val.strip() == "":
        return "不明・未記載"
    v = val.strip()
    if "（" in v:
        return v.split("（", 1)[0]
    return v


def normalize_series_for_raw_match(s: pd.Series) -> pd.Series:
    return (
        s.fillna("不明・未記載")
        .astype(str)
        .str.strip()
        .replace({"": "不明・未記載"})
    )


def normalize_series_for_grouped_match(s: pd.Series) -> pd.Series:
    grouped = s.fillna("").astype(str).map(extract_main_scheme)
    return grouped.replace({"": "不明・未記載"})


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "ごみ処理事業実施方式のうち、指定した方式のみを抽出して1つのCSVに出力する"
        )
    )
    p.add_argument(
        "methods",
        nargs="+",
        help=(
            "抽出対象の方式名（複数可）。"
            "--match grouped の場合は 'DB', 'PFI' など括弧前を指定"
        ),
    )
    p.add_argument(
        "--input",
        default=DATA_PATH,
        help=f"入力CSVのパス（既定: {DATA_PATH}）",
    )
    p.add_argument(
        "--output",
        default=None,
        help=(
            "出力CSVのパス。未指定時は result/filtered_implementation_methods.csv を使用"
        ),
    )
    p.add_argument(
        "--column",
        default=TARGET_COL,
        help=f"抽出対象のカラム名（既定: {TARGET_COL}）",
    )
    p.add_argument(
        "--match",
        choices=["raw", "grouped"],
        default="raw",
        help=(
            "raw: カラムの表記そのままで一致。grouped: 括弧前でグルーピングして一致"
        ),
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = args.output or os.path.join(OUT_DIR, "filtered_implementation_methods.csv")

    df = load_data(args.input)
    if args.column not in df.columns:
        raise SystemExit(f"指定カラムが見つかりません: {args.column}")

    methods = [m.strip() for m in args.methods if str(m).strip() != ""]
    if not methods:
        raise SystemExit("抽出対象の方式名が空です。1つ以上指定してください。")

    s = df[args.column]
    if args.match == "raw":
        key_series = normalize_series_for_raw_match(s)
    else:
        key_series = normalize_series_for_grouped_match(s)

    include_set = set(methods)
    mask = key_series.isin(include_set)
    filtered = df.loc[mask].copy()

    # Save
    filtered.to_csv(out_path, index=False, encoding="utf-8-sig")

    # Report
    unique_found = sorted(set(key_series[mask]))
    print(
        "抽出完了: 総件数=", len(df),
        " 抽出件数=", len(filtered),
        " 一致方式=", unique_found,
    )
    print("出力CSV:", out_path)


if __name__ == "__main__":
    main()


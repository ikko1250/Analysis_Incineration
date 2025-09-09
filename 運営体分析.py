import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from matplotlib import font_manager
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
import argparse


JP_FONT_PROP: FontProperties | None = None  # set by setup_japanese_font


def setup_japanese_font() -> None:
	"""Pick and apply a JP-capable font to avoid DejaVu fallback."""
	candidate_paths = [
		"/usr/share/fonts/truetype/mplus/mplus-1c-regular.ttf",
		"/usr/share/fonts/truetype/mplus/mplus-1c-bold.ttf",
		"/usr/share/fonts/truetype/mplus/mplus-1c-medium.ttf",
		"/usr/share/fonts/truetype/mplus/mplus-1p-regular.ttf",
		"/usr/share/fonts/truetype/mplus/mplus-1p-bold.ttf",
		"/usr/share/fonts/truetype/mplus/mplus-1p-medium.ttf",
		"/usr/share/fonts/opentype/mplus/MPLUS1c-Regular.otf",
		"/usr/share/fonts/opentype/mplus/MPLUS1c-Bold.otf",
		"/usr/share/fonts/opentype/mplus/MPLUS1p-Regular.otf",
		"/usr/share/fonts/opentype/mplus/MPLUS1p-Bold.otf",
	]
	candidate_families = [
		"M PLUS 1c", "M PLUS 1p", "M+ 1c", "M+ 1p",
		"Noto Sans CJK JP", "Noto Sans JP",
		"IPAexGothic", "IPAGothic", "TakaoPGothic",
	]

	chosen_family, resolved_path = None, None

	# 1) Prefer loading by file path to get an exact family name
	for p in candidate_paths:
		if not os.path.exists(p):
			continue
		try:
			font_manager.fontManager.addfont(p)
			if not chosen_family:
				prop = font_manager.FontProperties(fname=p)
				chosen_family, resolved_path = prop.get_name(), p
		except Exception:
			pass

	# 2) Fallback: try well-known family names
	if not chosen_family:
		for fam in candidate_families:
			try:
				font_manager.findfont(mpl.font_manager.FontProperties(family=fam), fallback_to_default=False)
				chosen_family = fam
				break
			except Exception:
				pass

	# 3) Apply rcParams
	if chosen_family:
		rcParams.update({
			'font.family': [chosen_family],
			'font.sans-serif': [
				chosen_family,
				'Noto Sans CJK JP', 'Noto Sans JP',
				'IPAexGothic', 'IPAGothic', 'TakaoPGothic',
			],
			'axes.unicode_minus': False,
			'axes.titleweight': 'normal',
			'font.weight': 'normal',
		})
		try:
			resolved = font_manager.findfont(mpl.font_manager.FontProperties(family=chosen_family), fallback_to_default=False)
		except Exception:
			resolved = resolved_path or ''
		print(f"Using Japanese font family: {chosen_family} -> {resolved}")

		global JP_FONT_PROP
		JP_FONT_PROP = FontProperties(fname=resolved_path) if resolved_path and os.path.exists(resolved_path) else FontProperties(family=chosen_family)
	else:
		# Keep defaults but warn user
		print("Warning: Could not find a Japanese font. Matplotlib may fall back to DejaVu Sans.")
		JP_FONT_PROP = None


# Configure font at import time so all plots use it
setup_japanese_font()

DATA_PATH = "/home/ubuntu/cur/program/Analyisis_incineration/2022_1焼却施設.csv"
OUT_DIR = "/home/ubuntu/cur/program/Analyisis_incineration/result"
os.makedirs(OUT_DIR, exist_ok=True)

TARGET_COL = "ごみ処理事業実施方式"


def load_data(path: str) -> pd.DataFrame:
	# 文字コードはUTF-8系。BOM付きにも対応
	try:
		return pd.read_csv(path, encoding="utf-8-sig")
	except UnicodeDecodeError:
		return pd.read_csv(path, encoding="utf-8")


def value_counts_raw(df: pd.DataFrame, col: str) -> pd.Series:
    """Return value counts without sorting (keeps appearance/category order).

    Note: pandas.value_counts(sort=False) keeps the original order of appearance
    or the categorical order if the Series has categorical dtype.
    """
    s = (
        df[col]
        .fillna("不明・未記載")
        .astype(str)
        .str.strip()
        .replace({"": "不明・未記載"})
    )
    return s.value_counts(sort=False)


def extract_main_scheme(val: str) -> str:
	# 例: "DB（公設公営、運転委託）" -> "DB"
	if not isinstance(val, str) or val.strip() == "":
		return "不明・未記載"
	v = val.strip()
	if "（" in v:
		return v.split("（", 1)[0]
	return v


def value_counts_grouped_raw(df: pd.DataFrame, col: str) -> pd.Series:
    """Return grouped value counts without sorting."""
    grouped = df[col].fillna("").astype(str).map(extract_main_scheme)
    grouped = grouped.replace({"": "不明・未記載"})
    return grouped.value_counts(sort=False)


def plot_barh_counts(counts: pd.Series, title: str, filename: str):
	plt.figure(figsize=(10, max(4, 0.5 * len(counts))))
	sns.set_style("whitegrid")
	ax = sns.barplot(x=counts.values, y=counts.index, palette="Blues_d")

	# Titles/labels
	ax.set_title(title, fontsize=14)
	ax.set_xlabel("施設数")
	ax.set_ylabel("")

	# Annotations on bars
	annots = [
		ax.text(v + max(counts.values) * 0.01, i, f"{int(v)}", va="center")
		for i, v in enumerate(counts.values)
	]

	# Enforce JP font everywhere if available (preserve current sizes)
	if JP_FONT_PROP is not None:
		texts = [ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels() + annots
		for t in texts:
			size = t.get_fontsize()
			t.set_fontproperties(JP_FONT_PROP)
			t.set_fontsize(size)

	plt.tight_layout()
	out_path = os.path.join(OUT_DIR, filename)
	plt.savefig(out_path)
	plt.close()
	print(f"グラフを保存しました: {out_path}")


def save_counts_csv(counts: pd.Series, filename: str):
	out_path = os.path.join(OUT_DIR, filename)
	counts.rename("count").to_frame().to_csv(out_path, encoding="utf-8-sig")
	print(f"集計CSVを保存しました: {out_path}")


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="運営体分析: 実施方式の件数を集計・可視化します")
	parser.add_argument(
		"--sort-by-counts",
		action="store_true",
		help="カテゴリを件数の多い順に並べ替えて出力・プロットする",
	)
	return parser.parse_args()


def main():
	args = parse_args()
	df = load_data(DATA_PATH)

	# 参考用に先頭を出力
	columns = ["施設名称", "施設全体の処理能力_t/日", "炉型式", TARGET_COL]
	pd.set_option("display.max_columns", None)
	print(df[columns].head())

	# 1) 実施方式（フル表記）の件数
	counts_full = value_counts_raw(df, TARGET_COL)
	if args.sort_by_counts:
		counts_full = counts_full.sort_values(ascending=False)
	save_counts_csv(counts_full, "implementation_method_counts_full.csv")
	title_full = "図: ごみ処理事業実施方式（フル表記）の内訳" + ("（降順）" if args.sort_by_counts else "")
	plot_barh_counts(
		counts_full,
		title=title_full,
		filename="implementation_method_counts_full.png",
	)

	# 2) 実施方式（括弧前でグルーピング）の件数
	counts_group = value_counts_grouped_raw(df, TARGET_COL)
	if args.sort_by_counts:
		counts_group = counts_group.sort_values(ascending=False)
	save_counts_csv(counts_group, "implementation_method_counts_grouped.csv")
	title_group = "図: ごみ処理事業実施方式（方式の種類別）の内訳" + ("（降順）" if args.sort_by_counts else "")
	plot_barh_counts(
		counts_group,
		title=title_group,
		filename="implementation_method_counts_grouped.png",
	)


if __name__ == "__main__":
	main()

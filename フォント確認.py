import os, glob
import matplotlib as mpl
import matplotlib.font_manager as fm

# キャッシュディレクトリを取得
cache_dir = mpl.get_cachedir()
print("matplotlib cache dir:", cache_dir)

# フォントキャッシュの候補ファイルを削除
patterns = ['fontList*', 'fontlist*', 'font-v*.json', '*.cache']
for p in patterns:
    for f in glob.glob(os.path.join(cache_dir, p)):
        try:
            os.remove(f)
            print("removed:", f)
        except PermissionError:
            print("permission denied:", f)

# プロセス内で再構築（確実に反映させるには Python / カーネル再起動を推奨）
fm.fontManager = fm.FontManager()   # FontManager を新しく作る -> フォント一覧を再読み込み
# または（古い/private API）: fm._rebuild()
print("fontManager rebuilt.")
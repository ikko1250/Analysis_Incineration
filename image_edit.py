from PIL import Image, ImageDraw, ImageFont

def add_text_to_image(image_path, font_path, output_path):
    """
    画像に翻訳された日本語テキストを追加します。

    Args:
        image_path (str): 元の画像のパス。
        font_path (str): 日本語フォントファイルのパス。
        output_path (str): テキストを追加した画像の保存パス。
    """
    try:
        # 画像を開く
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        # 日本語フォントを読み込む
        font_title = ImageFont.truetype(font_path, 28)
        font_legend = ImageFont.truetype(font_path, 18)
        font_xaxis = ImageFont.truetype(font_path, 16)

    except FileNotFoundError as e:
        print(f"エラー: ファイルが見つかりません。 -> {e}")
        print("スクリプト、画像ファイル、フォントファイルが同じディレクトリにあるか確認してください。")
        return

    # テキストと描画位置のリスト
    # 辞書のキー: text, pos (テキスト描画位置), bg_box (背景の白い四角の位置), font
    texts_to_add = [
        # タイトル
        {"text": "生産および売却GWhの推移", "pos": (250, 15), "bg_box": [200, 10, 680, 50], "font": font_title},
        # X軸ラベル
        {"text": "22年 年初来累計", "pos": (70, 485), "bg_box": [65, 485, 165, 510], "font": font_xaxis},
        {"text": "23年 年初来累計", "pos": (270, 485), "bg_box": [265, 485, 365, 510], "font": font_xaxis},
        {"text": "24年 年初来累計", "pos": (470, 485), "bg_box": [465, 485, 565, 510], "font": font_xaxis},
        {"text": "25年 予算", "pos": (675, 485), "bg_box": [670, 485, 745, 510], "font": font_xaxis},
        # 凡例
        {"text": "生産GWh", "pos": (355, 520), "bg_box": [345, 518, 455, 540], "font": font_legend},
        {"text": "売却GWh", "pos": (505, 520), "bg_box": [495, 518, 605, 540], "font": font_legend},
    ]

    # 各テキストを描画
    for item in texts_to_add:
        # 元のテキストを隠すために白い四角を描画
        draw.rectangle(item["bg_box"], fill="white", outline="white")
        # 新しいテキストを描画
        draw.text(item["pos"], item["text"], font=item["font"], fill="black")

    # 画像を保存
    image.save(output_path)
    print(f"処理が完了し、画像を '{output_path}' として保存しました。")

if __name__ == '__main__':
    # --- 設定 ---
    # 元の画像ファイル名
    input_image_file = 'image.png'
    # 使用する日本語フォントファイル名
    font_file = 'NotoSansJP-Regular.ttf'
    # 出力するファイル名
    output_image_file = 'translated_chart_jp.png'
    # --- 設定ここまで ---

    add_text_to_image(input_image_file, font_file, output_image_file)
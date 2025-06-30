import csv

def filter_csv_columns(input_path, output_path, columns_to_keep, mandatory_columns):
    """
    CSVファイルから指定されたカラムを抽出し、必須カラムに値を持つ行のみを新しいCSVファイルとして保存する。

    Args:
        input_path (str): 入力CSVファイルのパス。
        output_path (str): 出力CSVファイルのパス。
        columns_to_keep (list): 抽出するカラム名のリスト。
        mandatory_columns (list): 値が必須なカラム名のリスト。
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            header = next(reader)
            
            # 維持したいカラムと必須カラムのインデックスを検索
            try:
                indices_to_keep = [header.index(col) for col in columns_to_keep]
                mandatory_indices = [header.index(col) for col in mandatory_columns]
            except ValueError as e:
                print(f"エラー: 指定されたカラムが見つかりません - {e}")
                return

            # 新しいヘッダーを書き込む
            new_header = [header[i] for i in indices_to_keep]
            writer.writerow(new_header)
            
            # 各行を処理
            for row in reader:
                # 必須カラムのいずれかに値があるかチェック
                has_value_in_mandatory_columns = False
                for index in mandatory_indices:
                    if row[index].strip():  # 空白文字を除去して空でないかチェック
                        has_value_in_mandatory_columns = True
                        break
                
                # 必須カラムのいずれかに値があれば、指定されたカラムのデータのみを書き込む
                if has_value_in_mandatory_columns:
                    new_row = [row[i] for i in indices_to_keep]
                    writer.writerow(new_row)
                
        print(f"処理が完了しました。出力ファイル: {output_path}")

    except FileNotFoundError:
        print(f"エラー: 入力ファイルが見つかりません - {input_path}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    # --- 入力ファイルと出力ファイルをここで指定 ---
    INPUT_FILE_PATH = "2022_1焼却施設.csv"
    OUTPUT_FILE_PATH = "formatted_data.csv"
    # ------------------------------------

    # --- 抽出したいカラムをここで指定 ---
    COLUMNS_TO_EXTRACT = [
        "都道府県名", "地方公共団体名", "施設名称", "年間処理量_t/年度", 
        "処理方式", "炉型式", "ごみ処理事業実施方式", "炉数", "使用開始年度", 
        "余熱利用量（仕様値・公称値）_余熱利用量_MJ", 
        "余熱利用量（仕様値・公称値）_うち外部熱供給量_MJ", 
        "余熱利用量（実績値）_余熱利用量_MJ", 
        "余熱利用量（実績値）_うち外部熱供給量_MJ", 
        "発電能力_発電能力_kW", "発電能力_発電効率（仕様値・公称値）_％", 
        "発電能力_総発電量（実績値）_MWh", "発電能力_うち外部供給量（実績値）_MWh", 
        "余剰電力利用（売電）_売電量_MWh/年", "余剰電力利用（売電）_売電収入_円/年", 
        "余剰電力利用（売電）_売電価格(単価)_固定価格_円/kWh", 
        "余剰電力利用（売電）_売電価格(単価)_重負荷_円/kWh", 
        "余剰電力利用（売電）_売電価格(単価)_昼間_円/kWh", 
        "余剰電力利用（売電）_売電価格(単価)_夜間_円/kWh", 
        "ごみ組成分析結果（乾ベース）_合計_％", "ごみ組成分析結果（乾ベース）_紙・布類_％", 
        "ごみ組成分析結果（乾ベース）_ﾋﾞﾆｰﾙ、合成樹脂、ｺﾞﾑ、皮革類_％", 
        "ごみ組成分析結果（乾ベース）_木、竹、わら類_％", 
        "ごみ組成分析結果（乾ベース）_ちゅう芥類_％", 
        "ごみ組成分析結果（乾ベース）_不燃物類_％", 
        "ごみ組成分析結果（乾ベース）_その他_％", "単位容積重量_kg/m3", 
        "三成分_合計_％", "三成分_水分_％", "三成分_可燃分_％", "三成分_灰分_％", 
        "低位発熱量_(計算値)_kJ/kg", "低位発熱量_(実測値)_kJ/kg"
    ]
    # ------------------------------------

    # --- 値の有無をチェックするカラムをここで指定 ---
    MANDATORY_COLUMNS = [
        "余熱利用量（仕様値・公称値）_余熱利用量_MJ",
        "発電能力_総発電量（実績値）_MWh"
    ]
    # ------------------------------------
    
    filter_csv_columns(INPUT_FILE_PATH, OUTPUT_FILE_PATH, COLUMNS_TO_EXTRACT, MANDATORY_COLUMNS)
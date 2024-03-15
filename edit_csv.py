import csv
import json

# 入力となるCSVファイル名と出力するCSVファイル名
input_file = "sensor_values.csv"
output_file = "output.csv"

# JSON文字列からデータを抽出する関数
def extract_data_from_json(json_str):
    data = json.loads(json_str)
    print(data)
    return data["temperature"], data["humidity"], data["barometric_pressure"]

# CSVファイルを変換して出力する
with open(input_file, "r", newline="") as infile, open(output_file, "w", newline="") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # 最初の行をヘッダーとして読み取る
    header = next(reader)
    writer.writerow(["machine_id", "timestamp", "temperature", "humidity", "barometric_pressure"])
    
    # 各行を処理して出力する
    for row in reader:
        machine_id, timestamp, sensor_values = row
        temperature, humidity, barometric_pressure = extract_data_from_json(sensor_values)
        writer.writerow([machine_id, timestamp, temperature, humidity, barometric_pressure])

print("変換が完了しました。")

import requests
import datetime
import os

def make_day_list(start_date, end_date):
    print("start_date:", start_date)
    print("end_date:", end_date)

    period = end_date - start_date
    period = int(period.days)
    day_list = []
    for d in range(period + 1):
        day = start_date + datetime.timedelta(days=d)
        day_list.append(day)

    return day_list

def make_doc_id_list(day_list):
    """
    日付リストを受け取り、(docID, filerName) のリストを返す
    """
    securities_report_doc_info_list = []
    for index, day in enumerate(day_list):
        url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
        api_key = os.environ.get("MY_SUBSCRIPTION_KEY")
        params = {
            "date": day.strftime("%Y-%m-%d"),
            "type": 2,  # メタデータ取得
            "Subscription-Key": api_key
        }

        res = requests.get(url, params=params)
        json_data = res.json()
        print(day)

        if "results" in json_data:
            for num in range(len(json_data["results"])):
                ordinance_code = json_data["results"][num]["ordinanceCode"]
                form_code = json_data["results"][num]["formCode"]
                docInfoEditStatus = json_data["results"][num]["docInfoEditStatus"]

                # 有価証券報告書の判定(例: ordinance_code=="010" and form_code=="030000"かつ編集ステータスが2でない)
                if ordinance_code == "010" and form_code == "030000" and docInfoEditStatus != 2:
                    filer_name = json_data["results"][num]["filerName"]
                    doc_id = json_data["results"][num]["docID"]
                    print(filer_name, json_data["results"][num]["docDescription"], doc_id)

                    # (docID, filerName) をタプルで追加
                    securities_report_doc_info_list.append((doc_id, filer_name))

    return securities_report_doc_info_list

def download_xbrl_in_zip(securities_report_doc_info_list):
    """
    (docID, filerName)のリストを受け取り、ZIPファイルをダウンロードする。
    ダウンロード時のファイル名に filerName を付加。
    """
    save_dir = os.path.join(os.getcwd(), 'DLData')

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    number_of_lists = len(securities_report_doc_info_list)

    for index, (doc_id, filer_name) in enumerate(securities_report_doc_info_list):
        print(doc_id, ":", index + 1, "/", number_of_lists)
        url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
        api_key = os.environ.get("MY_SUBSCRIPTION_KEY")
        params = {
            "type": 1,
            "Subscription-Key": api_key
        }
        # ダウンロードファイル名に filerName を含める
        # ファイル名に使えない文字が含まれる場合があるので、必要に応じて置換してください
        # filename = os.path.join(save_dir, f"{doc_id}_{filer_name}.zip") # いったん中止
        filename = os.path.join(save_dir, f"{doc_id}.zip")

        res = requests.get(url, params=params, stream=True)
        try:
            if res.status_code == 200:
                with open(filename, 'wb') as file:
                    for chunk in res.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(f"Downloaded and Saved: {filename}")
            else:
                print(f"Failed to download file {doc_id} status_code:{res.status_code}")
        except Exception as e:
            print(f"Failed to download file {doc_id} error: {e}")

def main():
    # 直近7日間を例とする
    start_date = datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()

    day_list = make_day_list(start_date, end_date)

    # (docID, filerName) のリストを取得
    securities_report_doc_info_list = make_doc_id_list(day_list)
    print("number_of_lists:", len(securities_report_doc_info_list))
    print("get_list:", securities_report_doc_info_list)

    # ダウンロード処理
    download_xbrl_in_zip(securities_report_doc_info_list)
    print("download finish")

if __name__ == "__main__":
    main()

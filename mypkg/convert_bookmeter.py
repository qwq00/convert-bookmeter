import datetime
import time
import re
import json
import csv
import copy
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

root_url = "https://bookmeter.com/"
# Chromeを準備
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)


def check_date(input_date):
    """日付チェック

    Args:
        input_date(str) : 入力された日付
    Returns:
        bool            : チェック結果(True:OK, False:NG)
    """

    try:
        word = re.search(r'(\d{4})-(\d{2})-(\d{2})', input_date).group()
        if word:
            words = word.split("-")
            newDataStr = "%04d/%02d/%02d" % (
                int(words[0]), int(words[1]), int(words[2]))
            newDate = datetime.datetime.strptime(newDataStr, "%Y/%m/%d")
            return True
    except AttributeError:
        return False
    except ValueError:
        return False
    else:
        return False


def set_input_date():
    """読んだ日不明の設定

    Returns:
        str: 入力された日付
    """

    print("Enter the date you would like to set if the 'Date Read Unknown' is available.\nIf you do not want to set it, press enter.")
    print("(e.g.: 2008-05-01)")
    input_date = input()
    if len(input_date) != 0 and not (check_date(input_date)):
        # 日付の再入力
        print("There is a problem with your input. Please try again.")
        set_input_date()
    else:
        return input_date


def set_email(chrome):
    """ログイン画面のメールアドレス入力処理
    """

    input_email = chrome.find_element(By.ID, "session_email_address")
    print("Please enter your email address.")
    email = input()
    input_email.send_keys(email)
    return input_email.get_attribute("value")


def set_password(chrome):
    """ログイン画面のパスワード入力処理
    """

    input_password = chrome.find_element(By.ID, "session_password")
    print("Please enter your password.")
    password = input()
    input_password.send_keys(password)
    return input_password.get_attribute("value")


def check_login_error_message():
    """ログイン画面のエラーメッセージ処理
    ログイン画面でメールアドレス又はパスワードの入力チェックで引っ掛かった場合、
    対象の再入力を行う
    """

    elem_message = driver.find_elements(By.CLASS_NAME, "input__tip")
    elem_count = len(elem_message)
    no_problem_count = 0
    for i, message in enumerate(elem_message):
        if message.text:
            # エラーメッセージが表示されている場合
            print("There seems to be a problem with the input. Please try again.")
            if i == 0:
                # メールアドレス
                driver.find_element(By.ID, "session_email_address").clear()
                set_email(driver)
            elif i == 1:
                # パスワード
                driver.find_element(By.ID, "session_password").clear()
                set_password(driver)
        else:
            no_problem_count += 1
    # もう一度チェック処理を行う
    if elem_count != no_problem_count:
        check_login_error_message()


def login():
    """ログイン画面処理

    Returns:
        str: 入力された日付。登録日が「読んだ日不明」の本に適用する
    """

    input_date = set_input_date()
    set_email(driver)
    set_password(driver)
    # 入力でエラーメッセージが表示されている場合は再入力する
    check_login_error_message()

    driver.find_element(By.NAME, "button").click()
    current_url = driver.current_url
    if current_url != "https://bookmeter.com/home":
        # ログインに失敗した場合、再度ログイン処理を行う
        print("Login failed.")
        login()
    return input_date


def user_home():
    """ユーザホーム画面処理

    Returns:
        str: ユーザID
    """

    print("Login success.")
    user_id = re.search(r'([0-9]+)$', driver.find_element(By.CLASS_NAME,
                                                          "personal-account__data__link").get_attribute("href")).group()
    return user_id


def books_read(user_id, input_date):
    """読んだ本画面処理

    Args:
        user_id(str)    : ユーザID
        input_date(str) : 入力された日付
    Returns:
        tuple:(登録日, 書籍URLリスト)
    """

    read_books_url = root_url + "users/" + user_id + "/books/read"
    driver.get(read_books_url)
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "最後")))

    last_page_url = driver.find_element(
        By.LINK_TEXT, "最後").get_attribute("href")
    last_page = last_page_url.rsplit("=", 1)[1]
    # 読書メーター登録日の取得
    side_details = driver.find_element(
        By.CLASS_NAME, "bm-details-side").find_elements(By.CLASS_NAME, "bm-details-side__item")
    registration_date = None
    if input_date:
        # 入力された日付
        registration_date = input_date
    else:
        # 年月日の整形
        registration_date = re.search(
            r'^(\d{4})/(\d{2})/(\d{2})', side_details[0].text).group().replace("/", "-") + " 00:00:00"

    urls = []
    for i in range(int(last_page)):
        page_url = read_books_url + "?page=" + str(i + 1)
        driver.get(page_url)
        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "content-with-header__content")))

        elem_div = driver.find_elements(By.CLASS_NAME, "detail__title")
        for div in elem_div:
            link = div.find_element(By.TAG_NAME, "a").get_attribute("href")
            urls.append(link)
    else:
        print("Book count: " + str(len(urls)))
    return (registration_date, urls)


def csv_conversion(tuple_data):
    """CSV出力処理

    Args:
        tuple_data(str, list): 登録日, 書籍URLリスト
    """

    # インポートデータ
    import_csv_data = []
    title_csv_data = []
    data = []

    for i, url in enumerate(tuple_data[1]):
        driver.get(url)
        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "read-book")))
        time.sleep(3)

        # CSV情報の設定
        # サービスID
        data.append("1")
        # アイテムID
        data_book = json.loads(driver.find_element(
            By.CLASS_NAME, "action__items").get_attribute("data-book"))
        if "asin" in data_book:
            data.append(data_book["asin"])
        else:
            # ASINデータがないため、登録不可
            title_csv_data.append(copy.copy([data_book["title"]]))
            data.clear()
            continue
        # 13桁ISBN
        data.append("")
        # カテゴリ
        data.append("-")
        # 評価
        data.append("")
        # 読書状況
        data.append("読み終わった")
        # レビュー
        review = driver.find_element(
            By.CLASS_NAME, "read-book__content").find_element(By.TAG_NAME, "p").text
        data.append(review)
        # タグ
        data.append("")
        # 非公開メモ
        data.append("")
        # 登録日時
        pure_date = driver.find_element(
            By.CLASS_NAME, "read-book__date").text
        if len(pure_date) == 0:
            pure_date = driver.find_element(
                By.CLASS_NAME, "read-book__date").find_element(By.TAG_NAME, "a").text
        date = pure_date.replace("/", "-") + " 00:00:00"
        if re.search(r'(読んだ日不明)', date):
            # 読書メーターの登録日を設定する
            date = tuple_data[0]
        data.append(date)
        # 読了日
        data.append(date)

        import_csv_data.append(copy.copy(data))
        data.clear()

        if i != 0 and i % 50 == 0:
            print(f"{i} books converted.")
    else:
        # インポート用ファイル
        import_file_name = "books.csv"
        # インポート対象外ファイル
        not_import_file_name = "not_import_books.csv"

        if len(import_csv_data) != 0:
            with (open("./" + import_file_name, mode='w', encoding='cp932', errors='ignore') as import_file):
                import_writer = csv.writer(import_file, lineterminator='\n')
                import_writer.writerows(import_csv_data)
        if len(title_csv_data) != 0:
            with (open("./" + not_import_file_name, mode='w', encoding='cp932', errors='ignore') as not_import_file):
                not_import_writer = csv.writer(
                    not_import_file, lineterminator='\n')
                not_import_writer.writerows(title_csv_data)

        print("CSV output complete!")


def main():
    print("Starting Chrome...")

    # 読書メーターを開く
    driver.get("https://bookmeter.com/login")
    wait.until(EC.visibility_of_element_located((By.NAME, "button")))

    input_date = login()
    user_id = user_home()
    tuple_data = books_read(user_id, input_date)
    csv_conversion(tuple_data)

    # ブラウザを閉じる
    driver.quit()


if __name__ == '__main__':
    main()

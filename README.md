# convert-bookmeter

読書メーターに登録した読んだ本を CSV で出力する。

# Requirement

- Chrome
- Python 3.9
- ChromeDriver
- Selenium
- webdriver_manager
- 読書メーターのアカウント

# Installation

```bash
$ pip install git+https://github.com/qwq00/convert-bookmeter
```

# Usage

```bash
$ convert-bookmeter
Starting Chrome...  # Chrome window opens
Enter the date you would like to set if the 'Date Read Unknown' is available.
If you do not want to set it, press enter.
(e.g.: 2008-05-01)
# Enter the date you want to set
Please enter your email address.
# Enter the email address for your account
Please enter your password.
# Enter your account password
Login success.
Book count: 100 # Total number of books read
50 books converted.
100 books converted.
CSV output complete!
```

# CSV Format

| サービス ID(固定) | ASIN         | 13 桁 ISBN(固定) | カテゴリ(固定) | 評価(固定) | 読書状況(固定) | レビュー | タグ(固定) | 非公開メモ(固定) | 登録日時              | 読了日                |
| ----------------- | ------------ | ---------------- | -------------- | ---------- | -------------- | -------- | ---------- | ---------------- | --------------------- | --------------------- |
| "1"               | "B09RDWRJM9" | ""               | "-"            | ""         | "読み終わった" | "Good"   | ""         | ""               | "2022-02-15 00:00:00" | "2022-02-15 00:00:00" |

Example:

```
1,B09RDWRJM9,,-,,読み終わった,,,,2022-02-15 00:00:00,2022-02-15 00:00:00
1,B087JDXCX9,,-,,読み終わった,レビュー内容,,,2021-12-02 00:00:00,2021-12-02 00:00:00
```

# Note

- [ブクログ](https://booklog.jp/)へのインポート用CSVを想定しています。
- 読んだ本の読み終わった日が読んだ日不明で設定されている場合、ターミナルで入力された日付が設定されます。未入力の場合、読書メーターの登録日が設定されます。

# License

[MIT](https://choosealicense.com/licenses/mit/)

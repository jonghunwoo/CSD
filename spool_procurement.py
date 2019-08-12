import os
import urllib.request
import xlrd
import csv
import pandas as pd
import datetime
import numpy as np

# ./data 폴더에 해당 파일이 없으면 실행
if not os.path.isfile('./data/spool_list.csv'):
    #urlretrieve를 이용하여 파일에 직접 저장하는 코드
    url = "https://raw.githubusercontent.com/jonghunwoo/public/master/spool_list.xlsx"
    filename = "./data/spool_list.xlsx"
    urllib.request.urlretrieve(url, filename)

    # Excel 파일을 csv로 변환하는 함수 정의
    def csv_from_excel():
        workbook = xlrd.open_workbook('./data/spool_list.xlsx')
        worksheet = workbook.sheet_by_name('record')
        csv_file = open('./data/spool_list.csv', 'w')
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        for row_num in range(worksheet.nrows):
            writer.writerow(worksheet.row_values(row_num))

        csv_file.close()

    csv_from_excel()

# csv 파일 pandas 객체 생성
data = pd.read_csv('./data/spool_list.csv')
import os
import urllib.request
import xlrd
import csv
import pandas as pd
import datetime
import numpy as np

# ./data 폴더에 해당 파일이 없으면 실행
if not os.path.isfile('./data/spool_list_rev.csv'):
    #urlretrieve를 이용하여 파일에 직접 저장하는 코드
    url = "https://raw.githubusercontent.com/jonghunwoo/public/master/spool_list_rev.xlsx"
    filename = "./data/spool_list_rev.xlsx"
    urllib.request.urlretrieve(url, filename)

    # Excel 파일을 csv로 변환하는 함수 정의
    def csv_from_excel():
        workbook = xlrd.open_workbook('./data/spool_list_rev.xlsx')
        worksheet = workbook.sheet_by_name('spool_list_rev')
        csv_file = open('./data/spool_list_rev.csv', 'w')
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        for row_num in range(worksheet.nrows):
            writer.writerow(worksheet.row_values(row_num))

        csv_file.close()

    csv_from_excel()

# csv 파일 pandas 객체 생성
data = pd.read_csv('./data/spool_list_rev.csv')

# 필요한 column 로딩 - df에 저장
df = data[["block", "spool_no", "line_no", "dia", "dia_unit", "length", "weight", "wo", "material_out", "cutting", "fitup", "welding", "inspection","nde","palleting", "spool_out","coating", "painting_in", "painting_start", "painting", "stock_in", "stock_out", "on_deck", "in_position", "install_fitup", "installation"]]
#print(df.head(40))

# 숫자로 되어 있는 각 날자를 문자열로 변환한 후 datetime을 위한 형식으로 변환
for date in ["wo", "material_out", "cutting", "fitup", "welding", "inspection","nde","palleting", "spool_out","coating", "painting", "painting_in", "painting_start", "painting", "stock_in", "stock_out", "on_deck", "in_position", "install_fitup", "installation"]:
    df[date] = pd.TimedeltaIndex(df[date], unit='d') + datetime.datetime(1899,12,30)

#print(df[["wo", "material_out", "cutting", "fitup", "welding", "inspection","nde","palleting", "spool_out","coating", "painting_in", "painting_start", "painting", "stock_in", "stock_out", "on_deck", "in_position", "install_fitup", "installation"]].head(10))
print(df[["spool_no", "wo", "material_out", "cutting"]].head(10))

# 일별 평균 산출
grouped = df['spool_no'].groupby(df["stock_out"])
TH_AVG = grouped.count().mean() / 8 # spools / HR

print(TH_AVG)
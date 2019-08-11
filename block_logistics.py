import os
import urllib.request
import xlrd
import csv
import pandas as pd
import datetime

# ./data 폴더에 해당 파일이 없으면 실행
if not os.path.isfile('./data/block_transfer_list.csv'):
    #urlretrieve를 이용하여 파일에 직접 저장하는 코드
    url = "https://raw.githubusercontent.com/jonghunwoo/public/master/block_transfer_list.xlsx"
    filename = "./data/block_transfer_list.xlsx"
    urllib.request.urlretrieve(url, filename)

    #uropen을 이용하여 메모리에 저장후 파일에 저장하는 코드
    """
    url = "http://snowdeer.github.io/public/img/hello_page.jpg"
    filename = "snowdeer.jpg"
    image = urllib.request.urlopen(url).read()
    with open(filename, mode="wb") as f:
        f.write(image)
    """

    # Excel 파일을 csv로 변환하는 함수 정의
    def csv_from_excel():
        workbook = xlrd.open_workbook('./data/block_transfer_list.xlsx')
        worksheet = workbook.sheet_by_name('record')
        csv_file = open('./data/block_transfer_list.csv', 'w')
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        for row_num in range(worksheet.nrows):
            writer.writerow(worksheet.row_values(row_num))

        csv_file.close()

    csv_from_excel()

# csv 파일 pandas 객체 생성
data = pd.read_csv('./data/block_transfer_list.csv')

# 필요한 column 로딩 - df에 저장
df = data[["PROJ_NO", "BLK_NO","EREC_BLK_NO",
           "ASSY_PLN_SD", "ASSY_PLN_FD", "ASSY_ACTL_SD", "ASSY_ACTL_FD", "PLN_ASSY_SHOP",
           "OFT_PLN_SD", "OFT_FD_PLN", "OFT_ACTL_SD", "OFT_ACTL_FD", "PLN_OFT_SHOP",
           "PNT_PLN_SD", "PNT_PLN_FD", "PNT_ACTL_SD", "PNT_ACTL_FD", "PLN_PNT_SHOP"]]


# 해당 블록의 고유 번호 생성 - PROJ_NO + BLK_NO
df['PROJ_NO'] = data['PROJ_NO'].map(lambda x: str(x)[:-2])
df['BLK_NO'] = data['BLK_NO'].map(lambda x: str(x)[:-2])
df['BLK_NO_WITH_PROJ_NO'] = df['PROJ_NO'] + "_" + df['BLK_NO']

""" # 숫자로 되어 있는 각 날자를 문자열로 변환한 후 datetime을 위한 형식으로 변환
for activity in ["ASSY_PLN_SD", "ASSY_PLN_FD", "ASSY_ACTL_SD", "ASSY_ACTL_FD",
           "OFT_PLN_SD", "OFT_FD_PLN", "OFT_ACTL_SD", "OFT_ACTL_FD",
           "PNT_PLN_SD", "PNT_PLN_FD", "PNT_ACTL_SD", "PNT_ACTL_FD"]:

    df[activity] = df[activity].astype('int').astype('str')
    df[activity] = data[activity].map(lambda x: str(x)[:4]) + "-" + \
                        data[activity].map(lambda x: str(x)[5:7]) + "-" + \
                        data[activity].map(lambda x: str(x)[6:8]) """

# 숫자로 되어 있는 각 날자를 문자열로 변환한 후 datetime을 위한 형식으로 변환
for activity in ["ASSY_PLN_SD", "ASSY_PLN_FD", "ASSY_ACTL_SD", "ASSY_ACTL_FD",
           "OFT_PLN_SD", "OFT_FD_PLN", "OFT_ACTL_SD", "OFT_ACTL_FD",
           "PNT_PLN_SD", "PNT_PLN_FD", "PNT_ACTL_SD", "PNT_ACTL_FD"]:

    df[activity] = df[activity].astype('int').astype('str')
    df[activity] = pd.to_datetime(df[activity])
    #df[activity][i] = datetime.datetime.strptime(df[activity][i], "%Y%m%d").date() # Series 변환 불가하고 index로 돌릴 경우 높은 부하

# 각 작업 시간 기간 계산하여 새로운 변수에 저장
df['ASSY_PLN_DURATION'] = df['ASSY_PLN_FD'] - df['ASSY_PLN_SD']
df['ASSY_ACTL_DURATION'] = df['ASSY_ACTL_FD'] - df['ASSY_ACTL_SD']
df['OFT_PLN_DURATION'] = df['OFT_FD_PLN'] - df['OFT_PLN_SD']
df['OFT_ACTL_DURATION'] = df['OFT_ACTL_FD'] - df['OFT_ACTL_SD']
df['PNT_PLN_DURATION'] = df['PNT_PLN_FD'] - df['PNT_PLN_SD']
df['PNT_ACTL_DURATION'] = df['PNT_ACTL_FD'] - df['PNT_ACTL_SD']

CV_ASSY_PLN_DURATION = df['ASSY_PLN_DURATION'].std(axis=0)/df['ASSY_PLN_DURATION'].mean(axis=0)
CV_ASSY_ACTL_DURATION = df['ASSY_ACTL_DURATION'].std(axis=0)/df['ASSY_ACTL_DURATION'].mean(axis=0)

print("#" * 20, "AVG and STD of each process duration", "#"*20)
print("Planning average duration of assembly: ", df['ASSY_PLN_DURATION'].mean(axis=0))
print("Actual average duration of assembly: ", df['ASSY_ACTL_DURATION'].mean(axis=0))
print("STD of planning duration of assembly", df['ASSY_PLN_DURATION'].std(axis=0))
print("STD of actual duration of assembly", df['ASSY_ACTL_DURATION'].std(axis=0))

print("#" * 24, "CV each process duration", "#"*28)
print("CV of planning duration of assembly", CV_ASSY_PLN_DURATION)
print("CV of actual duration of assembly", CV_ASSY_ACTL_DURATION)





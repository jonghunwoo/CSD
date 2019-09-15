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

# 다음의 컬럼에 대하여 NaN이 있는 행 삭제 (결측치 처리)
for data in ["nde", "inspection", "spool_out", "palleting", "painting", "painting_in"]:
    df = df.dropna(subset=[data])

#print('Remaining number of rows is', df.count())
#print('Modified shape is ', df.shape)

# 숫자로 되어 있는 각 날자를 문자열로 변환한 후 datetime을 위한 형식으로 변환
for date in ["wo", "material_out", "cutting", "fitup", "welding", "inspection","nde","palleting", "spool_out","coating", "painting_in", "painting_start", "painting", "stock_in", "stock_out", "on_deck", "in_position", "install_fitup", "installation"]:
    df[date] = datetime.datetime(1899,12,30) + pd.TimedeltaIndex(df[date], unit='d')

# 각 작업 시간 기간 계산하여 새로운 변수에 저장
df['ct_fab'] = (df['welding'] - df['cutting']).astype('timedelta64[D]')
df['ct_ins'] = (df['nde'] - df['inspection']).astype('timedelta64[D]')
df['ct_srt'] = (df['spool_out'] - df['palleting']).astype('timedelta64[D]')
df['ct_pnt'] = (df['painting'] - df['painting_in']).astype('timedelta64[D]')

for data in ['ct_fab', 'ct_ins', 'ct_srt', 'ct_pnt']:
    print(df[data].head(10))

#각 공정의 평균과 표준편차를 구하여 변동성 계수 계산
ct_fab = (df['ct_fab'].mean(axis=0))
ct_ins = (df['ct_ins'].mean(axis=0))
ct_srt = (df['ct_srt'].mean(axis=0))
ct_pnt = (df['ct_pnt'].mean(axis=0))

print('Average cycle time of fabrication is ', ct_fab)
print('Average cycle time of insptection is ', ct_ins)
print('Average cycle time of sorting is ', ct_srt)
print('Average cycle time of painting is ', ct_pnt)

cv_fab = df['ct_fab'].std(axis=0)/ct_fab
cv_ins = df['ct_ins'].std(axis=0)/ct_ins
cv_srt = df['ct_srt'].std(axis=0)/ct_srt
cv_pnt = df['ct_pnt'].std(axis=0)/ct_pnt

print('CV of fabrication is ', cv_fab)
print('CV cycle time of inspection is ', cv_ins)
print('CV cycle time of sorting is ', cv_srt)
print('CV cycle time of painting is ', cv_pnt)

# 일별 평균 산출 # spools/HR
grouped = df['spool_no'].groupby(df["painting"])
TH_AVG = grouped.count().mean() / 8
print("Final TH = ", TH_AVG)

# 공정별 평균/표준편차 및 변동성 계수 출력
    #공정 모델
    #[:,0] : part processing time (days/block)
    #[:,1] : CV of part processing time
    #[:,2] : unit price of facility
    #[:,3] : number of facility or process

param_process = np.array([[ct_fab, cv_fab, 0, 14],
                          [ct_ins, cv_ins, 0, 5],
                          [ct_srt, cv_srt, 0, 2],
                          [ct_pnt, cv_pnt, 0, 15]])

print(param_process)

# 각 공정의 단위 제품 effective time 계산
te = np.zeros(4)
te = param_process[:, 0]
print("Te : ", te)

#각 공정 생산 시간의 변동성 (SCV: Squared Coefficient of Variability)
ce_2 = np.zeros(4)
ce_2 = np.power(param_process[:, 1],2)
print("SCV : ", ce_2)

#각 공정의 가동률 (utilization)
u = np.zeros(4)
u = TH_AVG * te / param_process[:, 3]
print("utilization : ", u)

ca_2 = np.zeros(4)
cd_2 = np.zeros(4)
ca_2[0] = 1

#전 공정의 출발률 변동성(cd_2[i]) = 후 공정의 도착률 변동성(ca_2[i+1])
cd_2[0] = 1 + (1-np.power(u[0],2))*(ca_2[0]-1) + (np.power(u[0],2)/np.sqrt(param_process[0,3])) * (ce_2[0]-1)
ca_2[1] = cd_2[0]
cd_2[1] = 1 + (1-np.power(u[1],2))*(ca_2[1]-1) + (np.power(u[1],2)/np.sqrt(param_process[1,3])) * (ce_2[1]-1)
ca_2[2] = cd_2[1]
cd_2[2] = 1 + (1-np.power(u[2],2))*(ca_2[2]-1) + (np.power(u[2],2)/np.sqrt(param_process[2,3])) * (ce_2[2]-1)
ca_2[3] = cd_2[2]
cd_2[3] = 1 + (1-np.power(u[3],2))*(ca_2[3]-1) + (np.power(u[3],2)/np.sqrt(param_process[3,3])) * (ce_2[3]-1)

# 설비수를 고려한 CT
CTq = np.zeros(4)
CT = np.zeros(4)
CTq = [(ca_2 + ce_2)/2] * np.power(u,np.sqrt(2*(param_process[:, 3]+1))-1)/(param_process[:, 3]*(1-u))* te
CT = CTq + te

CTtot = np.sum(CT)
WIPq = (CT-te) * TH_AVG
#WIPq = np.ceil(WIPq)

print("Total CT : ", CTtot)
print("WIPq : ", WIPq)
import urllib.request
import csv
import pandas as pd
import matplotlib.pyplot as plt
import  numpy as np

APS_data = pd.read_csv("./APS_ACTIVITY_midterm.csv",encoding='unicode_escape')

df = APS_data[["CASENO", "PROJECTNO","ACTIVITYCODE", "LOCATIONCODE", "LOCATIONTYPE", "WORKTYPE",
                              "MAINPROCESSCODE", "SUBPROCESSCODE", "PLANSTARTDATE", "PLANFINISHDATE", "PLANDURATION",
                              "PLANMH", "VOL1","VOL2","VOL3", "ACTIVITYDESC", "STAGECODE"]]

df['Zeros'] = '0'

df['ProcessCode'] = df['WORKTYPE'] + df['MAINPROCESSCODE'] + df['Zeros'] + df['SUBPROCESSCODE'].apply(str) + \
                    df['STAGECODE'].apply(str)

TargetProcessdf = pd.read_csv("./TargetActivity.csv",encoding='unicode_escape')

TargetProcessdf['AvgDuration'] = '0'

for i in range(TargetProcessdf.shape[0]):
    TargetProcessRows = df.loc[df['ProcessCode'] == TargetProcessdf['ProcessCode'].iloc[i]]
    TargetProcessAvgDuration = TargetProcessRows['PLANDURATION'].mean()
    TargetProcessdf['AvgDuration'][i] = TargetProcessAvgDuration

###주요 직종 액티비티 코드 표 - 총 17개
## 선각
# 소조립(중조용) HA011
# 소조립(대조용) HA021
# 중조 HA031
# 대조 HA041
# 가공 HF031
# Shop PE HP011
# 1차 PE HP023
# 2차 PE HP034

## 의장
# 중조의장 FB011
# 블록선행의장 FB021
# ShopPE의장 FP011
# 1차PE의장 FP023
# 2차PE의장 FP034

## 도장
# 블럭도장 PB011
# ShopPE도장 PP011
# 1차PE도장 PP023
# 2차PE도장 PP034

print("Done")
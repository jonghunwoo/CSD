import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time


class Cal_Fac_Param:

    def __init__(self, excel_name, sheet_name, start_dates, final_dates, process_names=None):
        self.excel_name = excel_name
        self.sheet_name = sheet_name
        self.start_dates = start_dates
        self.final_dates = final_dates
        self.param_index = ['Ra', 'Ca', 'Te', 'Ce', 'Rd', 'Cd', 'u']

        if process_names == None:
            self.process_names = [None] * len(start_dates)
            for i in range(len(start_dates)):
                self.process_names[i] = 'process' + str(i)
        else:
            self.process_names = process_names

        # 파일 읽기
        self.df = pd.read_excel('./' + self.excel_name, sheet_name=self.sheet_name)

    ## 전처리 함수
    def pre_process(self, del_inconsistency=True, drop_nan=True, zero_nan=False):

        df_dates = self.df[self.start_dates + self.final_dates]

        # 데이터 형식이 8자리 숫자로만 되어 있을 경우 datetime으로 변환
        for col in df_dates:
            if df_dates[col].dtype == 'int64':
                df_dates[col] = df_dates[col].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))

        print("Raw Data's number of rows : " + str(df_dates.shape[0]))

        # Nan 처리
        if drop_nan == True:
            df_dates.dropna(inplace=True)
            print("After deleting Nan, remains " + str(df_dates.shape[0]) + " rows")
        elif zero_nan == True:
            df_dates.fillna(0, inplace=True)

            # Inconsistency 처리  -  시작일이 종료일보다 늦은 경우
        if del_inconsistency == True:
            for i in range(len(self.start_dates)):
                df_dates.drop(df_dates[df_dates[self.start_dates[i]] > df_dates[self.final_dates[i]]].index,
                              inplace=True)
                print("After deleting " + self.process_names[i] + "\'s inconsistent rows, remains " + str(
                    df_dates.shape[0]) + " rows")

        self.df_dates = df_dates

    ## parameter 계산 함수
    def get_param(self):

        # 분석하고자 하는 공정 시작 및 종료 날짜 칼럼 이름 저장
        df_s_dates = self.df_dates[self.start_dates]
        df_f_dates = self.df_dates[self.final_dates]

        # 공정 te 계산 - CT이라고 해야하나?
        self.te_df = pd.DataFrame()
        for i in range(len(self.process_names)):
            self.te_df[i] = df_f_dates[self.final_dates[i]] - df_s_dates[self.start_dates[i]]
        for col in self.te_df:
            self.te_df[col] = self.te_df[col].apply(lambda x: x.days)

        # ra, ta, ca 계산
        int_arr = np.zeros((len(df_s_dates) - 1, len(self.start_dates)))
        np_s_dates = df_s_dates.to_numpy(copy=True)
        np_s_dates.sort(axis=0)
        df_np_s_dates = pd.DataFrame(np_s_dates)
        # print(df_np_s_dates)

        for i in range(len(self.start_dates)):
            for k in range(len(int_arr)):
                int_arr[k][i] = (np_s_dates[k + 1][i] - np_s_dates[k][i]).astype('timedelta64[D]') / np.timedelta64(1,
                                                                                                                    'D')

        # print('inter arrival time')
        # df_int_arr = pd.DataFrame(int_arr)
        # print(df_int_arr)

        self.ta = np.nanmean(int_arr, axis=0)
        # print('ta')
        # print(self.ta)
        self.ra = 1 / self.ta
        # print('ra')
        # print(self.ra)
        self.stda = np.nanstd(int_arr, axis=0)
        self.ca = self.stda / self.ta

        # rd, td, cd 계산
        int_dep = np.zeros((len(df_f_dates) - 1, len(self.final_dates)))
        np_f_dates = df_f_dates.to_numpy(copy=True)
        np_f_dates.sort(axis=0)

        for i in range(len(self.final_dates)):
            for k in range(len(int_dep)):
                int_dep[k][i] = (np_f_dates[k + 1][i] - np_f_dates[k][i]).astype('timedelta64[D]') / np.timedelta64(1,
                                                                                                                    'D')

        self.td = np.nanmean(int_dep, axis=0)
        self.rd = 1 / self.td
        self.stdd = np.nanstd(int_dep, axis=0)
        self.cd = self.stdd / self.td

        # 변수들 DataFrame, Numpy로 저장
        self.param = pd.DataFrame(columns=self.process_names, index=self.param_index)
        self.param.loc['Ra'] = self.ra
        self.param.loc['Ca'] = self.ca
        self.param.loc['Te'] = np.asarray(self.te_df.mean())
        self.param.loc['Ce'] = np.asarray(self.te_df.std() / self.te_df.mean())
        self.param.loc['Rd'] = self.rd
        self.param.loc['Cd'] = self.cd

        self.np_param = self.param.to_numpy(copy=True)

    # parameter 값들 반환하는 함수
    def show_param(self):
        return self.param


class Cal_Fac_Param_22:

    def __init__(self, param):
        self.param = param
        self.np_param = self.param.to_numpy(copy=True)
        self.process_names = list(param.columns)
        self.df_CT_WIP = pd.DataFrame(columns=param.columns, index=['CTq', 'CT', 'WIPq', 'WIP'])

    # m값 입력, 각 공정별 m값을 가지고 있는 list 형태로 입력
    def assume_m(self, m):
        self.m = np.asarray(m)

    # utilization 계산함수
    def cal_u(self, ra=None, te=None, m=None, inplace=True):
        if ra == None:
            ra = self.np_param[0][:]
        else:
            ra = np.asarray(ra)

        if te == None:
            te = self.np_param[2][:]
        else:
            te = np.asarray(te)

        if m == None:
            try:
                m = self.m
            except:
                print("m을 먼저 정의해야 합니다.")
        else:
            m = np.asarray(m)

        u = ra * te / m

        if inplace == True:
            self.u = u
            self.np_param[6][:] = u
            self.param.iloc[6] = u
            return self.u
        else:
            return u

    def cal_cd(self, ca, ce, u, m):
        cd = 1 + (1 - u * u) * (ca * ca - 1) + (u * u) * (ce * ce - 1) / np.sqrt(m)
        return cd

    # 공식에 의한 Cd 계산. Ca, Ce, u, m 값 입력 가능. Default는 param의 값들 사용.

    def cal_ass_cd(self, ca=None, ce=None, u=None, m=None, cont=True, inplace=True):
        if ca == None:
            ca = self.np_param[1][:]
        else:
            try:
                checker = len(ca)
                ca = np.asarray(ca)
            except:
                temp = np.zeros(len(self.process_names))
                temp.fill(ca)
                ca = temp

        if ce == None:
            ce = self.np_param[3][:]
        else:
            ce = np.asarray(ce)

        if u == None:
            try:
                u = self.np_param[6][:]
            except:
                print("cal_u 함수를 통해 utilization을 먼저 정의해야 합니다.")
        else:
            u = np.asarray(u)

        if m == None:
            try:
                m = self.m
            except:
                print("assume_m 함수를 통해 m을 먼저 정의해야 합니다.")
        else:
            m = np.asarray(m)

        cd = np.zeros(len(self.process_names))
        if cont == True:
            ra = self.np_param[0][:]
            ra.fill(ra[0])
            self.np_param[0][:] = ra
            self.param.iloc[0] = ra
            u = self.cal_u()

            for i in range(len(self.process_names) - 1):
                cd[i] = self.cal_cd(ca=ca[i], ce=ce[i], u=u[i], m=m[i])
                ca[i + 1] = cd[i]
                if i == len(self.process_names) - 2:
                    cd[i + 1] = self.cal_cd(ca=ca[i + 1], ce=ce[i + 1], u=u[i + 1], m=m[i + 1])

        else:
            cd = self.cal_cd(ca, ce, u, m)

        if inplace == True:
            self.np_param[0][:] = ra
            self.param.iloc[0] = ra
            self.np_param[1][:] = ca
            self.param.iloc[1] = ca
            self.np_param[5][:] = cd
            self.param.iloc[5] = cd
            self.np_param[6][:] = u
            self.param.iloc[6] = u
            return cd
        else:
            return cd

    # CT, WIP 계산

    def cal_CT_WIP(self, ca=None, ce=None, u=None, m=None, te=None, ra=None, inplace=True):
        if ca == None:
            ca = self.np_param[1][:]
        else:
            ca = np.asarray(ca)

        if ce == None:
            ce = self.np_param[3][:]
        else:
            ce = np.asarray(ce)

        if u == None:
            try:
                u = self.np_param[6][:]
            except:
                print("cal_u 함수를 통해 utilization을 먼저 정의해야 합니다.")
        else:
            u = np.asarray(u)

        if m == None:
            try:
                m = self.m
            except:
                print("assume_m 함수를 통해 m을 먼저 정의해야 합니다.")
        else:
            m = np.asarray(m)
            u = self.cal_u(m=m, inplace=False)

        if te == None:
            te = self.np_param[2][:]
        else:
            te = np.asarray(te)
            u = self.cal_u(te=te, inplace=False)

        if ra == None:
            ra = self.np_param[0][:]
        else:
            ra = np.asarray(ra)
            u = self.cal_u(ra=ra, inplace=False)

        CTq = (((ca * ca) + (ce * ce)) / 2) * (np.power(u, np.sqrt(2 * (m + 1)) - 1) / (m * (1 - u))) * te
        CT = CTq + te
        WIPq = CTq * ra
        WIP = CT * ra

        if inplace == True:
            self.CTq = CTq
            self.CT = CT
            self.WIPq = WIPq
            self.WIP = WIP

            self.df_CT_WIP.iloc[0] = CTq
            self.df_CT_WIP.iloc[1] = CT
            self.df_CT_WIP.iloc[2] = WIPq
            self.df_CT_WIP.iloc[3] = WIP

            return self.df_CT_WIP
        else:
            df_CT_WIP = pd.DataFrame(columns=self.param.columns, index=['CTq', 'CT', 'WIPq', 'WIP'])
            df_CT_WIP.iloc[0] = CTq
            df_CT_WIP.iloc[1] = CT
            df_CT_WIP.iloc[2] = WIPq
            df_CT_WIP.iloc[3] = WIP
            return df_CT_WIP


class sensitivity_analysis:

    def __init__(self, param, init_m):
        self.origin_param = param.copy()
        self.init_m = init_m
        # self.cfp3 = Cal_Fac_Param_22(param)
        # self.np_param = param.to_numpy(copy = True)
        # self.process_names = list(param.columns)
        # self.cfp3.assume_m(init_m)
        # self.cfp3.cal_ass_cd()

    def execute(self, var, out, start, stop, step, m_num=None, plot=True, check=False):
        self.cfp3 = Cal_Fac_Param_22(self.origin_param.copy())
        self.cfp3.assume_m(self.init_m)
        self.cfp3.cal_ass_cd()
        CT_WIP = ['CT', 'WIP']
        if out not in CT_WIP:
            print('out 파라미터에 CT 또는 WIP를 입력해야 합니다')

        index = np.arange(start, stop, step)
        out_list = list()

        if var == 'Ra':
            ra = index
            for x in ra:
                self.cfp3.np_param[0][:] = x
                self.cfp3.cal_ass_cd()
                temp = self.cfp3.cal_CT_WIP(inplace=False)
                if check == True:
                    print(x)
                    print(temp)
                    print('\n')
                out_list.append(temp.loc[out].sum())

        if var == 'Ca':
            ca = index
            for x in ca:
                self.cfp3.cal_ass_cd(ca=x)
                temp = self.cfp3.cal_CT_WIP(inplace=False)
                if check == True:
                    print(x)
                    print(temp)
                    print('\n')
                out_list.append(temp.loc[out].sum())

        if var == 'm':
            if m_num == None:
                print('몇 번째 프로세스의 기계 대수로 분석할 것인지 m_num 파라미터를 통해 입력해야 합니다')
                return
            else:
                temp_m = index
                for x in temp_m:
                    self.cfp3.m[m_num] = x
                    self.cfp3.cal_ass_cd()
                    temp = self.cfp3.cal_CT_WIP(inplace=False)
                    if check == True:
                        print(x)
                        print(temp)
                        print('\n')
                    out_list.append(temp.loc[out].sum())

        # result = pd.DataFrame({out : out_list}, index = index)
        result = pd.DataFrame({var: index, out: out_list})

        if plot == True:
            plt.plot(result[var], result[out], 'bo')
            plt.show()

        return result
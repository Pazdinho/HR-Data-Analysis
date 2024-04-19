import os
import math
import numpy as np
import pandas as pd

import requests

# scroll down to the bottom to implement your solution

if __name__ == '__main__':

    if not os.path.exists('../Data'):
        os.mkdir('../Data')

    # Download data if it is unavailable.
    if ('A_office_data.xml' not in os.listdir('../Data') and
            'B_office_data.xml' not in os.listdir('../Data') and
            'hr_data.xml' not in os.listdir('../Data')):
        print('A_office_data loading.')
        url = "https://www.dropbox.com/s/jpeknyzx57c4jb2/A_office_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/A_office_data.xml', 'wb').write(r.content)
        print('Loaded.')

        print('B_office_data loading.')
        url = "https://www.dropbox.com/s/hea0tbhir64u9t5/B_office_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/B_office_data.xml', 'wb').write(r.content)
        print('Loaded.')

        print('hr_data loading.')
        url = "https://www.dropbox.com/s/u6jzqqg1byajy0s/hr_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/hr_data.xml', 'wb').write(r.content)
        print('Loaded.')

        # All data in now loaded to the Data folder.

# Cleaning data set
def stage1():
    A = pd.read_xml('../Data/A_office_data.xml')
    B = pd.read_xml('../Data/B_office_data.xml')
    HR = pd.read_xml('../Data/hr_data.xml')

    NewIndexA = []
    NewIndexB = []
    HRR = []

    for i in A.employee_office_id:
        NewIndexA.append(f"A{i}")
    for j in B.employee_office_id:
        NewIndexB.append(f"B{j}")
    for k in HR.employee_id:
        HRR.append(k)

    #Reindexing
    A.set_index(pd.Series(NewIndexA),inplace=True)
    B.set_index(pd.Series(NewIndexB),inplace=True)
    HR.set_index(pd.Series(HRR),inplace=True)

    #concating two data sets
    AB = pd.concat([A,B])
    #merging it with HR data set
    Final = AB.merge(HR, right_index=True, left_index=True, indicator=True)
    Final.drop(columns=['_merge', 'employee_office_id','employee_id'], inplace=True)
    Final.sort_index(inplace = True)
    return Final

#Some insights about dataset
def stage2(Final):

    # What are the departments of the top ten employees in terms of working hours?
    print(Final.sort_values('average_monthly_hours',ascending=False)['Department'].head(10).values.tolist())
    # What is the total number of projects on which IT department employees with low salaries have worked?
    print(sum(Final.query("Department == 'IT' & salary == 'low'")['number_project']))
    # What are the last evaluation scores and the satisfaction levels of the employees A4, B7064, and A3033?
    print(Final.loc[['A4', 'B7064', 'A3033']][['last_evaluation','satisfaction_level']].values.tolist())

#Aggregation data
def stage3(Final):
    def count_bigger_5(series, maks=5):
        return series.where(series > maks).count()

    #Data grouped by 'left' column(0 - no (still in company), 1 - yes)

    #the median number of projects the employees in a group worked on, and how many employees worked on more than five projects
    print(round(Final.groupby(['left']).agg({'number_project':['median',count_bigger_5]}),2))
    #the mean and median time spent in the company
    print((round(Final.groupby(['left']).agg({'time_spend_company':['mean','median']}),2)))
    #the share of employees who've had work accidents;
    print((Final.groupby('left').agg({'Work_accident':'mean'}),2))
    #the mean and standard deviation of the last evaluation score.
    print((Final.groupby('left').agg({'last_evaluation':['mean','std']}),2))
    #All the above data in one dict
    print(Final.groupby("left").agg({"number_project": ["median", count_bigger_5],"time_spend_company": ["mean", "median"],"Work_accident": ["mean"],"last_evaluation": ["mean", "std"],}).round(2).to_dict())

#Pivot tables
def stage4(Final):

    #Creating Pivots  with median, min, max, mean aggregation functions
    first_pivot = Final.pivot_table(index='Department', columns=['left','salary'], values='average_monthly_hours', aggfunc = 'median')
    second_pivot = Final.pivot_table(index='time_spend_company', columns='promotion_last_5years', values=['satisfaction_level','last_evaluation'], aggfunc = ['min','max','mean'])

    #Find department where:
    # For employees currently employed: the median value of the working hours of high-salary employees is smaller/
    # /than the hours of the medium-salary employees.OR
    # For employees who left: the median value of working hours of low-salary employees is smaller/
    # /than the hours of high-salary employees
    print(round(first_pivot.loc[(first_pivot[(0, 'high')] < first_pivot[(0, 'medium')]) | (first_pivot[(1, 'low')]<first_pivot[(1, 'high')])],2))

    #find rows where the previous mean evaluation score is higher for those without promotion than those who had
    print(round(second_pivot.loc[(second_pivot[('mean', 'last_evaluation', 0)] > second_pivot[('mean', 'last_evaluation', 1)])],2))


stage1()
#stage2(stage1())
#stage3(stage1())
stage4(stage1())
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:18:37 2024

@author: hoye.110
"""


import pandas as pd
# import duckdb
import numpy as np
import streamlit as st

class syllabus_xlsx2df():
    def __init__(self, syllabus):
        self.syllabus = syllabus
        
    def convert_xlsx2df(syllabus):
        usecols = ['Stt', 'Mã MH', 'Tên môn học', 'Số tín chỉ', 'Môn bắt buộc', 'Đã học',
       'Nhóm', 'Nhánh', 'Số tín chỉ tối thiểu', 'Số tín chỉ tối đa',
       'Môn học đã học và đạt', 'Tổng tiết', 'Lý thuyết', 'Thực hành',
       'Tiết thành phần']
        syllabus = syllabus[usecols]
        # determine semester in which subject falls in
        syllabus['Tên học kỳ'] = syllabus['Stt'].astype(str).apply(lambda x: x if x.__contains__('Học kỳ') else '')
        semester_position = []
        for i in range(0, len(syllabus)): 
            if syllabus.loc[i, 'Tên học kỳ'] != '':
                semester_position.append((i, syllabus.loc[i, 'Tên học kỳ']))
        
        for i in range(0, len(semester_position)):
            if i == (len(semester_position)-1):
                key1 = semester_position[i][0]
                value1 = semester_position[i][1]
                for k in range(0, len(syllabus)):
                    if k > key1:
                        syllabus.loc[k, 'Tên học kỳ'] = value1
            else:
                key1 = semester_position[i][0]
                key2 = semester_position[i+1][0]
                value1 = semester_position[i][1]
                for k in range(0, len(syllabus)):
                    if k > key1 and k < key2:
                        syllabus.loc[k, 'Tên học kỳ'] = value1
        
        # format semester
        def semester_formatting(x):
            item1 = x[-9:]
            item2 = x[len('Học kỳ ')]
            semester_formatting = '(' + item1 + ').' + item2
            return semester_formatting
        
        syllabus['Học kỳ'] = syllabus['Tên học kỳ'].astype(str).apply(lambda x: semester_formatting(x))
        syllabus['Học kỳ'] = syllabus['Học kỳ'].astype(str)
        syllabus['Mã MH'] = syllabus['Mã MH'].astype(str)
        syllabus_cleaned = syllabus.loc[syllabus['Mã MH'] != 'nan']
        syllabus_cleaned = syllabus_cleaned.reset_index()


        # # ## select & rename columns to readable ones
        usecols = ['Học kỳ', 'Tên học kỳ', 'Mã MH', 'Tên môn học', 'Số tín chỉ', 'Môn bắt buộc',
                'Nhóm', 'Nhánh', 'Số tín chỉ tối thiểu', 'Số tín chỉ tối đa', 'Tổng tiết', 'Lý thuyết', 'Thực hành']
        # 'Đã học': remove this column cuz it's not correctly labeled
        syllabus_cleaned = syllabus_cleaned[usecols]
        syllabus_cleaned.columns = ['Mã môn học' if x=='Mã MH' else x for x in syllabus_cleaned.columns]
        syllabus_cleaned.columns = ['Học kỳ dự kiến học' if x=='Học kỳ' else x for x in syllabus_cleaned.columns]
        return syllabus_cleaned
        
# diem:syllabus = many:one
if __name__ == '__main__':
    syllabus = pd.read_excel(r"C:\Users\admin\Downloads\ChuongTrinhDaoTao (2).xlsx")
    print(syllabus.columns)
    syllabus_master_data = syllabus_xlsx2df.convert_xlsx2df(syllabus)
    st.dataframe(syllabus_master_data)



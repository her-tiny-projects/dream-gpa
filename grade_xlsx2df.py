# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:18:37 2024

@author: hoye.110
"""


import pandas as pd
import duckdb
import numpy as np
import streamlit as st

class grade_xlsx2df():
    def __init__(self, grade):
        self.grade = grade
        
    def convert_xlsx2df(grade):
    #     usecols = ['Stt', 'Mã MH', 'Môn thay thế', 'Nhóm/tổ môn học', 'Tên môn học',
    #    'Số tín chỉ', 'Điểm thi', 'Điểm TK (10)', 'Điểm TK (4)', 'Điểm TK (C)',
    #    'Kết quả', 'Chi tiết']
    #     grade = grade[usecols]
        # determine semester in which subject falls in
        grade['Tên học kỳ'] = grade['Stt'].astype(str).apply(lambda x: x if len(x) > 3 and 'Điểm' not in x and 'tín chỉ' not in x else '')
        semester_position = []
        for i in range(0, len(grade)): 
            if grade.loc[i, 'Tên học kỳ'] != '':
                semester_position.append((i, grade.loc[i, 'Tên học kỳ']))
        
        for i in range(0, len(semester_position)):
            if i == (len(semester_position)-1):
                key1 = semester_position[i][0]
                value1 = semester_position[i][1]
                for k in range(0, len(grade)):
                    if k > key1:
                        grade.loc[k, 'Tên học kỳ'] = value1
            else:
                key1 = semester_position[i][0]
                key2 = semester_position[i+1][0]
                value1 = semester_position[i][1]
                for k in range(0, len(grade)):
                    if k > key1 and k < key2:
                        grade.loc[k, 'Tên học kỳ'] = value1

        # format semester
        def semester_formatting(x):
            try:
                item1 = x[-9:]
                item2 = x[len('Học kỳ ')]
                semester_formatting = '(' + item1 + ').' + item2
                return semester_formatting
            except:
                return x
        grade['Học kỳ'] = grade['Tên học kỳ'].astype(str).apply(lambda x: semester_formatting(x))

        # subject
        q = """
        SELECT *
        FROM grade
        WHERE "Tên môn học" IS NOT NULL
        """
        grade_detail = duckdb.sql(q).df()
        

        
        # summary by semester 
        q = """
            SELECT
                "Học kỳ",
                Stt as Attribute,
                CAST("Mã MH" AS CHAR) AS Value
            FROM grade
            WHERE Stt LIKE '%- %'
            AND LENGTH(Stt) < 40 -- exclude record with the longest summary
            """
        summary = duckdb.sql(q).df()
        summary['Attribute'] = summary['Attribute'].apply(lambda x: x.replace('- ', '').replace(':', ''))
        summary = pd.pivot_table(summary, index='Học kỳ', columns='Attribute', values='Value', aggfunc='sum')
        summary['Học kỳ'] = summary.index
        summary.index = range(1, len(summary)+1)


        # mapping subject & summary and cleaning
        q = """
        SELECT *
        FROM grade_detail gd
        LEFT JOIN summary sm USING("Học kỳ")
        """
        grade_cleaned = duckdb.sql(q).df()

        # select columns
        usecols = ['Học kỳ', 'Tên học kỳ', 'Mã MH', 'Nhóm/tổ môn học', 'Tên môn học', 'Số tín chỉ', 
                'Điểm thi', 'Điểm TK (10)', 'Điểm TK (4)', 'Điểm TK (C)', 
                'Điểm trung bình học kỳ hệ 10', 'Điểm trung bình học kỳ hệ 4',
                'Số tín chỉ đạt học kỳ', 
                # 'Điểm rèn luyện học kỳ',
                'Điểm trung bình tích lũy hệ 10', 'Điểm trung bình tích lũy hệ 4',
                'Số tín chỉ tích lũy']
        grade_cleaned = grade_cleaned[usecols]
        # rename columns
        grade_cleaned.columns = ['Mã môn học' if x == 'Mã MH' else x for x in grade_cleaned.columns]
        grade_cleaned.columns = ['Học kỳ đăng ký học' if x == 'Học kỳ' else x for x in grade_cleaned.columns]
        # cast dtype
        item_2cleaned = ['Số tín chỉ tích lũy', 'Số tín chỉ đạt học kỳ', 
                        #  'Điểm rèn luyện học kỳ',
                        'Điểm trung bình học kỳ hệ 10', 'Điểm trung bình học kỳ hệ 4',
                        'Điểm trung bình tích lũy hệ 10', 'Điểm trung bình tích lũy hệ 4']
        for item in item_2cleaned:
            grade_cleaned[item] = grade_cleaned[item].astype(np.float32).apply(lambda x: np.nan if x==0 else x)
        grade_cleaned['Học kỳ đăng ký học'] = grade_cleaned['Học kỳ đăng ký học'].astype(str)
        return grade_cleaned

        
# diem:syllabus = many:one
if __name__ == '__main__':
    grade = pd.read_excel(r"C:\Users\admin\Downloads\Diem (4).xlsx")
    grade_master_data = grade_xlsx2df.convert_xlsx2df(grade)
    st.dataframe(grade_master_data)


    




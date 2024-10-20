import streamlit as st
import streamlit_analytics
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
from math import ceil
from plotly import graph_objects as go
from google.oauth2 import service_account
from google.cloud import firestore
import time
import grade_xlsx2df, syllabus_xlsx2df



empty_table = pd.DataFrame(columns=['temp'], index=[''])
empty_table.drop(empty_table.index, inplace=True)

# initiate shared variables:
if 'grade_upload_fail' not in st.session_state:
       st.session_state.grade_upload_fail = 0
if 'syllabus_upload_fail' not in st.session_state:
       st.session_state.syllabus_upload_fail = 0
if 'grade_upload' not in st.session_state:
       st.session_state.grade_upload = empty_table
if 'syllabus_upload' not in st.session_state:
       st.session_state.syllabus_upload = empty_table
if 'grade_master_data' not in st.session_state:
       st.session_state.grade_master_data = empty_table
if 'syllabus_master_data' not in st.session_state:
       st.session_state.syllabus_master_data = empty_table
if 'start_button' not in st.session_state:
       st.session_state.start_button = False
if 'english_mode' not in st.session_state:
       st.session_state.english_mode = 0
english_mode = st.session_state.english_mode


language_index = {'grade_upload': ['### UPLOAD BẢNG ĐIỂM', '### UPLOAD YOUR TRANSCRIPT'],
                  'grade_upload_des': ['Download bảng điểm ở ftugate và upload vào ô dưới:', 'Please attach your transcript from ftugate to the box below:'],
                  'syllabus_upload': ['### UPLOAD CHƯƠNG TRÌNH ĐÀO TẠO', '### UPLOAD YOUR CURRICULUM'],
                  'syllabus_upload_des': ['Download chương trình đào tạo ở ftugate và upload vào ô dưới:', 'Please attach your curriculum from ftugate to the box below:'],
                  'template_error': ['File không đúng mẫu! Bạn kiểm tra xem file của mình có chứa các cột như mẫu dưới đây không nhé', "Incorrect file format! Please make sure your file contains columns as the template below"],
                  'format_error': ['File không đúng định dạng Excel!', 'Incorrect file format! Only Excel is accepted!'],
                  'start_button': ['BẮT ĐẦU', 'START']}

# 2. LOGIN --> check
streamlit_analytics.start_tracking(firestore_key_file='db_key.json', firestore_collection_name='app_metrics')
grade_template = pd.DataFrame({
                            'Stt': '',
                            'Mã MH': '',
                            'Môn thay thế': '',
                            'Nhóm/tổ môn học': '',
                            'Tên môn học': '',
                            #'HK chuyển': '',
                            'Số tín chỉ': '',	
                            'Điểm thi': '',
                            'Điểm TK (10)': '',
                            'Điểm TK (4)': '',
                            'Điểm TK (C)': '',
                            'Kết quả': '',
                            'Chi tiết': ''}, index=[''])
grade_template.drop(grade_template.index, inplace=True)


syllabus_template = pd.DataFrame({
                            'Stt': '', 
                            'Mã MH': '', 
                            'Tên môn học': '', 
                            'Số tín chỉ': '', 
                            'Môn bắt buộc': '', 
                            'Đã học': '',
                            'Nhóm': '', 
                            'Nhánh': '', 
                            'Số tín chỉ tối thiểu': '', 
                            'Số tín chỉ tối đa': '',
                            'Môn học đã học và đạt': '', 
                            'Tổng tiết': '', 
                            'Lý thuyết': '', 
                            'Thực hành': '',
                            'Tiết thành phần': ''
                            }, index=[''])
syllabus_template.drop(syllabus_template.index, inplace=True)


upload1 = False
upload2 = False
user_upload = st.columns((1,4,1))
with user_upload[1]:
       st.markdown(language_index['grade_upload'][english_mode])
       grade_upload = st.file_uploader(language_index['grade_upload_des'][english_mode])
       if grade_upload:
              try:
                     grade_upload = pd.read_excel(grade_upload)
                     # check unordered list of grade template columns in unordered list of grade upload columns
                     check = []
                     for item in grade_template.columns:
                            if item not in grade_upload.columns:
                                   st.session_state.grade_upload_fail = st.session_state.grade_upload_fail+1
                                   st.error(language_index['template_error'][english_mode])
                                   st.dataframe(grade_template, hide_index=True, use_container_width=True)
                                   check.append(False)
                                   break
                     if False not in check:
                            st.session_state.grade_upload = grade_upload
                            upload1 = True
              except:
                     st.error(language_index['format_error'][english_mode])

# huhu xem lại phần tracking --> done
# layout

user_upload2 = st.columns((1,4,1))
with user_upload2[1]:
       st.markdown(language_index['syllabus_upload'][english_mode])
       syllabus_upload = st.file_uploader(language_index['syllabus_upload_des'][english_mode])
       if syllabus_upload:
              try:
                     syllabus_upload = pd.read_excel(syllabus_upload)
                     # check unordered list of syllabus template columns in unordered list of syllabus upload columns
                     check = []
                     for item in syllabus_template.columns:
                            if item not in syllabus_upload.columns:
                                   st.session_state.syllabus_upload_fail = st.session_state.syllabus_upload_fail + 1
                                   st.error(language_index['template_error'][english_mode])
                                   st.dataframe(syllabus_template, hide_index=True, use_container_width=True)
                                   check.append(False)
                                   break
                     if False not in check:
                            st.session_state.syllabus_upload = syllabus_upload
                            upload2 = True
              except:
                     st.error(language_index['format_error'][english_mode])

if upload1==True and upload2==True:
       progress_bar = st.columns(3)
       submit_button = st.columns(3)
       with progress_bar[1]:
              progress_bar = st.progress(0)
              for percent in range(1, 101):
                     progress_bar.progress(percent)
                     time.sleep(0.01)            

       with submit_button[1]:
              start_button = st.button(language_index['start_button'][english_mode], use_container_width=True, key='start_button')


streamlit_analytics.stop_tracking(firestore_key_file='db_key.json', firestore_collection_name='app_metrics')
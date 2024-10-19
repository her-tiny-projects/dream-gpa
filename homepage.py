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
import json, toml
import time
from datetime import datetime

from grade_xlsx2df import grade_xlsx2df
from syllabus_xlsx2df import syllabus_xlsx2df

st.set_page_config(
       page_title='Dream GPA',
       layout='wide',
       initial_sidebar_state='expanded',
       page_icon='pisces.png'
)


st.logo(image='dream_gpa_logo.png', icon_image='dream_gpa_icon.png', size='medium')

# 1. language mode
langugage_index = {'welcome': ['Xin chào', 'Welcome'],
             'upload_data': ['Tải lên dữ liệu', 'Data Upload'],
             'report_bugs': ['Báo lỗi', 'Bugs'],
             'overview': ['Tổng quan', 'Overview'],
             'visualization': ['Kết quả học tập', 'Study Dashboard'],
             'planning': ['Kế hoạch học tập', 'GPA Planning'],
             'feedback': ['Góp ý', 'Feedback'],
             'reset': ['Thoát', 'Reset']}


# 2. initiate shared vars
empty_table = pd.DataFrame(columns=['temp'], index=[''])
empty_table.drop(empty_table.index, inplace=True)


if 'start_button' not in st.session_state:
       st.session_state.start_button = 0
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
if  'max_credit' not in st.session_state:
       st.session_state.max_credit = None
if 'target_gpa' not in st.session_state:
       st.session_state.target_gpa = None
if 'english_mode' not in st.session_state:
       st.session_state.english_mode = None


# 3. pages & layout
with st.sidebar:
       english_mode = st.toggle('EN')
       english_mode = 1 if english_mode == True else 0
       st.session_state.english_mode = english_mode



intro_n_contact = st.Page('intro_n_contact.py', title=langugage_index['welcome'][english_mode], icon=':material/home:')
upload_login = st.Page('upload_login.py', title=langugage_index['upload_data'][english_mode], icon=':material/cloud_upload:')
bug_report = st.Page('bug_report.py', title=langugage_index['report_bugs'][english_mode], icon=':material/brightness_alert:')
grade_subject_overview = st.Page('grade_subject_overview.py', title=langugage_index['overview'][english_mode], icon=':material/table:')
visualization = st.Page('visualization.py', title=langugage_index['visualization'][english_mode], icon=':material/dashboard:')
gpa_planning = st.Page('gpa_planning.py', title=langugage_index['planning'][english_mode], icon=':material/calculate:')
feedback = st.Page('feedback.py', title=langugage_index['feedback'][english_mode], icon=':material/add_comment:')


if st.session_state.grade_upload.empty==False and st.session_state.syllabus_upload.empty==False:
       page = st.navigation([intro_n_contact, grade_subject_overview, visualization, gpa_planning, feedback])

       def change_onclick():
              st.session_state.grade_upload = empty_table
              st.session_state.syllabus_upload = empty_table
              st.session_state.grade_master_data = empty_table
              st.session_state.syllabus_master_data = empty_table
              st.session_state.max_credit = None
              st.session_state.target_gpa = None
              return st.session_state.grade_upload, st.session_state.syllabus_upload, st.session_state.grade_master_data, st.session_state.syllabus_master_data, st.session_state.max_credit, st.session_state.target_gpa
       
       with st.sidebar:
              reset = st.button(langugage_index['reset'][english_mode], icon=':material/logout:', on_click=change_onclick)


else:
       if (st.session_state.grade_upload_fail>=3) or (st.session_state.syllabus_upload_fail>=3):
              page = st.navigation([bug_report])
       else:
              page = st.navigation([intro_n_contact, upload_login])

page.run()




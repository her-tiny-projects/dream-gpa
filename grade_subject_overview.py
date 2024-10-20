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

# from upload_login import grade_upload, syllabus_upload

empty_table = pd.DataFrame(columns=['temp'], index=[''])
empty_table.drop(empty_table.index, inplace=True)


if 'grade_upload' not in st.session_state:
       st.session_state.grade_upload = empty_table
if 'syllabus_upload' not in st.session_state:
       st.session_state.syllabus_upload = empty_table
if 'grade_master_data' not in st.session_state:
       st.session_state.grade_master_data = empty_table
if 'syllabus_master_data' not in st.session_state:
       st.session_state.syllabus_master_data = empty_table
if 'current_max_credit' not in st.session_state:
       st.session_state.current_max_credit = 0

if st.session_state.grade_upload.empty == False:
       st.session_state.grade_master_data = grade_xlsx2df.convert_xlsx2df(st.session_state.grade_upload)
       grade_master_data = st.session_state.grade_master_data
       st.markdown('### BẢNG ĐIỂM')
       st.dataframe(grade_master_data.set_index(grade_master_data.columns[4]))

if st.session_state.syllabus_upload.empty == False:
       st.session_state.syllabus_master_data = syllabus_xlsx2df.convert_xlsx2df(st.session_state.syllabus_upload)
       syllabus_master_data = st.session_state.syllabus_master_data
       st.markdown('### CHƯƠNG TRÌNH ĐÀO TẠO')
       st.dataframe(syllabus_master_data.set_index(syllabus_master_data.columns[3]))

st.session_state.current_max_credit = grade_master_data['Số tín chỉ tích lũy'].max()
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




# CONNECT WITH FIREBASE DB
key_dict = json.loads(st.secrets['credentials']) # streamlit load key.toml --> toml strings = json strings --> json.loads (to load json strings)
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)



# PAGE CONFIG:

st.set_page_config(
       page_title='Dream GPA',
       layout='wide',
       initial_sidebar_state='expanded'
)

title_font_size = 18

# # # HOW TO TRACK: STREAMLIT + FIREBASE

empty_table = pd.DataFrame(columns=['temp'], index=[''])
empty_table.drop(empty_table.index, inplace=True)

# initiate shared variables:
if 'logged_in' not in st.session_state:
       st.session_state.logged_in = False
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
if  'max_credit' not in st.session_state:
       st.session_state.max_credit = None
if 'target_gpa' not in st.session_state:
       st.session_state.target_gpa = None




# 1. HDSD & CONTACT
video = st.columns((1,2,1))
# link_youtube = 'https://www.youtube.com/watch?v=J8GODfmKRHw&list=PLtqF5YXg7GLn0WWB_wQx7wHrIvbs0EH2e&index=2' # example
# video[1].video(link_youtube)

contact = st.columns((1,1,1))
st.markdown('LIÊN HỆ VỚI MÌNH:')
with contact[1]:
       sky_content = 'Bạn có thể nhắn mình qua Skype tại đây'
       skype_link = 'https://join.skype.com/invite/x7OxEPJyQ4tb'
       github_content = 'Xem thêm dự án của mình tại đây'
       github_link = ''
       

logo = ''
# st.logo
# ----------------------------------------------------------------------


# 2. LOGIN --> check
# streamlit_analytics.start_tracking(firestore_key_file='.streamlit/db_key.json', firestore_collection_name='app_analytics')
grade_template = pd.DataFrame({
                            'Stt': '',
                            'Mã MH': '',
                            'Môn thay thế': '',
                            'Nhóm/tổ môn học': '',
                            'Tên môn học': '',
                            'HK chuyển': '',
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



user_upload = st.columns((1,4,1))
with user_upload[1]:
       st.markdown('### UPLOAD BẢNG ĐIỂM')
       grade_upload = st.file_uploader('Download bảng điểm ở ftugate và upload vào ô dưới:')
       try:
              if grade_upload:
                     grade_upload = pd.read_excel(grade_upload)
                     st.session_state.grade_upload = grade_upload
                     for item in grade_upload.columns:
                            if item not in grade_template.columns:
                                   st.dataframe(grade_template, hide_index=True, use_container_width=True)
                                   st.session_state.grade_upload_fail = st.session_state.grade_upload_fail+1
                                   st.error('File không đúng định dạng. Bạn kiểm tra xem file có giống như mẫu bảng điểm như dưới không nhé!')
                                   break
       except:
              st.error('File không đúng định dạng Excel!')

# huhu xem lại phần tracking --> done
# layout

user_upload2 = st.columns((1,4,1))
with user_upload2[1]:
       st.markdown('### UPLOAD CHƯƠNG TRÌNH ĐÀO TẠO')
       syllabus_upload = st.file_uploader('Download chương trình đào tạo ở ftugate và upload vào ô dưới:')
       try:
              if syllabus_upload:
                     syllabus_upload = pd.read_excel(syllabus_upload)
                     st.session_state.syllabus_upload = syllabus_upload
                     for item in syllabus_upload.columns:
                            if item not in syllabus_template.columns:
                                   st.dataframe(syllabus_template, hide_index=True, use_container_width=True)
                                   st.session_state.syllabus_upload_fail = st.session_state.syllabus_upload_fail + 1
                                   st.error('File không đúng định dạng. Bạn kiểm tra xem file có giống như mẫu bên dưới không nhé!')
                                   break
       except:
              st.error('File không đúng định dạng Excel!')


if isinstance(grade_upload, pd.DataFrame) and isinstance(syllabus_upload, pd.DataFrame):
       submit_button = st.columns(5)
       progress_bar = st.columns(3)
       with submit_button[2]:
              start_button = st.button('BẮT ĐẦU', use_container_width=True, key='start_button')
              if st.session_state.start_button==True:
                     progress_bar = st.progress(0)
                     for percent in range(1, 101):
                            progress_bar.progress(percent)
                            time.sleep(0.01)

# streamlit_analytics.stop_tracking(firestore_key_file='.streamlit/db_key.json', firestore_collection_name='app_analytics')


# bug_report = st.Page('bug_report.py', title='Báo lỗi')
# if 'login_status' not in st.session_state:
#        login_status = False
# if (st.session_state.grade_upload_fail>=3 and grade_upload==False) or (st.session_state.syllabus_upload_fail>=3 and syllabus_upload==False):



# - UI login
# - choose language
# - st.session_state


# Note:
#- Bắt buộc dùng Chrome để truy cập --> test trên device khác xem work không





# 3. OVERVIEW (successfully login)


# noteeeeeeeeeee:
# format trường học kỳ từ ff,fff về fffff
# cái bảng nó bị 'rung rinh'
# sidebar, expander

if st.session_state.grade_upload.empty == False:
       grade = st.session_state.grade_upload
       st.session_state.grade_master_data = grade_xlsx2df.convert_xlsx2df(grade)
       grade_master_data = st.session_state.grade_master_data
       st.markdown('### BẢNG ĐIỂM')
       st.dataframe(grade_master_data.set_index(grade_master_data.columns[4]))

if st.session_state.syllabus_upload.empty == False:
       syllabus = st.session_state.syllabus_upload
       st.session_state.syllabus_master_data = syllabus_xlsx2df.convert_xlsx2df(syllabus)
       syllabus_master_data = st.session_state.syllabus_master_data
       st.markdown('### CHƯƠNG TRÌNH ĐÀO TẠO')
       st.dataframe(syllabus_master_data.set_index(syllabus_master_data.columns[3]))




# noteee:
# - lưu cache
# - layout: multipagee & layout for each page



# add các biến quy định chung cho chart


# 4. VISUALIZATION
if st.session_state.grade_master_data.empty == False:
       current_max_credit = grade_master_data['Số tín chỉ tích lũy'].max() # current credits accumulated
       row_current_max_credit = grade_master_data.loc[grade_master_data['Số tín chỉ tích lũy']==current_max_credit]

       current_gpa4 = row_current_max_credit['Điểm trung bình tích lũy hệ 4'].unique()[0]
       current_gpa4 = float('{:.2f}'.format(current_gpa4))

       current_gpa10 = row_current_max_credit['Điểm trung bình tích lũy hệ 10'].unique()[0]
       current_gpa10 = float('{:.2f}'.format(current_gpa10))


       visual_usecols = ['Học kỳ đăng ký học', 'Tên môn học', 'Điểm trung bình học kỳ hệ 4', 'Điểm trung bình tích lũy hệ 4', 'Điểm trung bình học kỳ hệ 10', 'Điểm trung bình tích lũy hệ 10', 'Số tín chỉ đạt học kỳ', 'Số tín chỉ tích lũy', 'Số tín chỉ', 'Điểm TK (C)'] # BIGNOTE: 'Không tín vào Điểm trung bình tích lũy'
       gpa_bysemester = grade_master_data[visual_usecols]



       # 2. LEARNING OVERVIEW
       # * Chỉ xét các môn/ tín chỉ được tính vào điểm trung bình chung tích lũy
       # OVERVIEW
       # THỐNG KÊ ĐIỂM
       # THỐNG KÊ TÍN CHỈ, MÔN HỌC



       def number(chart_name, input_number):
              fig = go.Figure()
              fig.add_trace(
                     go.Indicator(
                            mode='number',
                            value=input_number
                            )
                     )
              fig.update_layout(
                     title=dict(
                            text=chart_name,
                            x=0.3,
                            y=0.95,
                            font=dict(size=title_font_size)
                     ),
                     autosize=True,
                     height=100,
                     margin=dict(
                            l=10,
                            r=10,
                            t=10,
                            b=10)
                     )
              st.plotly_chart(fig, use_container_width=True)


       # note: fix line gì xuất hiện trước, line gì xuất hiện sau
       def double_line(gpa_bysemester, scale):
              scale = str(scale)
              gpa_bysemester = gpa_bysemester.sort_values(by='Học kỳ đăng ký học', ascending=True)
              x = gpa_bysemester['Học kỳ đăng ký học']
              y_line1 = gpa_bysemester[f'Điểm trung bình học kỳ hệ {scale}'].apply(lambda x: round(x, 2))
              y_line2 = gpa_bysemester[f'Điểm trung bình tích lũy hệ {scale}'].apply(lambda x: round(x, 2))

              fig = go.Figure()
              fig = fig.add_trace(
                     go.Scatter(
                            x=x,
                            y=y_line1,
                            mode='lines+markers+text',
                            text=y_line1,
                            textposition='middle right',
                            hovertemplate='Điểm TB: %{y} <br>Tại kỳ: %{x}',
                            name='Điểm TB trong kỳ học'
                     ))

              fig = fig.add_trace(
                     go.Scatter(
                            x=x,
                            y=y_line2,
                            mode='lines+markers+text',
                            text=y_line2,
                            textposition='middle right',
                            hovertemplate='Điểm TB tích lũy: %{y} <br>Tính đến kỳ: %{x}',
                            name='Điểm TB tích lũy đến kỳ học'
                     ))

              fig.update_traces(textposition='top center')
              fig.update_layout(autosize=True,
                            title=dict(
                                   text=f'GPA thang {scale} theo Học kỳ',
                                   x=0.4,
                                   y=1,
                                   font=dict(size=title_font_size)
                            ),
                            legend=dict(
                                   title='',
                                   orientation='h',
                                   xanchor='left',
                                   yanchor='top',
                                   x=0.2,
                                   y=-0.5

                            ),
                            width=600,
                            height=300,
                            margin=dict(
                                   l=10,
                                   r=10,
                                   t=10,
                                   b=10
                            ))
              fig.update_xaxes(tickangle=-30)
              fig.update_yaxes(visible=False)
              st.plotly_chart(fig, use_container_with=True)



       def bar_line(gpa_bysemester):
              q = """
              WITH eligible_credit AS
                     (SELECT DISTINCT
                            "Học kỳ đăng ký học",
                            "Số tín chỉ đạt học kỳ" AS "Số tín chỉ tích lũy trong kỳ",
                            "Số tín chỉ tích lũy" AS "Số tín chỉ tích lũy lũy kế"
                     FROM gpa_bysemester),

              registered_credit AS
                     (SELECT
                            "Học kỳ đăng ký học",
                            SUM("Số tín chỉ") AS "Số tín chỉ đăng ký trong kỳ"
                     FROM gpa_bysemester
                     GROUP BY "Học kỳ đăng ký học")

              SELECT *,
                     SUM("Số tín chỉ đăng ký trong kỳ") OVER (ORDER BY "Học kỳ đăng ký học" ASC) AS "Số tín chỉ đăng ký lũy kế"
              FROM registered_credit
              LEFT JOIN eligible_credit USING ("Học kỳ đăng ký học")
              ORDER BY "Học kỳ đăng ký học"
              """
              credit_bysemester = duckdb.sql(q).df()
              x = credit_bysemester['Học kỳ đăng ký học']
              bar_y1 = credit_bysemester['Số tín chỉ đăng ký trong kỳ']
              bar_y2 = credit_bysemester['Số tín chỉ tích lũy trong kỳ']
              line_y3 = credit_bysemester['Số tín chỉ đăng ký lũy kế']
              line_y4 = credit_bysemester['Số tín chỉ tích lũy lũy kế']


              fig = go.Figure()
              fig = fig.add_trace(
                     go.Bar(
                            x=x,
                            y=bar_y1,
                            text=bar_y1,
                            textposition='auto',
                            textangle=0,
                            hovertemplate='Số tín chỉ đăng ký: %{y}<br>Xét trong kỳ: %{x}',
                            name='Số tín chỉ đăng ký trong kỳ'
                     )
              )
              fig = fig.add_trace(
                     go.Bar(
                            x=x,
                            y=bar_y2,
                            text=bar_y2,
                            textposition='auto',
                            textangle=0,
                            hovertemplate='Số tín chỉ tính vào điểm TB: %{y}<br>Xét trong kỳ: %{x}',
                            name='Số tín chỉ tích lũy trong kỳ'
                     )
              )
              fig = fig.add_trace(
                     go.Scatter(
                            x=x,
                            y=line_y3,
                            line_color='#ff6962',
                            mode='lines+markers+text',
                            text=line_y3,
                            textposition='middle right',
                            hovertemplate='Số tín chỉ đăng ký lũy kế: %{y} <br>Tính đến: %{x}',
                            name='Số tín chỉ đăng ký lũy kế'
                     )
              )
              fig = fig.add_trace(
                     go.Scatter(
                            x=x,
                            y=line_y4,
                            line_color='#ffa9a9',
                            mode='lines+markers+text',
                            text=line_y4,
                            textposition='middle right',
                            hovertemplate='Số tín chỉ tích lũy kế: %{y} <br>Tính đến: %{x}',
                            name='Số tín chỉ tích lũy lũy kế'
                     )
              )
              fig.update_layout(
                     title=dict(
                            text='Số tín chỉ theo Kỳ học',
                            x=0.4,
                            y=0.95,
                            font=dict(size=title_font_size)
                     ),
                     xaxis_title='Học kỳ',
                     legend=dict(
                            title='',
                            orientation='h',
                            xanchor='left',
                            yanchor='top',
                            # x=0.2,
                            y=-0.5

                     ),
                     width=600,
                     height=300,
                     margin=dict(
                            l=10,
                            r=10,
                            t=10,
                            b=10
                     ))
              fig.update_xaxes(tickangle=-30)
              fig.update_yaxes(visible=False)
              st.plotly_chart(fig, use_container_with=True)


       def bar(gpa_bysemester):
              q = """
              SELECT DISTINCT
                     CASE WHEN "Điểm TK (C)" IS NULL THEN 'UNKNOWN' ELSE "Điểm TK (C)"  END AS "Điểm tổng kết Chữ",
                     SUM("Số tín chỉ") AS "Số tín chỉ",
                     COUNT("Số tín chỉ") AS "Số môn"
              FROM gpa_bysemester
              GROUP BY "Điểm TK (C)"
              ORDER BY "Điểm TK (C)"
              """
              groupby_grade = duckdb.sql(q).df()
              x = groupby_grade['Điểm tổng kết Chữ']
              bar_y1 = groupby_grade['Số tín chỉ']
              bar_y2 = groupby_grade['Số môn']

              fig = go.Figure()
              fig = fig.add_trace(
                     go.Bar(
                            x=x,
                            y=bar_y1,
                            name='Số tín chỉ',
                            text=bar_y1,
                            textposition='auto',
                            hovertemplate='Số tín chỉ đạt %{x}: %{y}'
                     )
              )
              fig = fig.add_trace(
                     go.Bar(
                            x=x,
                            y=bar_y2,
                            name='Số môn',
                            text=bar_y2,
                            textposition='auto',
                            hovertemplate='Số môn đạt %{x}: %{y}'
                     )
              )

              fig.update_layout(
                     title=dict(
                            text='Số tín chỉ, Số môn theo Điểm chữ<br><i>(Dựa trên kết quả của tất cả các tín chỉ đã đăng ký)',
                            x=0.4,
                            y=0.95,
                            font=dict(size=title_font_size)
                     ),
                     title_xanchor='center',
                     title_x=0.45,
                     xaxis_title='Điểm tổng kết Chữ',
                     legend=dict(
                            title='',
                            orientation='h',
                            xanchor='left',
                            yanchor='top',
                            x=0.2,
                            y=-0.5

                     ),
                     width=600,
                     height=300,
                     margin=dict(
                            l=10,
                            r=10,
                            t=10,
                            b=10
                     ))
              fig.update_yaxes(visible=False) 
              st.plotly_chart(fig, use_container_with=True)

       # Note: color scheme for all charts: red



       # LAYOUT:
       # overview
       st.markdown('### TỔNG QUAN')
       overview_1, overview_2, overview_3 = st.columns((1,1,1))
       with overview_1:
              chart_name = 'Điểm trên thang 4'
              input_number = current_gpa4
              number(chart_name, input_number)
       with overview_2:
              chart_name = 'Điểm trên thang 10'
              input_number = current_gpa10
              number(chart_name, input_number)
       with overview_3:
              chart_name = 'Số tín chỉ đã tích lũy'
              input_number = current_max_credit
              number(chart_name, input_number)



       # gpa
       st.markdown('### THỐNG KÊ ĐIỂM SỐ')
       gpa_4, gpa_10 = st.columns((1,1))
       with gpa_4:
              double_line(gpa_bysemester, 4)

       with gpa_10:
              double_line(gpa_bysemester, 10)


       # credit
       st.markdown('### THỐNG KÊ TÍN CHỈ')
       credit_bysemester, credit_byabcdf = st.columns((1,1))
       with credit_bysemester:
              bar_line(gpa_bysemester)
              # note: số tín chỉ tích lũy trong kỳ khi cộng dồn có thể # Số tín chỉ tích lũy lũy kế do học cải thiện
       with credit_byabcdf:
              bar(gpa_bysemester)



# 5. STUDY PLAN - KẾ HOẠCH HỌC TẬP:
# * HỌC PHẦN BẮT BUỘC: MAX=...
       # MÔN BẮT BUỘC D, F --> Học cải thiện, học lại
       # MÔN BẮT BUỘC CÒN PHẢI HỌC
# * HỌC PHẦN TỰ CHỌN: MAX=
       # MÔN TỰ CHỌN DƯỚI B --> Học lại hoặc Học môn khác với điểm cao hơn
       # MÔN TỰ CHỌN CÓ THỂ HỌC
# HỌC PHẦN TỐT NGHIỆP

# Note: 
# how many checkboxes tick --> validate with max
# column hóa 3 cục ở dưới



# 4 CRITERIA:
       # all subject
       # max credits
       # tolearn/ relearn subject
       # credits remaining

if st.session_state.grade_master_data.empty == False and st.session_state.syllabus_master_data.empty == False:
       # max grade per subject
       q = """
              WITH rank_grade_subject_learned AS (
                     SELECT
                            "Học kỳ đăng ký học",
                            "Mã môn học",
                            "Điểm TK (C)",
                            "Điểm TK (4)",
                            DENSE_RANK() OVER (PARTITION BY "Mã môn học" ORDER BY "Điểm TK (4)" DESC) AS MAX_GRADE
                     FROM grade_master_data
                     ),

              max_grade_subject_learned AS (
                     SELECT DISTINCT
                            "Học kỳ đăng ký học",
                            "Mã môn học",
                            1 AS "Đã học",
                            "Điểm TK (C)",
                            "Điểm TK (4)"
                     FROM rank_grade_subject_learned
                     WHERE MAX_GRADE = 1
                     )

              SELECT * FROM max_grade_subject_learned
       """
       max_grade_subject_learned = duckdb.sql(q).df()


       q = """
              SELECT 
                     *
              FROM syllabus_master_data t1
              LEFT JOIN max_grade_subject_learned USING("Mã môn học")
              WHERE "Mã môn học" NOT IN
                     (SELECT DISTINCT "Mã môn học"
                     FROM syllabus_master_data
                     WHERE "Mã môn học" IN ('GDQP', 'GDTC1', 'GDTC2', 'GDTC3')
                     OR LOWER("Tên môn học") LIKE '%quốc phòng%'
                     OR LOWER("Tên môn học") LIKE '%thể chất%')
       """
       syllabus_grade_master_data = duckdb.sql(q).df()
       syllabus_grade_master_data.insert(0, 'Checkbox', False)


       st.markdown("""## 1. ĐĂNG KÝ MÔN HỌC""")
       # max_credit = 160 # note: thêm box input
       input_max_credit, blank, input_target_gpa = st.columns((1, 0.25, 1))
       with input_max_credit:
              st.session_state.max_credit = st.number_input('#### :small_orange_diamond: Nhập tổng số tín chỉ cần tích lũy:', min_value=0, value=None)
              max_credit = st.session_state.max_credit
              st.write('Số tín chỉ của chương trình học (không tính quốc phòng, thể chất): ', max_credit)

       with input_target_gpa:
              st.session_state.target_gpa = st.number_input('#### :small_orange_diamond: Nhập GPA mục tiêu (thang 4)', min_value=0.00, max_value=4.00, value=None)
              target_gpa = st.session_state.target_gpa
              st.write('GPA mục tiêu: ', target_gpa)


       st.markdown('#### :small_orange_diamond: Tick chọn các môn bạn dự kiến học:')
       mandatory1, elective1, thesis1 = st.columns(3)
       mandatory2, elective2, thesis2 = st.columns(3)
       mandatory3, elective3, thesis3 = st.columns(3)
       # mandatory_status, elective_status, thesis_status = st.columns(3)
       empty_registered_table = pd.DataFrame({
              "Checkbox": '', 
              "Mã môn học": '', 
              "Số tín chỉ": ''},
              index=['Mã môn học'])
       empty_registered_table.drop(empty_registered_table.index, inplace=True)
       # 1. MANDATORY:
       if max_credit and target_gpa:
              q = """
                     SELECT 
                            *
                     FROM syllabus_grade_master_data
                     WHERE "Môn bắt buộc" IS NOT NULL
                     AND "Số tín chỉ" <= 3 -- Loại bỏ các học phần như Khóa luận tốt nghiệp 9 tín chỉ
              """
              mandatory_subject = duckdb.sql(q).df()
              max_mandatory_credit = mandatory_subject['Số tín chỉ'].sum()


              q = """
                     SELECT
                            "Checkbox",
                            "Mã môn học",
                            "Tên môn học",
                            "Số tín chỉ"
                     FROM mandatory_subject
                     WHERE "Đã học" IS NULL
                     ORDER BY "Học kỳ dự kiến học"
              """
              mandatory_subject_tolearn = duckdb.sql(q).df()
              mandatory_credit_tolearn = mandatory_subject_tolearn['Số tín chỉ'].sum()


              q = """
                     SELECT
                            "Checkbox",
                            "Mã môn học",
                            "Tên môn học",
                            "Số tín chỉ",
                            "Điểm TK (C)"
                     FROM mandatory_subject
                     WHERE "Đã học" IS NOT NULL
                     AND "Điểm TK (C)" IN ('D', 'F')
                     ORDER BY "Học kỳ dự kiến học"
              """
              mandatory_subject_relearn = duckdb.sql(q).df()
              mandatory_credit_relearn = mandatory_subject_relearn['Số tín chỉ'].sum()

              mandatory_credit_remaining = mandatory_credit_tolearn + mandatory_credit_relearn

              with mandatory1:
                     st.info(f'###### Học phần Bắt buộc')
                     st.markdown(':small_orange_diamond: Môn bắt buộc còn phải học')
                     # check empty
                     if mandatory_credit_tolearn == 0:
                            st.dataframe(mandatory_subject_tolearn, 
                                   hide_index=True, 
                                   height=170,
                                   use_container_width=True)
                     # create df
                     else:
                            mandatory_subject_tolearn = st.data_editor(
                                   mandatory_subject_tolearn,
                                   column_config={
                                          'Checkbox': st.column_config.CheckboxColumn(
                                                 help='Tick vào môn bạn **dự kiến** học',
                                                 default=False # Default value when new row added by user
                                          )
                                   },
                                   disabled=['Mã môn học', 'Tên môn học', 'Số tín chỉ'],
                                   hide_index=True,
                                   height=170,
                                   use_container_width=True
                            )
                     # validate input
                     if mandatory_subject_tolearn.empty == True:
                            mandatory_subject_registered1 = empty_registered_table
                            mandatory_credit_registered1 = mandatory_subject_registered1['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**-/-**] tín chỉ*')
                     else:
                            q = """
                            SELECT "Checkbox", "Mã môn học", "Số tín chỉ"
                            FROM mandatory_subject_tolearn
                            WHERE "Checkbox" = TRUE
                            """
                            mandatory_subject_registered1 = duckdb.sql(q).df()
                            mandatory_credit_registered1 = mandatory_subject_registered1['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**{int(mandatory_credit_registered1)}/{int(mandatory_credit_tolearn)}**] tín chỉ*')


              with mandatory2:
                     st.markdown('---')
                     st.markdown(':small_orange_diamond: Môn bắt buộc điểm D/ F có thể cải thiện/ học lại')
                     if mandatory_credit_relearn == 0:
                            st.dataframe(mandatory_subject_relearn, 
                                   hide_index=True, 
                                   height=170,
                                   use_container_width=True)
                            # st.success('Bạn không có học phần Bắt buộc nào để học cải hiện/ học lại')
                     else:
                            mandatory_subject_relearn = st.data_editor(
                                   mandatory_subject_relearn,
                                   column_config={
                                          'Checkbox': st.column_config.CheckboxColumn(
                                                 help='Tick vào môn bạn **dự kiến** học',
                                                 default=False
                                          )
                                   },
                                   disabled=['Mã môn học', 'Tên môn học', 'Số tín chỉ', 'Điểm TK (C)'],
                                   hide_index=True,
                                   height=170,
                                   use_container_width=True
                            )
                            
                     if mandatory_subject_relearn.empty == True:
                            mandatory_subject_registered2 = empty_registered_table
                            mandatory_credit_registered2 = mandatory_subject_registered2['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**-/-**] tín chỉ*')
                     else:
                            q = """
                            SELECT "Checkbox", "Mã môn học", "Số tín chỉ"
                            FROM mandatory_subject_relearn
                            WHERE "Checkbox" = TRUE
                            """
                            mandatory_subject_registered2 = duckdb.sql(q).df()
                            mandatory_credit_registered2 = mandatory_subject_registered2['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**{int(mandatory_credit_registered2)}/{int(mandatory_subject_relearn)}**] tín chỉ*')


       # 2. THESIS       
       if max_credit and target_gpa:
              # note: check xem ở chuyên ngành khác thì nhóm học phần tốt nghiệp có = 9 --> không --> dựa vào keyword   
              with thesis1:
                     q = """
                            SELECT
                                   "Checkbox",
                                   "Mã môn học",
                                   "Tên môn học",
                                   "Số tín chỉ",
                                   "Đã học"
                            FROM syllabus_grade_master_data
                            WHERE "Nhóm" = 9
                            OR LOWER("Tên môn học") LIKE '%khóa luận%'
                     """
                     thesis_subject = duckdb.sql(q).df()
                     thesis_credit = 9
                     thesis_learned = thesis_subject[thesis_subject['Đã học']=='x']['Số tín chỉ'].sum()
                     thesis_credit_remaining = thesis_credit - thesis_learned

                     st.info('###### Học phần Tốt nghiệp')
                     st.markdown(':small_orange_diamond:')

                     #check available thesis credits to register
                     if thesis_learned == thesis_credit: # completed
                            thesis_subject.drop(thesis_subject.index, inplace=True)
                            st.dataframe(
                                   thesis_subject, 
                                   hide_index=True,
                                   height=170,
                                   use_container_width=True)
                            thesis_subject_registered = thesis_subject[['Checkbox', 'Mã môn học', 'Số tín chỉ']]
                     else: # not completed --> ok to register
                            thesis_subject = thesis_subject[thesis_subject['Đã học'] != 'x']
                            thesis_subject = thesis_subject[['Checkbox', 'Mã môn học', 'Tên môn học', 'Số tín chỉ']]
                            thesis_subject = st.data_editor(
                                   thesis_subject,
                                   column_config={
                                          'Checkbox': st.column_config.CheckboxColumn(
                                                 help='Tick vào môn bạn **dự kiến** học',
                                                 default=False # Default value when new row added by user
                                          )
                                   },
                                   disabled=['Mã môn học', 'Tên môn học', 'Số tín chỉ'],
                                   hide_index=True,
                                   height=170,
                                   use_container_width=True
                            )
                     
                     # display
                     if thesis_subject.empty == True: # if completed
                            thesis_subject_registered = empty_registered_table
                            thesis_credit_registered = thesis_subject_registered['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**-/-**] tín chỉ*')

                     else: # if not completed
                            q = """
                            SELECT "Checkbox", "Mã môn học", "Số tín chỉ" 
                            FROM thesis_subject
                            WHERE "Checkbox" = TRUE
                            """
                            thesis_subject_registered = duckdb.sql(q).df()
                            thesis_credit_registered = thesis_subject_registered['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**{int(thesis_credit_registered)}/{thesis_credit_remaining}**] tín chỉ*')
                            if int(thesis_credit_registered) > int(thesis_credit_remaining):
                                   st.error('Bạn đã chọn quá số lượng tín chỉ Tốt nghiệp có thể học! \nHãy bỏ tick một số môn học nhé!')


       # 3. ELECTIVE
       if max_credit and target_gpa:
              q = """
                     SELECT 
                            *
                     FROM syllabus_grade_master_data
                     WHERE "Môn bắt buộc" IS NULL
                     AND "Nhóm" != 9
              """
              elective_subject = duckdb.sql(q).df()
              max_elective_credit = max(0, max_credit - max_mandatory_credit - thesis_credit)

       #note: elective bị dồn về nhóm 2 thì sao???? --> kệ, người dùng phải tự sắp xếp
              q = """
                     SELECT
                            *,
                            SUM("Số tín chỉ") OVER (ORDER BY "Học kỳ đăng ký học") AS "Tín chỉ tự chọn tích lũy"
                     FROM elective_subject
                     WHERE "Đã học" IS NOT NULL
              """
              accumulated_elective_subject = duckdb.sql(q).df()
              accumulated_elective_credit = accumulated_elective_subject["Tín chỉ tự chọn tích lũy"].max()
              elective_credit_tolearn = max(0, max_elective_credit - accumulated_elective_credit) # number of elective credits available to learn/ relearn to maximize grade

              q = """
                     SELECT
                            "Checkbox",
                            "Mã môn học",
                            "Tên môn học",
                            "Nhóm" AS "Nhóm tự chọn",
                            "Số tín chỉ"
                     FROM elective_subject
                     WHERE "Đã học" IS NULL
                     ORDER BY "Học kỳ dự kiến học"
              """
              elective_subject_tolearn = duckdb.sql(q).df()


              q = f"""
                     SELECT DISTINCT
                            "Checkbox",
                            "Mã môn học",
                            "Tên môn học",
                            "Nhóm" AS "Nhóm tự chọn",
                            "Số tín chỉ",
                            "Điểm TK (C)"
                     FROM accumulated_elective_subject
                     WHERE "Điểm TK (C)" IN ('D', 'F')   
                     AND "Tín chỉ tự chọn tích lũy" <= {max_elective_credit}
                     ORDER BY "Học kỳ đăng ký học"
              """
              elective_subject_relearn = duckdb.sql(q).df()
              elective_credit_relearn = elective_subject_relearn['Số tín chỉ'].sum()
              # D --> relearn; F --> relearn or replaced by another elective subject
              # ==> overall,  have to relearn both D, F to improve GPA

              elective_credit_remaining = elective_credit_tolearn + elective_credit_relearn

              with elective1:
                     st.info('###### Học phần Tự chọn')
                     st.markdown(f':small_orange_diamond: Môn tự chọn có thể học')
                     #check available elective credits to register
                     if elective_credit_tolearn == 0: # if completed
                            elective_subject_tolearn.drop(elective_subject_tolearn.index, inplace=True)
                            st.dataframe(
                                   elective_subject_tolearn,
                                   hide_index=True,
                                   height=170,
                                   use_container_width=True)

                     else:
                            elective_subject_tolearn = st.data_editor(
                                   elective_subject_tolearn,
                                   column_config={
                                          'Checkbox': st.column_config.CheckboxColumn(
                                                 help='Tick vào môn bạn **dự kiến** học',
                                                 default=False
                                          )
                                   },
                                   disabled=['Mã môn học', 'Tên môn học', 'Nhóm', 'Số tín chỉ'],
                                   hide_index=True,
                                   height=170,
                                   use_container_width=True)

                     if elective_subject_tolearn.empty == True:
                            elective_subject_registered1 = empty_registered_table
                            elective_credit_registered1 = elective_subject_registered1['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**-/-**] tín chỉ*')
                     else:
                            q = """
                            SELECT "Checkbox", "Mã môn học", "Số tín chỉ" 
                            FROM elective_subject_tolearn
                            WHERE "Checkbox" = TRUE
                            """
                            elective_subject_registered1 = duckdb.sql(q).df()
                            elective_credit_registered1 = elective_subject_registered1['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**{int(elective_credit_registered1)}/{int(elective_credit_tolearn)}**] tín chỉ*')
                            if int(elective_credit_registered1) > int(elective_credit_tolearn):
                                   st.error('Bạn đã chọn quá số lượng tín chỉ Tự chọn có thể học! \nHãy bỏ tick một số môn học nhé!')


              with elective2:
                     st.markdown('---')
                     st.markdown(f':small_orange_diamond: Môn tự chọn điểm D/ F có thể cải thiện/ học lại, thay thế')

                     if elective_credit_relearn == 0:
                            st.dataframe(
                                   elective_subject_relearn,
                                   hide_index=True,
                                   height=170,
                                   use_container_width=True)
                            # st.success('Bạn không có học phần Tự chọn nào để học cải hiện/ học lại')
                     else:
                            elective_subject_relearn = st.data_editor(
                                   elective_subject_relearn,
                                   column_config={
                                          'Checkbox': st.column_config.CheckboxColumn(
                                                 help='Tick vào môn bạn **dự kiến** học: \nĐiểm D: học lại môn này để cải thiện điểm \nĐiểm F: học lại môn này hoặc chọn môn Tự chọn khác để cải thiện điểm',
                                                 default=False
                                          )
                                   },
                                   disabled=['Mã môn học', 'Tên môn học', 'Nhóm', 'Số tín chỉ', 'Điểm TK (C)'],
                                   hide_index=True,
                                   height=170,
                                   use_container_width=True)

                     if elective_subject_relearn.empty == True:
                            elective_subject_registered2 = empty_registered_table
                            elective_credit_registered2 = elective_subject_registered2['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**-/-**] tín chỉ*')

                     else:
                            q = """
                            SELECT "Checkbox", "Mã môn học", "Số tín chỉ" 
                            FROM elective_subject_relearn
                            WHERE "Checkbox" = TRUE
                            """
                            elective_subject_registered2 = duckdb.sql(q).df()
                            elective_credit_registered2 = elective_subject_registered2['Số tín chỉ'].sum()
                            st.write(f'*Đã chọn: :red[**{int(elective_credit_registered2)}/{int(elective_credit_relearn)}**] tín chỉ*')
                            if int(elective_credit_registered2) > int(elective_credit_relearn):
                                   st.error('Bạn đã chọn quá số lượng tín Tự chọn có thể học lại, học cải thiện/ thay thế! \nHãy bỏ tick một số môn học nhé!')
       try:
              total_credit_registered = mandatory_credit_registered1 + mandatory_credit_registered2 + thesis_credit_registered + elective_credit_registered1 + elective_credit_registered2
       except:
              total_credit_registered = 0

       st.markdown("""## 2. KẾ HOẠCH HỌC TẬP""")
       content = """
              ---
              Lưu ý:
              - *Dưới đây là các kịch bản về số lượng tín chỉ A, B, C để đạt GPA mục tiêu (căn cứ theo học phần bạn đã tick ở Mục 1). Bạn cân nhắc để chọn kịch bản phù hợp với bản thân*

              - *Giả định các học phần bạn học đều đạt được điểm từ C trở lên (ngưỡng không thể thay đổi điểm bằng cách cải thiện/ học lại, học thay thế)*

              - *Khi có thêm kết quả thực tế của các học phần đã học, bạn có thể vào lại trang web này để có những điều chỉnh kế hoạch phù hợp*
              ---
              """
       st.markdown(content)
       blank1, scenario, blank2 = st.columns((1,4,1))
       if max_credit == None or target_gpa == None or int(thesis_credit_registered) > int(thesis_credit_remaining) or int(elective_credit_registered1) > int(elective_credit_tolearn) or  int(elective_credit_registered2) > int(elective_credit_relearn) or total_credit_registered==0:
              content = """
                     Để phần Kế hoạch học tập dưới đây hiện ra, bạn cần hoàn thiện Mục 1. Thử kiểm tra xem:
                     - Đã điền đúng Số tín chỉ chương trình học của bạn chưa
                     - Đã điền đúng GPA mục tiêu chưa
                     - Số tín chỉ Tick chọn cho mỗi loại học phần có vượt quá số lượng cho phép 
                     """
              scenario.warning(content)
       else:

              content = f"""
                     Bạn dự kiến đăng ký học :red[**{total_credit_registered} tín chỉ**]. Dưới đây là các kịch bản để đạt :red[**TỐI THIỂU GPA = {target_gpa}**]:
                     """
              scenario.write(content)

              # ALL SUBJECT REGISTERED TO LEARN
              q = """
                     SELECT * FROM mandatory_subject_registered1
                     UNION ALL
                     SELECT * FROM mandatory_subject_registered2
                     UNION ALL
                     SELECT * FROM thesis_subject_registered
                     UNION ALL
                     SELECT * FROM elective_subject_registered1
                     UNION ALL
                     SELECT * FROM elective_subject_registered2
              """
              subject_registered = duckdb.sql(q).df()

              q = """
                     WITH temp1 AS
                            (SELECT 
                                   "Mã môn học",
                                   "Số tín chỉ",
                                   "Điểm TK (4)"
                            FROM syllabus_grade_master_data
                            WHERE CAST("Mã môn học" AS VARCHAR) NOT IN 
                                   (SELECT CAST("Mã môn học" AS VARCHAR) FROM subject_registered)
                            AND "Điểm TK (4)" IS NOT NULL
                            ),

                     temp2 AS
                            (SELECT
                                   "Mã môn học",
                                   "Số tín chỉ",
                                   '' "Điểm TK (4)"
                            FROM subject_registered
                            )

                     (SELECT * FROM temp1
                     UNION ALL
                     SELECT * FROM temp2)
              """
              subject_calculate_gpa = duckdb.sql(q).df()
              subject_calculate_gpa['Điểm TK (4)'] = subject_calculate_gpa['Điểm TK (4)'].apply(lambda x: int(float(x)) if x != '' else np.nan)
              subject_calculate_gpa['Tín chỉ x Điểm'] = subject_calculate_gpa['Số tín chỉ']*subject_calculate_gpa['Điểm TK (4)']


              credit_calculate_gpa = subject_calculate_gpa['Số tín chỉ'].sum()
              credit_grade_accumulated = subject_calculate_gpa['Tín chỉ x Điểm'].sum()
              # credit_grade_tobe_accumulated = target_gpa*credit_calculate_gpa - credit_grade_accumulated
              credit_tobe_accumulated = subject_registered['Số tín chỉ'].sum()


              def sublist(mylist):
                     n = len(mylist)
                     sublist = []
                     for start in range(n):
                            for end in range(start+1, n+1):
                                   item = mylist[start:end]
                                   if item not in sublist:
                                          sublist.append(item)
                     return sublist
              
              def sum_sublist(sublist):
                     sum_sublist = [0] # default value = 0: 0 có tín chỉ nào thỏa mãn
                     for item in sublist:
                            sum_ = sum(item)
                            if sum_ not in sum_sublist:
                                   sum_sublist.append(sum_)
                     return sum_sublist

              
              mylist = subject_registered['Số tín chỉ'].tolist()
              sublist = sublist(mylist)
              sum_sublist = sum_sublist(sublist)

              # X, Y, Z: no. credits in accordance with A(4), B(3), C(2) --> 0 <= X, Y, Z <= credit_tobe_accumulated
              # credit_grade_tobe_accumulated = 4X + 3Y + 2Z
              # credit_tobe_accumulated = X + Y + Z
              # -credit_grade_tobe_accumulated + 4credit_tobe_accumulated = Y + 2Z

              gradeA = []
              gradeB = []
              gradeC = []
              gpa = []
              for x in range(0, credit_tobe_accumulated+1):
                     for y in range(0, credit_tobe_accumulated+1):
                            for z in range(0, credit_tobe_accumulated+1):
                                   if (x+y+z) != credit_tobe_accumulated:
                                          continue
                                   else:
                                          credit_grade_tobe_accumulated = 4*x+3*y+2*z
                                          target_gpa_calculate = (credit_grade_tobe_accumulated+credit_grade_accumulated)/credit_calculate_gpa
                                          if target_gpa_calculate >= target_gpa and x in sum_sublist and y in sum_sublist and z in sum_sublist:
                                                 gradeA.append(x)
                                                 gradeB.append(y)
                                                 gradeC.append(z)
                                                 gpa.append(target_gpa_calculate)

              # for z in range(0, credit_tobe_accumulated+1):
              #        y = (-1)*credit_grade_tobe_accumulated + 4*credit_tobe_accumulated - 2*z
              #        y = ceil(y)
              #        if y>0 and (y+z)<=credit_tobe_accumulated:
              #               x = int(credit_tobe_accumulated - y - z)
              #               gradeA.append(x)
              #               gradeB.append(y)
              #               gradeC.append(z)

              df = pd.DataFrame({'Kịch bản': range(1, len(gradeA)+1),
                            'Số tín chỉ A': gradeA,
                            'Số tín chỉ B': gradeB,
                            'Số tín chỉ C': gradeC,
                            'GPA dự kiến': gpa
                            })
              

              if df.empty == True:
                     col = st.columns((1,4,1))
                     col[1].warning('GPA này có vẻ như không thực hiện được rồi, bạn xem lại nhé :worried:')
                     scenario.dataframe(df, hide_index=True, use_container_width=True)
              else:
                     scenario.dataframe(df.style.highlight_max(subset=['GPA dự kiến'], color='red'), hide_index=True, use_container_width=True)



# YAYYYYYYYY đã xong phần nội dung từng page. Next:
# - tạo class cho từng page & tạo homepage --> partially done
# - multiple page
# - session state --> save user data input
# - cache: how does it work



# NOTE
# CHECK LAJIIIIIIIIIIIIIIIIIIIIII LOGICCCCCCCCCCCC
# BỔ SUNG SESSION STATE CHO CÁC INPUT TỪ USERS


# CHECK LẠI VỀ ĐIỀU KIỆN VALIDATE TÍN CHỈ MÔN TỰ CHỌN CÓ THỂ HỌC
# MAX TÍN CHỈ TỰ CHỌN = MAX TÍN CHỈ - TÍN CHỈ BẮT BUỘC - 9 





# bổ sung check, error when count(checkboxed)> max_check, đặc biệt cho học phần tự chọn




# LAYOUT: tập hợp các note

# LANGUAGE CONTROL:
       # INDEX: VN, EN
       # HEADING 1, 2, 3/ CONTENT
# THÔNG TIN LIÊN HỆ



# 6. FEEDBACK FORM:
form, blank = st.columns((3,2))
with form:
       with st.form(key='feedback_form', clear_on_submit=True):
              st.markdown('# :envelope: GÓC GÓP Ý')
              form_id = str(round(time.time()))
              form_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
              form_rating_usefull = st.slider(label='Mức độ hữu ích:red[*]', min_value=0, max_value=5, help='Có phục vụ bạn trong việc theo dõi kết quả và lên kế hoạch học tập không (Điểm từ 1-5):\n\n1 - Không hữu ích\n\n2 - Có một chút hữu ích\n\n3 - Khá hữu ích\n\n4 - Hữu ích\n\n5 - Rất hữu ích')
              form_rating_userfriendly = st.slider(label='Mức độ dễ sử dụng:red[*]', min_value=0, 
              max_value=5, step=1, help='Bạn có thấy ứng dụng dễ sử dụng, thao tác không (Điểm từ 1-5):\n\n1 - Rất khó sử dụng\n\n2 - Khó sử dụng\n\n3 - Trung bình\n\n4 - Dễ sử dụng\n\n5 - Rất dễ sử dụng')
              form_feedback = st.text_area(label='Cho mình xin thêm ý kiến về App nha', help='Bạn có thể gửi bất cứ nhắn gì cho mình qua feedback form này nha. Một số gợi ý:\n\n- Bạn có thể chia sẻ cảm nhận khi sử dụng mini app này\n\n- Bạn muốn mình thêm tính năng gì để phục vụ học tập\n\n- Bạn thấy có chỗ nào bị lỗi, khó hiểu hoặc chưa giải thích rõ không,...\n\nMình cảm ơn ý kiến đóng góp của bạn :>')
              form_email = st.text_input(label='Email của bạn')
              form_name = st.text_input(label='Tên của bạn')
              submit_button = st.form_submit_button('Submit')
              if submit_button:
                     # check whether all mandatory fields are filled
                     if form_rating_usefull==0 or form_rating_userfriendly==0:
                            if form_feedback:
                                   st.error(f"Bạn cần đánh giá **Mức độ hữu ích** và **Mức độ dễ sử dụng** trước khi ấn Submit\n\nChỉnh sửa gần đây của bạn: *'{form_feedback}'*")
                            else:
                                   st.error('Bạn cần đánh giá **Mức độ hữu ích** và **Mức độ dễ sử dụng** trước khi ấn Submit')
                     else:
                            st.success('Bạn đã Submit thành công. Cảm ơn góp ý của bạn!')


# ADD DATA FEEDBACK TO DB
if form_rating_usefull and form_rating_userfriendly and submit_button:
       doc_ref = db.collection('feedback').document(form_id)
       doc_ref.set({
              'feedback_id': form_id,
              'form_date': form_date,
              'email': form_email,
              'name': form_name,
              'rating_usefull': form_rating_usefull,
              'rating_userfriendly': form_rating_userfriendly,
              'additional_info': form_feedback
       })




# yayyyyyyyyyyyyyyy, bây giờ cần làm page layout, session state, rà luồng, rà logic dữ liệu, rà bug

# st.cache_data, decorator
# index language: vn, en


# UNIT TEST:  
# check xem các khoa khác thì học phần tốt nghiệp có phải là Nhóm tự chọn bằng 9
# RÀ SOÁT LẠI CÁC TRƯỜNG BỊ THAY ĐỔI: Không tín vào Điểm TB tích lũy, gpa_bysemester
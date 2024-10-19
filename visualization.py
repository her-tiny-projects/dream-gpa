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



title_font_size = 18

# empty_table = pd.DataFrame(columns=['temp'], index=[''])
# empty_table.drop(empty_table.index, inplace=True)

# # initiate shared variables:
# if 'grade_master_data' not in st.session_state:
#        st.session_state.grade_master_data = empty_table
# if 'syllabus_master_data' not in st.session_state:
#        st.session_state.syllabus_master_data = empty_table



# 4. VISUALIZATION
if st.session_state.grade_master_data.empty == False:
       grade_master_data = st.session_state.grade_master_data
       grade_master_data['term_order'] = grade_master_data['Số tín chỉ tích lũy'].rank(method='dense').astype(int)

       current_max_credit = grade_master_data['Số tín chỉ tích lũy'].max() # current credits accumulated
       row_current_max_credit = grade_master_data.loc[grade_master_data['Số tín chỉ tích lũy']==current_max_credit]

       current_gpa4 = row_current_max_credit['Điểm trung bình tích lũy hệ 4'].unique()[0]
       current_gpa4 = float('{:.2f}'.format(current_gpa4))

       current_gpa10 = row_current_max_credit['Điểm trung bình tích lũy hệ 10'].unique()[0]
       current_gpa10 = float('{:.2f}'.format(current_gpa10))


       visual_usecols = ['Học kỳ đăng ký học', 'Tên môn học', 'Điểm trung bình học kỳ hệ 4', 'Điểm trung bình tích lũy hệ 4', 'Điểm trung bình học kỳ hệ 10', 'Điểm trung bình tích lũy hệ 10', 'Số tín chỉ đạt học kỳ', 'Số tín chỉ tích lũy', 'Số tín chỉ', 'Điểm TK (C)', 'term_order'] # BIGNOTE: 'Không tín vào Điểm trung bình tích lũy'
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
              gpa_bysemester = gpa_bysemester.sort_values(by='term_order', ascending=True)
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
                            "Số tín chỉ tích lũy" AS "Số tín chỉ tích lũy lũy kế",
                            term_order
                     FROM gpa_bysemester),

              registered_credit AS
                     (SELECT
                            "Học kỳ đăng ký học",
                            SUM("Số tín chỉ") AS "Số tín chỉ đăng ký trong kỳ"
                     FROM gpa_bysemester
                     GROUP BY "Học kỳ đăng ký học")

              SELECT 
                     "Học kỳ đăng ký học",
                     "Số tín chỉ đăng ký trong kỳ",
                     "Số tín chỉ tích lũy trong kỳ",
                     "Số tín chỉ tích lũy lũy kế",
                     SUM("Số tín chỉ đăng ký trong kỳ") OVER (ORDER BY term_order ASC) AS "Số tín chỉ đăng ký lũy kế"
              FROM registered_credit
              LEFT JOIN eligible_credit USING ("Học kỳ đăng ký học")
              ORDER BY term_order
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
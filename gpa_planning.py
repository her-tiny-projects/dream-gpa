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



empty_table = pd.DataFrame(columns=['temp'], index=[''])
empty_table.drop(empty_table.index, inplace=True)


if 'grade_master_data' not in st.session_state:
       st.session_state.grade_master_data = empty_table
if 'syllabus_master_data' not in st.session_state:
       st.session_state.syllabus_master_data = empty_table
if 'subject_registered' not in st.session_state:
       st.session_state.subject_registered = empty_table
if 'current_max_credit' not in st.session_state:
       st.session_state.current_max_credit = 0

# 4 CRITERIA:
       # all subject
       # max credits
       # tolearn/ relearn subject
       # credits remaining

if st.session_state.grade_master_data.empty == False and st.session_state.syllabus_master_data.empty == False:
       # max grade per subject
       grade_master_data = st.session_state.grade_master_data
       syllabus_master_data = st.session_state.syllabus_master_data
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
       input1, input2 = st.columns((2, 1))
       with input1:
              cols = st.columns((3,1))
              with cols[0]:
                     st.markdown('#### :small_orange_diamond: Nhập GPA mục tiêu (thang 4)')
                     target_gpa_input = st.number_input('*GPA mục tiêu không tính quốc phòng, thể chất*', min_value=0.00, max_value=4.00, value=None)
                     st.write('Bạn đã nhập GPA mục tiêu là:', target_gpa_input)


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
       if target_gpa_input:
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
                            st.write(f'*Đã chọn: :red[**{int(mandatory_credit_registered1)}**] tín chỉ*')


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
                            st.write(f'*Đã chọn: :red[**{int(mandatory_credit_registered2)}**] tín chỉ*')


       # 2. THESIS       
       if target_gpa_input:
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
                     thesis_learned = thesis_subject[thesis_subject['Đã học']==1]['Số tín chỉ'].sum()
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
                            thesis_subject = thesis_subject[thesis_subject['Đã học'] != 1]
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
       if target_gpa_input:
              q = """
                     SELECT 
                            *
                     FROM syllabus_grade_master_data
                     WHERE "Môn bắt buộc" IS NULL
                     AND "Nhóm" != 9
              """
              elective_subject = duckdb.sql(q).df()

       #note: elective bị dồn về nhóm 2 thì sao???? --> kệ, người dùng phải tự sắp xếp
              q = """
                     SELECT
                            *,
                            SUM("Số tín chỉ") OVER (ORDER BY "Học kỳ đăng ký học") AS "Tín chỉ tự chọn tích lũy"
                     FROM elective_subject
                     WHERE "Đã học" IS NOT NULL
              """
              accumulated_elective_subject = duckdb.sql(q).df()

              # accumulated_elective_credit = accumulated_elective_subject["Tín chỉ tự chọn tích lũy"].max()
              # elective_credit_tolearn = max(0, max_elective_credit - accumulated_elective_credit) # number of elective credits available to learn/ relearn to maximize grade

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
                     ORDER BY "Học kỳ đăng ký học"
              """
              elective_subject_relearn = duckdb.sql(q).df()
              elective_credit_relearn = elective_subject_relearn['Số tín chỉ'].sum()
              # D --> relearn; F --> relearn or replaced by another elective subject
              # ==> overall,  have to relearn both D, F to improve GPA

              # elective_credit_remaining = elective_credit_tolearn + elective_credit_relearn

              with elective1:
                     st.info('###### Học phần Tự chọn')
                     st.markdown(f':small_orange_diamond: Môn tự chọn có thể học')
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
                            st.write(f'*Đã chọn: :red[**{int(elective_credit_registered1)}**] tín chỉ*')


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
                            st.write(f'*Đã chọn: :red[**{int(elective_credit_registered2)}**] tín chỉ*')

              total_credit_registered = mandatory_credit_registered1 + mandatory_credit_registered2 + thesis_credit_registered + elective_credit_registered1 + elective_credit_registered2

       with input2:
              current_max_credit = round(st.session_state.current_max_credit)
              try:
                     content = f"""
                            ---
                            **TỔNG SỐ TÍN CHỈ:** :red[**{current_max_credit
                            +total_credit_registered}**]
                            - Số tín chỉ đã chọn: :red[**{total_credit_registered}**]
                            - Số tín chỉ đã tích lũy: :red[**{current_max_credit}**]
                            ---
                            """
                     st.markdown(content)
              except:
                     content = f"""
                            ---
                            **TỔNG SỐ TÍN CHỈ:** :red[**{current_max_credit}**]
                            - Số tín chỉ đã chọn: :red[**-/-**]
                            - Số tín chỉ đã tích lũy: :red[**{current_max_credit}**]
                            ---
                            """
                     st.markdown(content)
              #note: remind người dùng xem Tổng số tín chỉ dự kiến tích lũy ở đây có vượt quá số tín chỉ của chương trình học không

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
       if target_gpa_input == None or int(thesis_credit_registered) > int(thesis_credit_remaining) or int(elective_credit_registered2) > int(elective_credit_relearn) or total_credit_registered==0:
              content = """
                     Để phần Kế hoạch học tập dưới đây hiện ra, bạn cần hoàn thiện Mục 1. Thử kiểm tra xem:
                     - Đã điền đúng Số tín chỉ chương trình học của bạn chưa
                     - Đã điền đúng GPA mục tiêu chưa
                     - Số tín chỉ Tick chọn cho mỗi loại học phần có vượt quá số lượng cho phép 
                     """
              scenario.warning(content)
       else:
              temp = st.columns(7)
              temp[3].button('CLICK TO CHECK', key='check_gpa')
              if st.session_state.check_gpa==True:
                     content = f"""
                            Bạn dự kiến đăng ký học :red[**{total_credit_registered} tín chỉ**]. Dưới đây là các kịch bản để đạt :red[**TỐI THIỂU GPA = {target_gpa_input}**]:
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
                                                 if target_gpa_calculate >= target_gpa_input and x in sum_sublist and y in sum_sublist and z in sum_sublist:
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

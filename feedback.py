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
# from dotenv import load_dotenv
# import os



# CONNECT WITH FIREBASE DB
# key_dict = json.loads(st.secrets['credentials']) # streamlit load key.toml --> toml strings = json strings --> json.loads (to load json strings)
# creds = service_account.Credentials.from_service_account_info(key_dict)
# db = firestore.Client(credentials=creds)


# load_dotenv()
# key_dict = json.loads(os.getenv('credentials')) 

db_key = open('db_key.json')
key_dict = json.load(db_key)
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)


# 6. FEEDBACK FORM:
blank1, form, blank2 = st.columns((1,3,1))
with form:
       with st.form(key='feedback_form', clear_on_submit=True):
              st.markdown('# :envelope: GÓC GÓP Ý')
              form_id = str(round(time.time()))
              form_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
              form_rating_usefull = st.slider(label='Mức độ hữu ích:red[*]', min_value=0, max_value=5, help='Có phục vụ bạn trong việc theo dõi kết quả và lên kế hoạch học tập không (Điểm từ 1-5):\n\n1 - Không hữu ích\n\n2 - Có một chút hữu ích\n\n3 - Khá hữu ích\n\n4 - Hữu ích\n\n5 - Rất hữu ích')
              form_rating_userfriendly = st.slider(label='Mức độ dễ sử dụng:red[*]', min_value=0, 
              max_value=5, step=1, help='Bạn có thấy công cụ dễ sử dụng, thao tác không (Điểm từ 1-5):\n\n1 - Rất khó sử dụng\n\n2 - Khó sử dụng\n\n3 - Trung bình\n\n4 - Dễ sử dụng\n\n5 - Rất dễ sử dụng')
              form_feedback = st.text_area(label='Cho mình xin thêm ý kiến về công cụ này nha', help='Bạn có thể gửi bất cứ nhắn gì cho mình qua feedback form này nha. Một số gợi ý:\n\n- Bạn có thể chia sẻ cảm nhận khi sử dụng\n\n- Bạn muốn mình thêm tính năng gì để phục vụ học tập\n\n- Bạn thấy có chỗ nào bị lỗi, khó hiểu hoặc chưa giải thích rõ không,...\n\nMình cảm ơn ý kiến đóng góp của bạn :>')
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

import streamlit as st
from google.oauth2 import service_account
from google.cloud import firestore
import json
import time
from datetime import datetime
import pytz


# CONNECT WITH FIREBASE DB
# key_dict = json.loads(st.secrets['credentials']) # streamlit load key.toml --> toml strings = json strings --> json.loads (to load json strings)
# creds = service_account.Credentials.from_service_account_info(key_dict)
# db = firestore.Client(credentials=creds)


db_key = open('db_key.json')
key_dict = json.load(db_key)
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)



if 'english_mode' not in st.session_state:
    st.session_state.english_mode = 0

english_mode = st.session_state.english_mode

# 1. language mode
language_index = {'form_name': ['## :envelope: BÁO LỖI', '## :envelope: BUG REPORT'],
                   'notification': ['Có gì đó không ổn khi upload dữ liệu, bạn điền vào mẫu Báo lỗi dưới đây để mình biết nhé. Cảm ơn bạn!', 'You seem encounter an issue. Please provide details in the form below.'],
                   'email': ['Email của bạn:', 'Your email:'],
                   'description': ['Mô tả vấn đề bạn gặp phải:(*)', 'Describe your issue(s):(*)'],
                   'button': ['Gửi', 'Submit'],
                   'submit_success': ['Báo lỗi thành công. Vui lòng thử lại sau.', 'Successfully submitted. Please try again later.'],
                   'submit_fail': ['Vui lòng mô tả vấn đề trước khi ấn :red[Gửi]!', 'Please describe your issue(s) before hitting :red[Submit] button']}

# REPORT FORM
cols = st.columns((1,3,1))
with cols[1]:
    with st.form('bug_report_form', clear_on_submit=True):
            st.info(language_index['notification'][english_mode])
            st.markdown(language_index['form_name'][english_mode])
            form_id = str(round(time.time()))
            form_date = datetime.now(pytz.timezone('Asia/Saigon')).strftime('%Y-%m-%d %H:%M:%S')
            report_email = st.text_input(language_index['email'][english_mode])
            report_content = st.text_area(language_index['description'][english_mode])
            sub_cols = st.columns(3)
            submit = sub_cols[1].form_submit_button(language_index['button'][english_mode], use_container_width=True)
            if submit:
                if report_content:
                    st.success(language_index['submit_success'][english_mode])
                else:
                    st.error(language_index['submit_fail'][english_mode])


# ADD REPORT CONTENT TO DB
if report_content and submit:
       doc_ref = db.collection('bug_report').document(form_id)
       doc_ref.set({
              'report_id': form_id,
              'report_date': form_date,
              'report_email': report_email,
              'report_content': report_content
       })
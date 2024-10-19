import streamlit as st

# 1. HDSD & CONTACT

if 'english_mode' not in st.session_state:
    st.session_state.english_mode = 0

english_mode = st.session_state.english_mode

title_vn = """### :raised_hand_with_fingers_splayed: Chào bạn mình là Hoàng Yến:)"""
title_en = """### :raised_hand_with_fingers_splayed: Hello, I'm Hoàng Yến:)"""
intro_vn = """
       :red[**Dream GPA**] là một dự án cá nhân nhỏ xinh của mình hỗ trợ việc lên kế hoạch học tập cho sinh viên FTU hiệu quả hơn. Dù bạn đang nhắm tới GPA cao để đạt học bổng, đạt bằng giỏi/ xuất sắc hay đang cần cân bằng việc học với các hoạt động khác như làm thêm, tham gia CLB hoặc chỉ đơn giản là đang tìm cách đạt được điểm số mong muốn thì công cụ này đều phù hợp.\n
       Công cụ này có thể giúp bạn:
       - Đưa ra các kịch bản về mốc điểm A, B, C để đạt được GPA mục tiêu, từ đó lựa chọn kịch bản phù hợp với tình hình của bản thân
       - Tính toán GPA tối đa mà bạn đạt được với kết quả học tập hiện tại
       - Nhìn lại quá trình học tập một cách trực quan\n
       
       Video hướng dẫn sử dụng :arrow_down::
       """
intro_en = """
       :red[**Dream GPA**] is my tiny project to assist FTU students with planning their studies more effectively. Whether you are aiming for a high GPA to achieve scholarship/ graduate with hornors or struggling to balance multiple activities like study, part-time job, club or you are just wondering how to attain your desired GPA, this tool is for you.\n

       This mini tool can help you:
       - Map out different paths to your dream GPA
       - See how far you can go with your current grades
       - Keep track of your learning progress\n

       Tutorial video :arrow_down::
       """

connect_vn = '### KẾT NỐI VỚI MÌNH:'
connect_en = '### CONNECT WITH ME:'

skype_link = 'https://join.skype.com/invite/x7OxEPJyQ4tb'
github_link = 'https://github.com/her-tiny-projects'
contact1_vn = ':speech_balloon: Liên hệ với mình qua Skype [tại đây](%s)'%skype_link
contact1_en = ':speech_balloon: Start a Skype conversation [here](%s)'%skype_link
contact2_vn = ':link: Xem thêm dự án của mình trên GitHub [tại đây](%s)'%github_link
contact2_en = ':link: Explore my projects on GitHub [here](%s)'%github_link
contact_vn = f"""
       {contact1_vn}\n
       {contact2_vn}\n
       ---
       """
contact_en = f"""
       {contact1_en}\n
       {contact2_en}\n
       ---
       """

notice_vn = '### NHẮN NHỦ:'
notice_en = '### NOTICE:'

notice_content_vn = """
       - Dự án chỉ phục vụ mục đích học tập, không thu phí và không thu thập bất cứ dữ liệu điểm, chương trình đào tạo của người dùng
       - Trang web có link ...... và có video hướng dẫn, kiểm tra tính chính xác của đường link trước khi truy cập
       """

notice_content_en = """
       - This project is solely for educational purposes. No fee. No user data collection regarding users' grades or academic programs  
       - Link to access this website: ........................ Please double-check the link before uploading any files.
       """


language_index = {'title': [title_vn, title_en],
                  'intro': [intro_vn, intro_en],
                  'connect': [connect_vn, connect_en],
                  'contact': [contact_vn, contact_en],
                  'notice': [notice_vn, notice_en],
                  'notice_content': [notice_content_vn, notice_content_en]
                     }

st.markdown(language_index['title'][english_mode])
st.markdown(language_index['intro'][english_mode])


video = st.columns((1,2,1))
# link_youtube = '' 
# video[1].video(link_youtube)


st.markdown(language_index['connect'][english_mode])
st.markdown(language_index['contact'][english_mode])

st.markdown(language_index['notice'][english_mode])
st.warning(language_index['notice_content'][english_mode])
# st.logo
# ----------------------------------------------------------------------
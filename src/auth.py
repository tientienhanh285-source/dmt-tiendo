import streamlit as st
import db_handler

def check_login():
    """Simple mockup of a login system using session state"""
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        st.title("Đăng nhập Hệ thống KPI")
        username = st.text_input("Tên đăng nhập")
        if st.button("Đăng nhập"):
            user = db_handler.get_user_by_username(username.lower().replace(" ", ""))
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Không tìm thấy tài khoản trong hệ thống!")
        return False
    return True

def logout():
    st.session_state.user = None
    st.rerun()

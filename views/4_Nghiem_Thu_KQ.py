import streamlit as st
import runpy
import os

# Tích hợp trực tiếp màn hình Nghiệm thu & Duyệt khách quan
target_path = os.path.join(os.path.dirname(__file__), '4_Nghiem_Thu.py')
if os.path.exists(target_path):
    runpy.run_path(target_path, run_name='__main__')

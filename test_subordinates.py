import sys
import unittest
from unittest.mock import MagicMock
import pandas as pd

# Mock streamlit
mock_st = MagicMock()
mock_st.session_state = {}
mock_st.secrets = {"connections": {"gsheets": True}}
sys.modules['streamlit'] = mock_st

class TestEmployeeViews(unittest.TestCase):
    def setUp(self):
        # Reset session state before each test
        mock_st.session_state.clear()
        mock_st.session_state.is_personal_authenticated = False
        mock_st.session_state.is_manager_authenticated = False
        mock_st.session_state.role_mode = "Cá nhân"
        mock_st.session_state.selected_company = "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"
        
    def test_nguyen_tran_thuc_login(self):
        # Nguyễn Trần Thức (KHĐT - Subordinate of Trần Quốc Thể)
        mock_st.session_state.is_manager_authenticated = True
        mock_st.session_state.manager_dept = "KHĐT"
        mock_st.session_state.manager_user = "Nguyễn Trần Thức"
        mock_st.session_state.role_mode = "Quản lý"
        
        try:
            import views.1_Tong_Quan as tong_quan
            # Just importing should execute the code since streamlit apps are script-based
            # If it doesn't crash, it's a pass for the basic rendering path
            print("Successfully loaded 1_Tong_Quan for Nguyễn Trần Thức")
        except Exception as e:
            self.fail(f"1_Tong_Quan failed for Nguyễn Trần Thức: {e}")
            
    def test_dong_thi_nguyet_nga_login(self):
        # Đồng Thị Nguyệt Nga (TCKT - Subordinate of Đoàn Thị Ngọc Nữ)
        mock_st.session_state.is_manager_authenticated = True
        mock_st.session_state.manager_dept = "TCKT"
        mock_st.session_state.manager_user = "Đồng Thị Nguyệt Nga"
        mock_st.session_state.role_mode = "Quản lý"
        
        try:
            import views.2_Tien_Do as tien_do
            print("Successfully loaded 2_Tien_Do for Đồng Thị Nguyệt Nga")
        except Exception as e:
            self.fail(f"2_Tien_Do failed for Đồng Thị Nguyệt Nga: {e}")

    def test_dang_cong_nhut_login(self):
        # Đặng Công Nhựt (ĐBGT - Subordinate of Nguyễn Ngọc Tôn)
        mock_st.session_state.is_manager_authenticated = True
        mock_st.session_state.manager_dept = "ĐBGT"
        mock_st.session_state.manager_user = "Đặng Công Nhựt"
        mock_st.session_state.role_mode = "Quản lý"
        
        try:
            import views.3_Cap_Nhat as cap_nhat
            print("Successfully loaded 3_Cap_Nhat for Đặng Công Nhựt")
        except Exception as e:
            self.fail(f"3_Cap_Nhat failed for Đặng Công Nhựt: {e}")
            
    def test_tran_quoc_the_bld_login(self):
        # Trần Quốc Thể as BLĐ
        mock_st.session_state.is_manager_authenticated = True
        mock_st.session_state.manager_dept = "BLĐ"
        mock_st.session_state.manager_user = "Trần Quốc Thể"
        mock_st.session_state.role_mode = "Quản lý"
        
        try:
            import views.5_Danh_Gia_KPI as kpi
            print("Successfully loaded 5_Danh_Gia_KPI for Trần Quốc Thể (BLĐ)")
        except Exception as e:
            self.fail(f"5_Danh_Gia_KPI failed for Trần Quốc Thể: {e}")

if __name__ == '__main__':
    unittest.main()

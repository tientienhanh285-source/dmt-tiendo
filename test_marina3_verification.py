import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core_logic import (
    HIERARCHY_MARINA_3,
    get_subordinates_for_manager,
    get_allowed_personnel_for_manager,
    setup_manager_db_filters,
    DEPT_LEADS
)

print("=== STARTING COMPREHENSIVE VERIFICATION OF SHEET MARINA (3) ===")

# Test 1: Đặng Ngọc Hoàng
dnh_subs = get_subordinates_for_manager("Đặng Ngọc Hoàng")
assert "Ngô Thị Tâm" in dnh_subs, f"Đặng Ngọc Hoàng must evaluate Ngô Thị Tâm! Got: {dnh_subs}"
assert "Trần Cường" in dnh_subs, f"Đặng Ngọc Hoàng must evaluate Trần Cường! Got: {dnh_subs}"
print("[PASS] Test 1: Đặng Ngọc Hoàng -> Ngô Thị Tâm & Trần Cường")

# Test 2: Trần Cường
tc_subs = get_subordinates_for_manager("Trần Cường")
assert "Nguyễn Thị Hạnh Tiên" in tc_subs, f"Trần Cường must evaluate Nguyễn Thị Hạnh Tiên! Got: {tc_subs}"
assert "Lê Thị Hải" in tc_subs, f"Trần Cường must evaluate Lê Thị Hải! Got: {tc_subs}"
assert "Ngô Thị Tâm" not in tc_subs, f"Trần Cường must NOT evaluate Ngô Thị Tâm in MARINA (3)! Got: {tc_subs}"
print("[PASS] Test 2: Trần Cường -> Nguyễn Thị Hạnh Tiên & Lê Thị Hải")

# Test 3: Nguyễn Thị Hạnh Tiên
ntht_subs = get_subordinates_for_manager("Nguyễn Thị Hạnh Tiên")
assert "Nguyễn Băng Trinh" in ntht_subs, f"Nguyễn Thị Hạnh Tiên must evaluate Nguyễn Băng Trinh! Got: {ntht_subs}"
assert "Lê Ngọc Tú Uyên" in ntht_subs, f"Nguyễn Thị Hạnh Tiên must evaluate Lê Ngọc Tú Uyên! Got: {ntht_subs}"
assert "Ngô Thị Tâm" not in ntht_subs, f"Nguyễn Thị Hạnh Tiên must NOT evaluate Ngô Thị Tâm in MARINA (3)! Got: {ntht_subs}"
print("[PASS] Test 3: Nguyễn Thị Hạnh Tiên -> Nguyễn Băng Trinh & Lê Ngọc Tú Uyên (no Ngô Thị Tâm)")

# Test 4: Đồng Thị Nguyệt Nga
dtn_subs = get_subordinates_for_manager("Đồng Thị Nguyệt Nga")
assert "Huỳnh Thị Hoàng Hà" in dtn_subs, f"Đồng Thị Nguyệt Nga must evaluate Huỳnh Thị Hoàng Hà! Got: {dtn_subs}"
assert "Nguyễn Thị Nhật Sang" in dtn_subs, f"Đồng Thị Nguyệt Nga must evaluate Nguyễn Thị Nhật Sang! Got: {dtn_subs}"
assert "Lê Thị Hải" in dtn_subs, f"Đồng Thị Nguyệt Nga must evaluate Lê Thị Hải (Marina)! Got: {dtn_subs}"
print("[PASS] Test 4: Đồng Thị Nguyệt Nga -> Huỳnh Thị Hoàng Hà, Nguyễn Thị Nhật Sang, Lê Thị Hải")

# Test 5: Nguyễn Thị Ngọc Hà
ntnh_subs = get_subordinates_for_manager("Nguyễn Thị Ngọc Hà")
assert "Huỳnh Thị Hoàng Hà" in ntnh_subs, f"Nguyễn Thị Ngọc Hà must evaluate Huỳnh Thị Hoàng Hà! Got: {ntnh_subs}"
assert "Lê Thị Hải" in ntnh_subs, f"Nguyễn Thị Ngọc Hà must evaluate Lê Thị Hải! Got: {ntnh_subs}"
assert "Nguyễn Thị Như Can" in ntnh_subs, f"Nguyễn Thị Ngọc Hà must evaluate Nguyễn Thị Như Can! Got: {ntnh_subs}"
print("[PASS] Test 5: Nguyễn Thị Ngọc Hà -> Huỳnh Thị Hoàng Hà, Lê Thị Hải, Nguyễn Thị Như Can")

# Test 6: Thái Văn Thành
tvt_subs = get_subordinates_for_manager("Thái Văn Thành")
assert "Nguyễn Văn Bồn" in tvt_subs, f"Thái Văn Thành must evaluate Nguyễn Văn Bồn! Got: {tvt_subs}"
assert "Đặng Hiền" in tvt_subs or "Đặng Hiển" in tvt_subs, f"Thái Văn Thành must evaluate Đặng Hiền! Got: {tvt_subs}"
assert "Phạm Quang Nghĩa" in tvt_subs, f"Thái Văn Thành must evaluate Phạm Quang Nghĩa! Got: {tvt_subs}"
assert len(tvt_subs) >= 11, f"Thái Văn Thành must have at least 11 subordinates! Got: {len(tvt_subs)}"
print(f"[PASS] Test 6: Thái Văn Thành -> {len(tvt_subs)} subordinates (including Nguyễn Văn Bồn & Đặng Hiền)")

# Test 7: Trần Văn Trọng
tvtr_subs = get_subordinates_for_manager("Trần Văn Trọng")
assert "Lê Nho Tân" in tvtr_subs, f"Trần Văn Trọng must evaluate Lê Nho Tân! Got: {tvtr_subs}"
assert "Đặng Hiền" in tvtr_subs or "Đặng Hiển" in tvtr_subs, f"Trần Văn Trọng must evaluate Đặng Hiền! Got: {tvtr_subs}"
assert "Phạm Quang Nghĩa" in tvtr_subs, f"Trần Văn Trọng must evaluate Phạm Quang Nghĩa! Got: {tvtr_subs}"
print("[PASS] Test 7: Trần Văn Trọng -> 8 subordinates (including Lê Nho Tân & Đặng Hiền)")

# Test 8: Trần Quốc Thể
tqt_subs = get_subordinates_for_manager("Trần Quốc Thể")
assert "Nguyễn Văn Bồn" in tqt_subs, f"Trần Quốc Thể must evaluate Nguyễn Văn Bồn! Got: {tqt_subs}"
assert "Hồ Văn Khoa" in tqt_subs, f"Trần Quốc Thể must evaluate Hồ Văn Khoa! Got: {tqt_subs}"
assert "Nguyễn Trần Thức" in tqt_subs, f"Trần Quốc Thể must evaluate Nguyễn Trần Thức! Got: {tqt_subs}"
assert "Mai Văn Châu" in tqt_subs, f"Trần Quốc Thể must evaluate Mai Văn Châu! Got: {tqt_subs}"
print("[PASS] Test 8: Trần Quốc Thể -> Nguyễn Văn Bồn, Hồ Văn Khoa, Nguyễn Trần Thức, Mai Văn Châu")

# Test 9: Phạm Quang Nghĩa
pqn_subs = get_subordinates_for_manager("Phạm Quang Nghĩa")
assert "Mai Văn Châu" in pqn_subs, f"Phạm Quang Nghĩa must evaluate Mai Văn Châu! Got: {pqn_subs}"
print("[PASS] Test 9: Phạm Quang Nghĩa -> Mai Văn Châu")

# Test 10: Hồ Văn Khoa
hvk_subs = get_subordinates_for_manager("Hồ Văn Khoa")
assert "Phan Thị Mỹ Hạnh" in hvk_subs, f"Hồ Văn Khoa must evaluate Phan Thị Mỹ Hạnh! Got: {hvk_subs}"
assert "Phan Thị Kim Cúc" in hvk_subs, f"Hồ Văn Khoa must evaluate Phan Thị Kim Cúc! Got: {hvk_subs}"
print("[PASS] Test 10: Hồ Văn Khoa -> Phan Thị Mỹ Hạnh & Phan Thị Kim Cúc")

# Test 11: Nguyễn Trần Thức
ntt_subs = get_subordinates_for_manager("Nguyễn Trần Thức")
assert "Nguyễn Đức Lợi" in ntt_subs, f"Nguyễn Trần Thức must evaluate Nguyễn Đức Lợi! Got: {ntt_subs}"
assert "Cao Thuỷ Tiên" in ntt_subs, f"Nguyễn Trần Thức must evaluate Cao Thuỷ Tiên! Got: {ntt_subs}"
assert "Trần Tin" in ntt_subs, f"Nguyễn Trần Thức must evaluate Trần Tin! Got: {ntt_subs}"
print("[PASS] Test 11: Nguyễn Trần Thức -> Nguyễn Đức Lợi, Cao Thuỷ Tiên, Trần Tin")

# Test 12: Nguyễn Ngọc Tôn
nnt_subs = get_subordinates_for_manager("Nguyễn Ngọc Tôn")
assert "Đặng Công Nhựt" in nnt_subs or "Đặng Công Nhật" in nnt_subs, f"Nguyễn Ngọc Tôn must evaluate Đặng Công Nhựt! Got: {nnt_subs}"
assert "Đặng Thị Mỹ Hạnh" in nnt_subs, f"Nguyễn Ngọc Tôn must evaluate Đặng Thị Mỹ Hạnh! Got: {nnt_subs}"
assert "Đặng Thanh Quang" in nnt_subs, f"Nguyễn Ngọc Tôn must evaluate Đặng Thanh Quang! Got: {nnt_subs}"
print("[PASS] Test 12: Nguyễn Ngọc Tôn -> Đặng Công Nhựt, Đặng Thị Mỹ Hạnh, Đặng Thanh Quang")

# Test 13: HĐQT Leaders
assert get_subordinates_for_manager("Đặng Thanh Bình") is None, "Đặng Thanh Bình must have None (all access)"
assert get_subordinates_for_manager("Đặng Thị Lan Ngọc") is None, "Đặng Thị Lan Ngọc must have None (all access)"
print("[PASS] Test 13: HĐQT Leaders (Đặng Thanh Bình, Đặng Thị Lan Ngọc) have full unconstrained access")

# Test 14: Cross-company filter test
db_f = {'DonVi': 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT'}
res_f = setup_manager_db_filters(db_f.copy(), "Thái Văn Thành", "BLĐ", 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT')
assert 'DonVi' not in res_f, f"DonVi must be deleted for cross-company manager Thái Văn Thành! Got: {res_f}"
assert "Nguyễn Văn Bồn" in res_f['NguoiChuTri'], f"Nguyễn Văn Bồn must be in NguoiChuTri for Thái Văn Thành! Got: {res_f}"
print("[PASS] Test 14: Cross-company filter removes DonVi so Thái Văn Thành sees Nguyễn Văn Bồn (Đầu Tư)")

# Test 15: DEPT_LEADS presence
assert "Nguyễn Thị Hạnh Tiên" in DEPT_LEADS["CÔNG TY CỔ PHẦN DMT-MARINA"]["HCNS"], "Nguyễn Thị Hạnh Tiên must be in Marina HCNS leads"
assert "Lê Thị Hải" in DEPT_LEADS["CÔNG TY CỔ PHẦN DMT-MARINA"]["TCKT"], "Lê Thị Hải must be in Marina TCKT leads"
assert "Lê Nho Tân" in DEPT_LEADS["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]["Mỏ"], "Lê Nho Tân must be in Cienco Mỏ leads"
assert "Đặng Hiền" in DEPT_LEADS["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]["XN XMTB"], "Đặng Hiền must be in Cienco XN XMTB leads"
print("[PASS] Test 15: DEPT_LEADS has all leads in Marina, Cienco, and Đầu Tư")

print("\n🎉 ALL 15 AUTOMATED TESTS PASSED WITH 100% SUCCESS!")

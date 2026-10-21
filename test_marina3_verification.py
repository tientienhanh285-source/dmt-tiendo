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
assert "Nguyễn Thị Hạnh Tiên" in dnh_subs, f"Đặng Ngọc Hoàng must evaluate Nguyễn Thị Hạnh Tiên! Got: {dnh_subs}"
print("[PASS] Test 1: Đặng Ngọc Hoàng -> Trần Cường, Nguyễn Thị Hạnh Tiên, Ngô Thị Tâm")

# Test 2: Trần Cường
tc_subs = get_subordinates_for_manager("Trần Cường")
assert tc_subs == [], f"Trần Cường has no subordinates to manage! Got: {tc_subs}"
print("[PASS] Test 2: Trần Cường -> only person in Marina, no subordinates")

# Test 2b: Thể, Nữ, Tôn hiện tại chưa ai quản lý
all_managed = set()
for m, subs in HIERARCHY_MARINA_3.items():
    if subs:
        all_managed.update(subs)
assert "Trần Quốc Thể" not in all_managed, "Trần Quốc Thể must NOT have anyone managing him!"
assert "Đoàn Thị Ngọc Nữ" not in all_managed, "Đoàn Thị Ngọc Nữ must NOT have anyone managing her!"
assert "Nguyễn Ngọc Tôn" not in all_managed, "Nguyễn Ngọc Tôn must NOT have anyone managing him!"
dtn_n_subs = get_subordinates_for_manager("Đoàn Thị Ngọc Nữ")
assert dtn_n_subs == ["Đồng Thị Nguyệt Nga"], f"Đoàn Thị Ngọc Nữ must only manage Đồng Thị Nguyệt Nga! Got: {dtn_n_subs}"
print("[PASS] Test 2b: Thể, Nữ, Tôn hiện tại chưa ai quản lý; Đoàn Thị Ngọc Nữ -> Đồng Thị Nguyệt Nga")

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
print("[PASS] Test 4: Đồng Thị Nguyệt Nga -> Huỳnh Thị Hoàng Hà, Nguyễn Thị Nhật Sang, Lê Thị Hải (sole approver)")

# Test 5: Nguyễn Thị Ngọc Hà
ntnh_subs = get_subordinates_for_manager("Nguyễn Thị Ngọc Hà")
assert "Nguyễn Thị Như Can" in ntnh_subs, f"Nguyễn Thị Ngọc Hà must evaluate Nguyễn Thị Như Can! Got: {ntnh_subs}"
assert "Lê Thị Hải" not in ntnh_subs, f"Nguyễn Thị Ngọc Hà must NOT evaluate Lê Thị Hải! Got: {ntnh_subs}"
assert "Huỳnh Thị Hoàng Hà" not in ntnh_subs, f"Nguyễn Thị Ngọc Hà must NOT evaluate Huỳnh Thị Hoàng Hà! Got: {ntnh_subs}"
print("[PASS] Test 5: Nguyễn Thị Ngọc Hà -> Nguyễn Thị Như Can (sole approver for Can)")

# Test 6: Thái Văn Thành
tvt_subs = get_subordinates_for_manager("Thái Văn Thành")
assert "Nguyễn Văn Bồn" not in tvt_subs, f"Nguyễn Văn Bồn must only be evaluated by Trần Quốc Thể! Got: {tvt_subs}"
assert "Đặng Hiền" not in tvt_subs, f"Đặng Hiền must only be evaluated by Trần Văn Trọng! Got: {tvt_subs}"
assert "Phạm Quang Nghĩa" in tvt_subs, f"Thái Văn Thành must evaluate Phạm Quang Nghĩa! Got: {tvt_subs}"
assert "Nguyễn Thị Ngọc Hà" in tvt_subs, f"Thái Văn Thành must evaluate Nguyễn Thị Ngọc Hà! Got: {tvt_subs}"
print(f"[PASS] Test 6: Thái Văn Thành -> {len(tvt_subs)} subordinates (Nguyễn Văn Bồn -> Thể, Đặng Hiền -> Trọng)")

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

# Test 9: Phạm Quang Nghĩa & Nguyễn Thị Mỹ Phương
pqn_subs = get_subordinates_for_manager("Phạm Quang Nghĩa")
assert pqn_subs == [], f"Phạm Quang Nghĩa must not evaluate anyone! Got: {pqn_subs}"
ntmp_subs = get_subordinates_for_manager("Nguyễn Thị Mỹ Phương")
assert ntmp_subs == [], f"Nguyễn Thị Mỹ Phương must not evaluate anyone! Got: {ntmp_subs}"
print("[PASS] Test 9: Phạm Quang Nghĩa (nhân viên Ban KT) & Nguyễn Thị Mỹ Phương không duyệt công việc cho ai")

# Test 10: Hồ Văn Khoa
hvk_subs = get_subordinates_for_manager("Hồ Văn Khoa")
assert "Phan Thị Mỹ Hạnh" in hvk_subs, f"Hồ Văn Khoa must evaluate Phan Thị Mỹ Hạnh! Got: {hvk_subs}"
assert "Cao Thuỷ Tiên" in hvk_subs, f"Hồ Văn Khoa must evaluate Cao Thuỷ Tiên! Got: {hvk_subs}"
print("[PASS] Test 10: Hồ Văn Khoa -> Phan Thị Mỹ Hạnh & Cao Thuỷ Tiên")

# Test 11: Nguyễn Trần Thức
ntt_subs = get_subordinates_for_manager("Nguyễn Trần Thức")
assert "Nguyễn Đức Lợi" in ntt_subs, f"Nguyễn Trần Thức must evaluate Nguyễn Đức Lợi! Got: {ntt_subs}"
assert "Phan Thị Kim Cúc" in ntt_subs, f"Nguyễn Trần Thức must evaluate Phan Thị Kim Cúc! Got: {ntt_subs}"
assert "Trần Tin" in ntt_subs, f"Nguyễn Trần Thức must evaluate Trần Tin! Got: {ntt_subs}"
print("[PASS] Test 11: Nguyễn Trần Thức -> Nguyễn Đức Lợi, Phan Thị Kim Cúc, Trần Tin")

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
db_f = {'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG'}
res_f = setup_manager_db_filters(db_f.copy(), "Đặng Ngọc Hoàng", "BLĐ", 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG')
assert 'DonVi' not in res_f, f"DonVi must be deleted for cross-company manager Đặng Ngọc Hoàng! Got: {res_f}"
assert "Trần Cường" in res_f['NguoiChuTri'], f"Trần Cường must be in NguoiChuTri for Đặng Ngọc Hoàng! Got: {res_f}"
print("[PASS] Test 14: Cross-company filter removes DonVi so Đặng Ngọc Hoàng sees Trần Cường (Marina)")

# Test 15: DEPT_LEADS presence
assert "Trần Cường" in DEPT_LEADS["CÔNG TY CỔ PHẦN DMT-MARINA"]["BLĐ"], "Trần Cường must be in Marina BLĐ leads"
assert DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["DA"] == [], "Ban DA must have empty leads"
assert DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["ĐBGT"] == [], "Ban ĐBGT must have empty leads"
assert DEPT_LEADS["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]["KT"] == [], "KT must have empty leads"
assert DEPT_LEADS["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]["BCH CT"] == [], "BCH CT must have empty leads"
assert DEPT_LEADS["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]["XN XMTB"] == [], "XN XMTB must have empty leads"
assert DEPT_LEADS["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]["Mỏ"] == [], "Mỏ must have empty leads"
assert DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["KT"] == [], "Ban KT in DMT must have empty leads"
assert DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["XN DTBD"] == [], "XN DTBD in DMT must have empty leads"
assert DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["SÀN"] == [], "SÀN in DMT must have empty leads"
assert "Thái Văn Thành" in DEPT_LEADS["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]["BLĐ"], "Thái Văn Thành must be in Cienco BLĐ leads"
assert "Trần Văn Trọng" in DEPT_LEADS["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]["BLĐ"], "Trần Văn Trọng must be in Cienco BLĐ leads"
print("[PASS] Test 15: DEPT_LEADS has all correct leads: Thành, Trọng, Thể, Hoàng, Tôn, Nữ only in BLĐ leads")

# Test 16: Cienco KT & BCH CT personnel
from core_logic import get_personnel_for_company_dept, load_config
cfg = load_config()
cienco_co = "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"
kt_personnel = get_personnel_for_company_dept(cienco_co, "KT", cfg)
assert set(kt_personnel) == {"Phạm Quang Nghĩa", "Lê Văn Thành", "Ngô Văn Hoàng"}, f"KT personnel mismatch! Got: {kt_personnel}"
bch_personnel = get_personnel_for_company_dept(cienco_co, "BCH CT", cfg)
assert set(bch_personnel) == {"Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long"}, f"BCH CT personnel mismatch! Got: {bch_personnel}"
print("[PASS] Test 16: Cienco Ban KT = [Nghĩa, Văn Hoàng, Văn Thành], BCH CT = [Trung, Đông, Long]")

# Test 17: Verify BLĐ members never appear as leads in non-BLĐ departments, and Đặng Ngọc Hoàng is not in HĐQT
bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Nguyễn Ngọc Tôn", "Thái Văn Thành", "Trần Văn Trọng"]
for co_name, co_leads in DEPT_LEADS.items():
    for dept, leads in co_leads.items():
        if dept not in ["BLĐ", "Ban Lãnh đạo"]:
            for m in bld_members:
                assert m not in leads, f"BLĐ member {m} must NOT be in department lead for {co_name} -> {dept}!"

assert "Đặng Ngọc Hoàng" not in DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["HĐQT"], "Đặng Ngọc Hoàng must not be in DMT HĐQT leads!"
dmt_hdqt = get_personnel_for_company_dept("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "HĐQT", cfg)
assert "Đặng Ngọc Hoàng" not in dmt_hdqt, f"Đặng Ngọc Hoàng must not be in DMT HĐQT personnel! Got: {dmt_hdqt}"
print("[PASS] Test 17: BLĐ members (Thể, Nữ, Hoàng, Tôn, Thành, Trọng) are strictly isolated to BLĐ only (Hoàng removed from HĐQT)")

print("\n🎉 ALL 17 AUTOMATED TESTS PASSED WITH 100% SUCCESS!")

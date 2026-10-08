import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import core_logic

def test():
    config = core_logic.load_config()
    core_logic.config = config  # manually override for the test
    
    # Emulate mapping logic at module level:
    for comp_name, comp_data in config.get("companies", {}).items():
        if "departments" in comp_data:
            comp_data["departments"] = [core_logic.DEPT_ABBR.get(d, d) for d in comp_data["departments"]]
        if "personnel_by_department" in comp_data:
            new_personnel = {}
            for d, p in comp_data["personnel_by_department"].items():
                new_personnel[core_logic.DEPT_ABBR.get(d, d)] = p
            comp_data["personnel_by_department"] = new_personnel

    print("--- Sàn GDBĐS ---")
    p1 = core_logic.get_personnel_for_company_dept("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "Sàn GDBĐS", config)
    print(p1)
    
    print("--- XN DTBD ---")
    p2 = core_logic.get_personnel_for_company_dept("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "XN DTBD", config)
    print(p2)
    
if __name__ == "__main__":
    test()

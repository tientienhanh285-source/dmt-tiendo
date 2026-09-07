                    def _get_pb(name):
                        # Try to find from current company's departments
                        if selected_company != "Tất cả đơn vị":
                            depts = get_departments_for_company(selected_company, config)
                            for d in depts:
                                p_list = get_personnel_for_company_dept(selected_company, d, config)
                                if name in p_list: return d
                        # Fallback to global config
                        for d, p_list in config.get("personnel_by_department", {}).items():
                            if name in p_list: return d
                        return "Khác"

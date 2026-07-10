"""字段备选项与固定文案。全部提取自官方 Word 模板（Woodards Gas/Smoke Report PDF 表单域）。"""

GAS_LOCATIONS = ["Bedroom", "Hallway", "Kitchen", "Living room", "Other"]
GAS_APPLIANCE_TYPES = ["Cooktops/hobs", "Duct Heating", "Hot Water Service"]
GAS_MANUFACTURERS = ["ASKO", "Bosch", "Chef", "Delonghi", "Electrolux", "Fisher & Paykel", "GE",
                     "Haier", "ILVE", "LG", "Miele", "Omega", "Samsung", "Smeg", "Westinghouse", "Whirlpool"]
GAS_FLUE_TYPES = ["N/A"]
GAS_INSTALL_OPTIONS = ["Compliant", "Non-Compliant"]
PASS_FAIL_NA = ["Pass", "Fail", "N/A"]
YES_NO_NA = ["Yes", "No", "N/A"]

SMOKE_BRANDS = ["ANKA", "Clipsal", "Ionization", "Legrand", "Lifesaver", "Matelec",
                "Photoelectric", "Quell", "Tesla", "Trafalgar"]

GAS_OVERALL_FINDINGS = [
    {"label": "Compliant / Non-Compliant", "options": ["Compliant", "Non-Compliant"]},
    {"label": "Recommendation", "options": ["N/A", "Yes"]},
    {"label": "Faulty Found", "options": ["N/A", "Yes"]},
    {"label": "Safety Issue", "options": ["N/A", "Yes"]},
    {"label": "Disconnected\n(Urgent Repair)", "options": ["N/A", "Yes"]},
]

GAS_INSTALLATION_ITEMS = [
    {"order": 1, "label": "APPLIANCES TESTED:",
     "description": "Are all appliances certified and installed in accordance with AS/NZS5601?"},
    {"order": 2, "label": "SUPPLY PIPEWORK VISUAL:",
     "description": "Are the appliances and its components accessible for service and adjustment?"},
    {"order": 3, "label": "INSTALLATION PIPEWORK VISUAL:",
     "description": "All pipework and valves fitted as required by AS/NZS5601?"},
    {"order": 4, "label": "GAS LINE TEST:",
     "description": "Is the property gastight in accordance with AS/NZS5601?"},
    {"order": 5, "label": "METER ACCESS:",
     "description": "Did the Gas Meter have acceptable access as per AS/NZS5601?"},
    {"order": 6, "label": "APPLIANCES OPERATION:",
     "description": "Are all appliances operating as per manufacturers operating instructions?"},
    {"order": 7, "label": "APPLIANCE CLEARANCES:",
     "description": "Do all Appliance Clearances comply with AS/NZS5601?"},
    {"order": 8, "label": "DEFECTS FOUND:",
     "description": "Were there any defects found at the property?"},
]

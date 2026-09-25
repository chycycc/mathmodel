# -*- coding: utf-8 -*-
import os

# 1. Patch code/Q1/problem1.py
p1_path = 'code/Q1/problem1.py'
with open(p1_path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'sys.path.insert(0, os.path.dirname(__file__))\nimport data_loader as dl',
    '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\n_WORKSPACE_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))\nsys.path.insert(0, os.path.join(_WORKSPACE_ROOT, "code"))\nimport data_loader as dl'
).replace(
    'sys.path.insert(0, os.path.dirname(__file__))\r\nimport data_loader as dl',
    '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\r\n_WORKSPACE_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))\r\nsys.path.insert(0, os.path.join(_WORKSPACE_ROOT, "code"))\r\nimport data_loader as dl'
)

c = c.replace(
    "os.makedirs('results', exist_ok=True)",
    "out_dir = os.path.join(_WORKSPACE_ROOT, 'results', 'Q1')\n    os.makedirs(out_dir, exist_ok=True)"
).replace(
    "df_final.to_csv('results/Q1_单点组批方案.csv'",
    "df_final.to_csv(os.path.join(out_dir, 'Q1_单点组批方案.csv')"
).replace(
    "sensitivity['summary'].to_csv('results/Q1_敏感性_eta_汇总.csv'",
    "sensitivity['summary'].to_csv(os.path.join(out_dir, 'Q1_敏感性_eta_汇总.csv')"
).replace(
    "sensitivity['payload_table'].to_csv('results/Q1_敏感性_eta_安全载荷.csv'",
    "sensitivity['payload_table'].to_csv(os.path.join(out_dir, 'Q1_敏感性_eta_安全载荷.csv')"
)

with open(p1_path, 'w', encoding='utf-8') as f:
    f.write(c)
print('code/Q1/problem1.py patched successfully')

# 2. Patch code/Q2/problem2.py
p2_path = 'code/Q2/problem2.py'
with open(p2_path, 'r', encoding='utf-8') as f:
    c2 = f.read()

c2 = c2.replace(
    '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\n_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR)',
    '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\n_WORKSPACE_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))'
).replace(
    '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\r\n_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR)',
    '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\r\n_WORKSPACE_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))'
)

c2 = c2.replace(
    "df_trips.to_csv('results/Q2_运输架次.csv'",
    "out_dir = os.path.join(_WORKSPACE_ROOT, 'results', 'Q2')\n    os.makedirs(out_dir, exist_ok=True)\n    df_trips.to_csv(os.path.join(out_dir, 'Q2_运输架次.csv')"
).replace(
    "df_boxes.to_csv('results/Q2_逐箱交付.csv'",
    "df_boxes.to_csv(os.path.join(out_dir, 'Q2_逐箱交付.csv')"
)

with open(p2_path, 'w', encoding='utf-8') as f:
    f.write(c2)
print('code/Q2/problem2.py patched successfully')

# 3. Patch code/export/export_excel.py
pe_path = 'code/export/export_excel.py'
if os.path.exists(pe_path):
    with open(pe_path, 'r', encoding='utf-8') as f:
        ce = f.read()
    ce = ce.replace(
        '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\n_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR)',
        '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\n_WORKSPACE_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))'
    ).replace(
        '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\r\n_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR)',
        '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\r\n_WORKSPACE_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))'
    )
    with open(pe_path, 'w', encoding='utf-8') as f:
        f.write(ce)
    print('code/export/export_excel.py patched successfully')

# 4. Patch code/export/export_q12_submission.py
pq_path = 'code/export/export_q12_submission.py'
if os.path.exists(pq_path):
    with open(pq_path, 'r', encoding='utf-8') as f:
        cq = f.read()
    cq = cq.replace(
        '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\n_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR)',
        '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\n_WORKSPACE_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))'
    ).replace(
        '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\r\n_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR)',
        '_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\r\n_WORKSPACE_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))'
    )
    with open(pq_path, 'w', encoding='utf-8') as f:
        f.write(cq)
    print('code/export/export_q12_submission.py patched successfully')

# -*- coding: utf-8 -*-
import sys, json, os, subprocess
import pandas as pd
import io

sys.stdout.reconfigure(encoding='utf-8')

def get_git_file(branch, path):
    cmd = ['git', 'show', f'{branch}:{path}']
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.stdout.decode('utf-8-sig', errors='replace')

q3_relay_feat = pd.read_csv(io.StringIO(get_git_file('feature/q3-q4-tasks', 'results/Q3/Q3_中继架次.csv')))
q3_sens_feat = pd.read_csv(io.StringIO(get_git_file('feature/q3-q4-tasks', 'results/Q3/Q3_方案对比与敏感性.csv')))
q4_cfg_feat = pd.read_csv(io.StringIO(get_git_file('feature/q3-q4-tasks', 'results/Q4/Q4_分区配置.csv')))
q4_gap_feat = pd.read_csv(io.StringIO(get_git_file('feature/q3-q4-tasks', 'results/Q4/Q4_方案对比与资源缺口.csv')))

print("=== FEATURE/Q3-Q4-TASKS Q3 方案对比 ===")
print(q3_sens_feat.to_string())

print("\n=== FEATURE/Q3-Q4-TASKS Q3 中继架次 ===")
print(q3_relay_feat.to_string())

print("\n=== FEATURE/Q3-Q4-TASKS Q4 分区配置 ===")
print(q4_cfg_feat.to_string())

print("\n=== FEATURE/Q3-Q4-TASKS Q4 资源缺口 ===")
print(q4_gap_feat.to_string())

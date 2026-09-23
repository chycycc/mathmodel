# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd

sys.path.insert(0, 'code')
import data_loader as dl

def run_audit():
    orig_boxes = dl.CARGO_BOXES
    orig_box_ids = set(b['box_id'] for b in orig_boxes)
    assert len(orig_boxes) == 80, f"原始货箱数量异常: {len(orig_boxes)}"
    box_dict = {b['box_id']: b for b in orig_boxes}

    csv_path = 'results/Q1_单点组批方案.csv'
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    assigned_boxes = []
    print("=== 开始逐架次物理约束与守恒校验 ===")
    for idx, row in df.iterrows():
        b_list = [x.strip() for x in str(row['货箱编号列表']).split(',')]
        assigned_boxes.extend(b_list)
        
        # 1. 质量守恒校验
        w_sum = sum(box_dict[bid]['weight'] for bid in b_list)
        assert abs(w_sum - row['总质量（kg）']) < 1e-3, f"架次 {row['架次编号']} 质量不匹配"
        
        # 2. 体积守恒校验
        v_sum = sum(box_dict[bid]['volume'] for bid in b_list)
        assert abs(v_sum - row['总体积（m³）']) < 1e-4, f"架次 {row['架次编号']} 体积不匹配"
        
        # 3. 服务区不跨区校验
        for bid in b_list:
            assert box_dict[bid]['service_id'] == row['服务区编号'], f"货箱 {bid} 发生跨服务区混装"
        
        # 4. 机型容积上限校验
        v_max = dl.DRONE_PARAMS[row['机型编号']]['vol_max']
        assert v_sum <= v_max + 1e-6, f"架次 {row['架次编号']} 容积超限: {v_sum} > {v_max}"
        
        # 5. 返航安全 SOC 校验
        assert row['返航SOC（%）'] >= 20.0 - 1e-4, f"架次 {row['架次编号']} 返航SOC低于20%: {row['返航SOC（%）']}%"
        
        # 6. 单架次耗时与能耗复核
        t_fl, e_calc = dl.compute_leg_flight(row['机型编号'], 'O01', row['服务区编号'], w_sum)
        t_bk, e_bk = dl.compute_leg_flight(row['机型编号'], row['服务区编号'], 'O01', 0.0)
        e_tot_round = e_calc + e_bk
        assert abs(e_tot_round - row['架次能耗（kWh）']) < 1e-3, f"架次 {row['架次编号']} 能耗不吻合"

    # 7. 全网无遗漏、无重复校验
    assert len(assigned_boxes) == 80, f"指派货箱数 {len(assigned_boxes)} != 80"
    assert set(assigned_boxes) == orig_box_ids, "指派货箱集合与 80 个原始货箱不一致"
    assert len(set(assigned_boxes)) == 80, "存在重复指派货箱"

    print("=== 全网物理校验 100% 通过 ===")
    print(f"1. 货箱覆盖率: 80/80 (100.0%)，无重复、无遗漏、无跨区。")
    print(f"2. 架次总数: {len(df)} 架次 (B型: {(df['机型编号']=='B').sum()}, C型: {(df['机型编号']=='C').sum()}, A型: {(df['机型编号']=='A').sum()})")
    print(f"3. 累计总能耗: {df['架次能耗（kWh）'].sum():.4f} kWh")
    print(f"4. 累计作业总耗时: {df['_累计作业时间(s)'].sum():.1f} 秒")
    print(f"5. 返航最低 SOC: {df['返航SOC（%）'].min():.2f}% (架次: {df.loc[df['返航SOC（%）'].idxmin(), '架次编号']}, 服务区: {df.loc[df['返航SOC（%）'].idxmin(), '服务区编号']})")
    print(f"6. 返航最高 SOC: {df['返航SOC（%）'].max():.2f}% (架次: {df.loc[df['返航SOC（%）'].idxmax(), '架次编号']}, 服务区: {df.loc[df['返航SOC（%）'].idxmax(), '服务区编号']})")

if __name__ == '__main__':
    run_audit()

import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

df_q2 = pd.read_csv('results/Q2_运输架次.csv', encoding='utf-8-sig')
df_box = pd.read_csv('results/Q2_逐箱交付.csv', encoding='utf-8-sig')

df_q2['时长(s)'] = df_q2['返回O01时刻（s）'] - df_q2['开始时刻（s）']
df_q2['经停点数'] = df_q2['访问服务区顺序'].apply(lambda x: len([s.strip() for s in x.split('->')]))

print("=== 1. 总体指标 ===")
print(f"总架次数: {len(df_q2)}")
print(f"交付货箱总数: {len(df_box)}")
print(f"任务起始时刻: {df_q2['开始时刻（s）'].min():.1f} s")
print(f"任务结束时刻 (Makespan): {df_q2['返回O01时刻（s）'].max():.1f} s ({df_q2['返回O01时刻（s）'].max() / 3600:.2f} 小时 / {df_q2['返回O01时刻（s）'].max() / 60:.1f} 分钟)")
print(f"最后一箱物资交付完成时刻: {df_box['交付完成时刻（s）'].max():.1f} s ({df_box['交付完成时刻（s）'].max() / 60:.1f} 分钟)")
print(f"总运输能耗: {df_q2['架次能耗（kWh）'].sum():.4f} kWh")
print(f"平均每架次能耗: {df_q2['架次能耗（kWh）'].mean():.4f} kWh (最小: {df_q2['架次能耗（kWh）'].min():.4f}, 最大: {df_q2['架次能耗（kWh）'].max():.4f})")
print(f"平均架次时长: {df_q2['时长(s)'].mean():.1f} s (最小: {df_q2['时长(s)'].min():.1f} s, 最大: {df_q2['时长(s)'].max():.1f} s)")

print("\n=== 2. 机型与无人机使用统计 ===")
print("按机型统计:")
type_stat = df_q2.groupby('机型编号').agg(
    架次数=('架次编号', 'count'),
    使用飞机数=('无人机编号', 'nunique'),
    总能耗=('架次能耗（kWh）', 'sum'),
    平均架次时长=('时长(s)', 'mean'),
    平均架次能耗=('架次能耗（kWh）', 'mean')
)
print(type_stat)

print("\n各无人机执行架次明细:")
drone_stat = df_q2.groupby(['机型编号', '无人机编号']).agg(
    执行架次数=('架次编号', 'count'),
    总飞行时长=('时长(s)', 'sum'),
    总能耗=('架次能耗（kWh）', 'sum'),
    首次起飞=('开始时刻（s）', 'min'),
    末次返航=('返回O01时刻（s）', 'max')
)
print(drone_stat)

print("\n=== 3. 电池使用与周转统计 ===")
bat_stat = df_q2.groupby(['机型编号', '电池编号']).agg(
    循环使用次数=('架次编号', 'count'),
    累计耗电=('架次能耗（kWh）', 'sum'),
    首次使用=('开始时刻（s）', 'min'),
    末次使用返航=('返回O01时刻（s）', 'max')
)
print(bat_stat)

print("\n=== 4. 路径拓扑特征 (单点 vs 多点串联) ===")
print(df_q2['经停点数'].value_counts())

print("\n=== 5. 每架次送达货箱数统计 ===")
box_per_flight = df_box.groupby('架次编号').size().rename('送箱数')
df_q2_merge = df_q2.merge(box_per_flight, on='架次编号', how='left')
print(df_q2_merge[['架次编号', '无人机编号', '机型编号', '访问服务区顺序', '送箱数', '时长(s)', '架次能耗（kWh）']].to_string())

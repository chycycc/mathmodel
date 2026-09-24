# -*- coding: utf-8 -*-
"""问题四：救援任务分区与资源配置，Python标准库实现。"""
import csv, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
Q2=ROOT/'results'/'Q2_运输架次.csv'; Q3=ROOT/'results'/'Q3'/'Q3_中继任务.csv'; OUT=ROOT/'results'/'Q4'
INV={'A':{'u':4,'b':6},'B':{'u':2,'b':4},'C':{'u':2,'b':4},'R':{'u':2,'b':6}}
PARAM={'A':{'e':4.5,'t':1800},'B':{'e':4.0,'t':2400},'C':{'e':8.0,'t':3000}}

def read_csv(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def peak_intervals(rows,start_key,end_key):
    events=[]
    for row in rows:
        events.extend(((float(row[start_key]),1),(float(row[end_key]),-1)))
    events.sort(key=lambda x:(x[0],x[1]))
    cur=peak=0
    for _,delta in events:
        cur+=delta; peak=max(peak,cur)
    return peak

def charge_end(row):
    m=row['机型编号']; soc=1-float(row['架次能耗（kWh）'])/PARAM[m]['e']
    frac=((0.9-soc)/0.9*0.65+0.35) if soc<0.9 else ((1-soc)/0.1*0.35)
    return float(row['返回O01时刻（s）'])+frac*PARAM[m]['t']+1

def group_rows(group,trips):
    out=[]
    for row in trips:
        seq=row['访问服务区顺序'].split(' -> ')
        if seq and all(s in group for s in seq):out.append(row)
    return out

def resources(rows):
    result={'架次':len(rows),'完工时间':max((float(x['返回O01时刻（s）']) for x in rows),default=0.0),
            '能耗':sum(float(x['架次能耗（kWh）']) for x in rows),'按机型':{}}
    for m in ('A','B','C'):
        typed=[x for x in rows if x['机型编号']==m]
        u=peak_intervals(typed,'开始时刻（s）','返回O01时刻（s）') if typed else 0
        battery_events=[]
        for x in typed:battery_events.extend(((float(x['开始时刻（s）']),1),(charge_end(x),-1)))
        battery_events.sort(key=lambda x:(x[0],x[1])); cur=bat=0
        for _,d in battery_events:cur+=d;bat=max(bat,cur)
        result['按机型'][m]={'架次':len(typed),'运输无人机需求':u,'共享电池需求':bat,
            '库存无人机':INV[m]['u'],'库存电池':INV[m]['b'],
            '无人机缺口':max(0,u-INV[m]['u']),'电池缺口':max(0,bat-INV[m]['b'])}
    result['中继无人机需求']=0;result['中继能源组件需求']=0;result['中继无人机缺口']=0;result['中继能源组件缺口']=0
    result['工作量秒']=sum(float(x['返回O01时刻（s）'])-float(x['开始时刻（s）']) for x in rows)
    return result

def main():
    trips=read_csv(Q2); relays=read_csv(Q3)
    big={'S001','S002','S003','S004','S005','S006','S007','S008','S009','S011','S012','S013','S015'}
    schemes={'K2_A':[big,{'S010','S014'}], 'K2_B':[big|{'S010'},{'S014'}], 'K2_C':[big|{'S014'},{'S010'}], 'K3':[big,{'S010'},{'S014'}]}
    summary={}; rows=[]
    for name,groups in schemes.items():
        group_results=[]
        for idx,group in enumerate(groups,1):
            ts=group_rows(group,trips); r=resources(ts); r.update({'方案':name,'组编号':idx,'服务区':'|'.join(sorted(group))})
            group_results.append(r)
            flat={'方案':name,'组编号':idx,'服务区':r['服务区'],'架次':r['架次'],'完工时间_s':r['完工时间'],'工作量_s':r['工作量秒'],'能耗_kWh':r['能耗']}
            for m in ('A','B','C'):
                x=r['按机型'][m]
                flat.update({f'{m}运输机需求':x['运输无人机需求'],f'{m}运输机缺口':x['无人机缺口'],f'{m}电池需求':x['共享电池需求'],f'{m}电池缺口':x['电池缺口']})
            flat.update({'中继无人机需求':r['中继无人机需求'],'中继能源组件需求':r['中继能源组件需求']}); rows.append(flat)
        summary[name]={'groups':group_results,'总架次':sum(x['架次'] for x in group_results),'总能耗':sum(x['能耗'] for x in group_results),'最大组完工时间':max(x['完工时间'] for x in group_results),'工作量极差':max(x['工作量秒'] for x in group_results)-min(x['工作量秒'] for x in group_results)}
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'Q4_分区配置.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (OUT/'Q4_summary.json').write_text(json.dumps({'inventory':INV,'schemes':summary,'componentConstraint':'Q2多点架次服务区连通分量不可拆分'},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()

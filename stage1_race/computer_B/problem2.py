import math,itertools,json
from pathlib import Path
import numpy as np,pandas as pd,rasterio
ROOT=Path(r'D:\D ti'); DATA=ROOT/'数据'/'无人机应急物资运输基础数据'; GEO=ROOT/'数据'/'镇龙乡地理空间数据'/'镇龙乡及周边地理数据'/'数字高程模型数据（DEM）'; tif=GEO/'镇龙乡及周边30米DEM.tif'
loc=pd.read_excel(DATA/'调度中心与服务区.xlsx',header=None); rr=loc.iloc[2]; O={'id':'O01','lon':float(rr.iloc[2]),'lat':float(rr.iloc[3]),'z':float(rr.iloc[4])}; services={}
for _,r in loc.iloc[6:21].iterrows(): services[str(r.iloc[0])]={'id':str(r.iloc[0]),'lon':float(r.iloc[2]),'lat':float(r.iloc[3]),'z':float(r.iloc[4])}
boxes=pd.read_excel(DATA/'物资需求与配送时限.xlsx',sheet_name='逐箱货箱清单'); boxes.columns=['box','svc','type','mass','vol','first','first_deadline','due','priority']; boxes['first']=boxes['first'].astype(str).str.contains('是'); boxes['first_deadline']=pd.to_numeric(boxes.first_deadline,errors='coerce'); boxes['due']=pd.to_numeric(boxes.due,errors='coerce')
md=pd.read_excel(DATA/'运输无人机数据.xlsx',header=None); U={}
for _,r in md.iloc[2:5].iterrows():
 g=str(r.iloc[0]); U[g]={'name':r.iloc[1],'empty':float(r.iloc[2]),'Q':float(r.iloc[3]),'V':float(r.iloc[4]),'v':float(r.iloc[5]),'L0':float(r.iloc[6]),'LF':float(r.iloc[7]),'E':float(r.iloc[8]),'rho':float(r.iloc[9])/100,'prep':float(r.iloc[10]),'load_t':float(r.iloc[11]),'handoff':float(r.iloc[12]),'box_handoff':float(r.iloc[13]),'vu':float(r.iloc[14]),'vd':float(r.iloc[15]),'eta_up':float(r.iloc[16]),'Tfull':{'A':1800,'B':2400,'C':3000}[g]}
with rasterio.open(tif) as ds: DEM=ds.read(1); tr=ds.transform; W,H=ds.width,ds.height
def hav(a,b):
 R=6371000.; p1,p2=math.radians(a['lat']),math.radians(b['lat']); dp=math.radians(b['lat']-a['lat']); dl=math.radians(b['lon']-a['lon']); h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2; return 2*R*math.asin(math.sqrt(h))
def ht(lon,lat):
 c=max(0,min(W-1,int((lon-tr.c)/tr.a))); row=max(0,min(H-1,int((lat-tr.f)/tr.e))); return float(DEM[row,c])
cache={}
def seg(g,a,b,q):
 k=(g,a['id'],b['id'],round(q,5))
 if k in cache:return cache[k]
 d=hav(a,b); n=max(2,int(d/20)+1); z=max(ht(a['lon']+(b['lon']-a['lon'])*u,a['lat']+(b['lat']-a['lat'])*u) for u in np.linspace(0,1,n))+50; za=a['z']+(30 if a['id']!='O01' else 0); zb=b['z']+(30 if b['id']!='O01' else 0); hp=max(0,z-za); hm=max(0,z-zb); m=U[g]; L=m['L0']-(m['L0']-m['LF'])*(q/m['Q'])**1.5 if q else m['L0']; E=d/L*m['E']+(m['empty']+q)*9.80665*hp/(3.6e6*m['eta_up']); t=hp/m['vu']+d/m['v']+hm/m['vd']; cache[k]=(E,t); return E,t
def route_eval(g,svcs,sel):
 m=U[g]; nodes=[O]+[services[s] for s in svcs]+[O]; total_mass=sum(float(boxes.loc[i,'mass']) for i in sel); e=t=0.; rem=total_mass; arrivals={}; idx=0
 # prep + loading
 t=m['prep']+len(sel)*m['load_t']
 for k in range(len(nodes)-1):
  ee,tt=seg(g,nodes[k],nodes[k+1],rem); e+=ee; t+=tt
  if k<len(svcs):
   s=svcs[k]; ids=[i for i in sel if boxes.loc[i,'svc']==s]; t+=m['handoff']+len(ids)*m['box_handoff']; arrivals[s]=t; rem-=sum(float(boxes.loc[i,'mass']) for i in ids)
 if e>(1-m['rho'])*m['E']+1e-7:return None
 return {'energy':e,'duration':t,'arrivals':arrivals,'mass':total_mass,'volume':sum(float(boxes.loc[i,'vol']) for i in sel)}
def select_boxes(g,svcs,remain):
 m=U[g]; cand=[i for i in remain if boxes.loc[i,'svc'] in svcs]
 # urgent/medical/first first; higher priority first
 cand.sort(key=lambda i:(0 if boxes.loc[i,'first'] else 1, float(boxes.loc[i,'due']) if not pd.isna(boxes.loc[i,'due']) else 1e9, -float(boxes.loc[i,'priority'])))
 sel=[]
 for i in cand:
  trial=sel+[i]; mass=sum(float(boxes.loc[j,'mass']) for j in trial); vol=sum(float(boxes.loc[j,'vol']) for j in trial)
  if mass>m['Q'] or vol>m['V']:continue
  if route_eval(g,svcs,trial) is not None: sel=trial
 # ensure anchor present if possible
 return sel
# resources: 4 A, 2 B, 2 C drones; battery pools 6,4,4
drones={g:[0.0]*n for g,n in {'A':4,'B':2,'C':2}.items()}; bats={g:[0.0]*n for g,n in {'A':6,'B':4,'C':4}.items()}; remain=set(boxes.index); trips=[]; clock=0

def best_pair(g):
 best=None
 for u,du in enumerate(drones[g]):
  for b,br in enumerate(bats[g]):
   st=max(du,br)
   if best is None or st<best[0]:best=(st,u,b)
 return best
def charge(g,e):
 s=1-e/U[g]['E']; T=U[g]['Tfull'];
 return T*(0.65*(0.90-s)/0.90+0.35) if s<0.90 else T*0.35*(1-s)/0.10
while remain:
 # anchor: earliest due among remaining, prioritize first then medical then due
 anchor=min(remain,key=lambda i:(0 if boxes.loc[i,'first'] else (1 if boxes.loc[i,'type']=='医疗物资' else 2),float(boxes.loc[i,'due']) if not pd.isna(boxes.loc[i,'due']) else 1e9,-float(boxes.loc[i,'priority'])))
 a_s=str(boxes.loc[anchor,'svc']); others=sorted({str(boxes.loc[i,'svc']) for i in remain if str(boxes.loc[i,'svc'])!=a_s},key=lambda s:hav(services[a_s],services[s]))[:5]
 candidates=[]
 route_opts=[(a_s,),*[(a_s,s) for s in others]]
 for g in U:
  st,u,b=best_pair(g)
  for rv in route_opts:
   sel=select_boxes(g,rv,remain)
   if anchor not in sel:continue
   ev=route_eval(g,rv,sel)
   if ev is None:continue
   arr={s:st+v for s,v in ev['arrivals'].items()}; late=0.; hard=0
   for i in sel:
    at=arr[str(boxes.loc[i,'svc'])]; due=float(boxes.loc[i,'due']) if not pd.isna(boxes.loc[i,'due']) else 1e9; fd=float(boxes.loc[i,'first_deadline']) if not pd.isna(boxes.loc[i,'first_deadline']) else due
    late += float(boxes.loc[i,'priority'])*max(0,at-due)
    if boxes.loc[i,'first'] and at>fd+1e-9: hard += at-fd
    if boxes.loc[i,'type']=='医疗物资' and at>due+1e-9: hard += 0.5*(at-due)
   finish=st+ev['duration']; score=hard*1e8+late+0.0001*finish+0.5*ev['energy']-0.05*len(sel)
   candidates.append((score,g,rv,sel,ev,st,u,b))
 if not candidates:
  print('NO CANDIDATE',anchor); break
 candidates.sort(key=lambda x:x[0]); score,g,rv,sel,ev,st,u,b=candidates[0]; finish=st+ev['duration']; arr={s:st+v for s,v in ev['arrivals'].items()};
 for i in sel: remain.remove(i)
 drones[g][u]=finish; bats[g][b]=finish+charge(g,ev['energy'])
 trips.append({'trip':len(trips)+1,'model':g,'drone':({'A':['U01','U02','U03','U04'],'B':['U05','U06'],'C':['U07','U08']}[g][u]),'battery':f'{g}-B{b+1}','route':['O01']+list(rv)+['O01'],'boxes':[str(boxes.loc[i,'box']) for i in sel],'box_indices':sel,'start_s':st,'finish_s':finish,'duration_s':ev['duration'],'energy_kwh':ev['energy'],'mass_kg':ev['mass'],'volume_m3':ev['volume'],'arrivals_s':arr,'charge_ready_s':bats[g][b]})
# save
(ROOT/'results').mkdir(exist_ok=True); json.dump(trips,open(ROOT/'results'/'problem2_trips.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
rows=[]
for trp in trips:
 for i in trp['box_indices']: rows.append({'trip':trp['trip'],'model':trp['model'],'drone':trp['drone'],'battery':trp['battery'],'route':'-'.join(trp['route']),'box':boxes.loc[i,'box'],'service':boxes.loc[i,'svc'],'type':boxes.loc[i,'type'],'arrival_s':trp['arrivals_s'][str(boxes.loc[i,'svc'])],'due_s':boxes.loc[i,'due'],'first':boxes.loc[i,'first']})
pd.DataFrame(rows).to_csv(ROOT/'results'/'problem2_box_delivery.csv',index=False,encoding='utf-8-sig')
summary={'trips':len(trips),'makespan_s':max((t['finish_s'] for t in trips),default=0),'energy_kwh':sum(t['energy_kwh'] for t in trips),'by_model':{g:{'trips':sum(t['model']==g for t in trips),'energy':sum(t['energy_kwh'] for t in trips if t['model']==g),'drones_used':len({t['drone'] for t in trips if t['model']==g})} for g in U},'unserved':len(remain),'late_hard':0}
for t in trips:
 for i in t['box_indices']:
  at=t['arrivals_s'][str(boxes.loc[i,'svc'])]; due=boxes.loc[i,'due']; fd=boxes.loc[i,'first_deadline']
  if boxes.loc[i,'first'] and at>fd: summary['late_hard']+=1
  if boxes.loc[i,'type']=='医疗物资' and at>due: summary['late_hard']+=1
json.dump(summary,open(ROOT/'results'/'problem2_summary.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False,indent=2))
for t in trips: print(t['trip'],t['model'],t['route'],round(t['start_s'],1),round(t['finish_s'],1),len(t['boxes']),[round(v,1) for v in t['arrivals_s'].values()])


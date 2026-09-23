import math,itertools,json
from pathlib import Path
import numpy as np,pandas as pd,rasterio
from ortools.sat.python import cp_model
ROOT=Path(r'D:\D ti'); DATA=ROOT/'数据'/'无人机应急物资运输基础数据'; GEO=ROOT/'数据'/'镇龙乡地理空间数据'/'镇龙乡及周边地理数据'/'数字高程模型数据（DEM）'; TIF=GEO/'镇龙乡及周边30米DEM.tif'
loc=pd.read_excel(DATA/'调度中心与服务区.xlsx',header=None); r=loc.iloc[2]; O={'id':'O01','lon':float(r.iloc[2]),'lat':float(r.iloc[3]),'z':float(r.iloc[4])}; S={}
for _,r in loc.iloc[6:21].iterrows(): S[str(r.iloc[0])]={'id':str(r.iloc[0]),'lon':float(r.iloc[2]),'lat':float(r.iloc[3]),'z':float(r.iloc[4])}
B=pd.read_excel(DATA/'物资需求与配送时限.xlsx',sheet_name='逐箱货箱清单'); B.columns=['box','svc','type','mass','vol','first','first_deadline','due','priority']
M=pd.read_excel(DATA/'运输无人机数据.xlsx',header=None); U={}
for _,r in M.iloc[2:5].iterrows():
 g=str(r.iloc[0]); U[g]={'Q':float(r.iloc[3]),'V':float(r.iloc[4]),'v':float(r.iloc[5]),'L0':float(r.iloc[6]),'LF':float(r.iloc[7]),'E':float(r.iloc[8]),'rho':float(r.iloc[9])/100,'empty':float(r.iloc[2]),'prep':float(r.iloc[10]),'load_t':float(r.iloc[11]),'handoff':float(r.iloc[12]),'box_handoff':float(r.iloc[13]),'vu':float(r.iloc[14]),'vd':float(r.iloc[15]),'eta':float(r.iloc[16])}
with rasterio.open(TIF) as ds: A=ds.read(1); tr=ds.transform; W,H=ds.width,ds.height
def hav(a,b):
 R=6371000;p=math.radians(a['lat']);q=math.radians(b['lat']);dp=math.radians(b['lat']-a['lat']);dl=math.radians(b['lon']-a['lon']);h=math.sin(dp/2)**2+math.cos(p)*math.cos(q)*math.sin(dl/2)**2;return 2*R*math.asin(math.sqrt(h))
def ht(x,y): return float(A[max(0,min(H-1,int((y-tr.f)/tr.e))),max(0,min(W-1,int((x-tr.c)/tr.a)))])
PC={}
def geom(a,b):
 k=(a['id'],b['id'])
 if k not in PC:
  d=hav(a,b); z=max(ht(a['lon']+(b['lon']-a['lon'])*u,a['lat']+(b['lat']-a['lat'])*u) for u in np.linspace(0,1,max(2,int(d/20)+1)))+50; PC[k]=(d,z)
 return PC[k]
def seg(g,a,b,q):
 m=U[g]; d,z=geom(a,b); za=a['z']+(30 if a['id']!='O01' else 0); zb=b['z']+(30 if b['id']!='O01' else 0); hp=max(0,z-za);hm=max(0,z-zb); L=m['L0']-(m['L0']-m['LF'])*(q/m['Q'])**1.5 if q else m['L0']; return d/L*m['E']+(m['empty']+q)*9.80665*hp/(3.6e6*m['eta']),hp/m['vu']+d/m['v']+hm/m['vd']
def direct(g,s,q): return tuple(sum(x) for x in zip(seg(g,O,S[s],q),seg(g,S[s],O,0)))
def maxload(g,s,rho=None):
 m=U[g]; lim=(1-(m['rho'] if rho is None else rho))*m['E'];lo,hi=0,m['Q']
 for _ in range(50):
  x=(lo+hi)/2
  if direct(g,s,x)[0]<=lim:lo=x
  else:hi=x
 return lo
types=['医疗物资','饮用水','应急食品','生活卫生用品']
def solve_service(s,g,rho=None):
 sub=B[B.svc==s]; cs=[int((sub.type==t).sum()) for t in types]; m=U[g]; pats=[]
 for x in itertools.product(*[range(c+1) for c in cs]):
  if not sum(x):continue
  mass=sum(xi*float(sub[sub.type==t].mass.iloc[0]) for xi,t in zip(x,types) if xi);vol=sum(xi*float(sub[sub.type==t].vol.iloc[0]) for xi,t in zip(x,types) if xi)
  if mass>min(m['Q'],maxload(g,s,rho))+1e-8 or vol>m['V']:continue
  E,tf=direct(g,s,mass)
  if rho is not None and E>(1-rho)*m['E']+1e-8:continue
  tm=m['prep']+sum(x)*(m['load_t']+m['box_handoff'])+m['handoff']+tf;pats.append((x,mass,vol,E,tm))
 mdl=cp_model.CpModel(); z=[mdl.NewIntVar(0,100,f'z{i}') for i in range(len(pats))]
 for k,c in enumerate(cs):mdl.Add(sum(z[i]*pats[i][0][k] for i in range(len(pats)))==c)
 mdl.Minimize(sum(z)*10**12+sum(int(pats[i][3]*1e5)*z[i] for i in range(len(pats)))*10**4+sum(int(pats[i][4]*100)*z[i] for i in range(len(pats))))
 so=cp_model.CpSolver();so.parameters.max_time_in_seconds=5;so.parameters.num_search_workers=8;so.Solve(mdl); chosen=[]
 for i,v in enumerate(z):chosen += [pats[i]]*so.Value(v)
 return {'trips':len(chosen),'energy':sum(p[3] for p in chosen),'time':sum(p[4] for p in chosen),'patterns':[p[0] for p in chosen]}
results=[]
for s in S:
 by={g:{'max_safe':maxload(g,s),'plan':solve_service(s,g)} for g in U}; best=min(by,key=lambda g:(by[g]['plan']['trips'],by[g]['plan']['energy'],by[g]['plan']['time']));results.append({'service':s,'models':by,'best_model':best})
json.dump(results,open(ROOT/'results/problem1_summary.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
rows=[];bestrows=[]
for r in results:
 for g,v in r['models'].items():rows.append({'service':r['service'],'model':g,'max_safe_kg':v['max_safe'],'trips':v['plan']['trips'],'energy_kwh':v['plan']['energy'],'time_s':v['plan']['time'],'selected':g==r['best_model']})
 for j,x in enumerate(r['models'][r['best_model']]['plan']['patterns'],1):
  sub=B[B.svc==r['service']]; mass=sum(xi*float(sub[sub.type==t].mass.iloc[0]) for xi,t in zip(x,types) if xi);vol=sum(xi*float(sub[sub.type==t].vol.iloc[0]) for xi,t in zip(x,types) if xi);E,tf=direct(r['best_model'],r['service'],mass);bestrows.append({'service':r['service'],'trip':j,'model':r['best_model'],'box_counts':str(x),'mass_kg':mass,'volume_m3':vol,'energy_kwh':E,'time_s':U[r['best_model']]['prep']+sum(x)*(U[r['best_model']]['load_t']+U[r['best_model']]['box_handoff'])+U[r['best_model']]['handoff']+tf})
pd.DataFrame(rows).to_csv(ROOT/'results/problem1_model_summary.csv',index=False,encoding='utf-8-sig');pd.DataFrame(bestrows).to_csv(ROOT/'results/problem1_best_batches.csv',index=False,encoding='utf-8-sig')
# reserve sensitivity of maximum safe payload only
sens=[]
for rho in [0.10,0.15,0.20,0.25,0.30,0.40]:
 for s in S:
  row={'rho':rho,'service':s}
  for g in U: row['max_'+g+'_kg']=maxload(g,s,rho)
  sens.append(row)
pd.DataFrame(sens).to_csv(ROOT/'results/problem1_sensitivity.csv',index=False,encoding='utf-8-sig')
print('problem1 complete')

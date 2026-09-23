import csv, math, struct, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter

# 自适应工程根目录路径
_CUR_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _CUR_DIR.parent.parent
ROOT = _WORKSPACE_ROOT / '数模题目' / 'D题'
if not ROOT.exists():
    ROOT = Path(r'D:\数学建模2026\D题')

DATA = ROOT / '数据' / '无人机应急物资运输基础数据'
DEM_PATH = ROOT / '数据' / '镇龙乡地理空间数据' / '镇龙乡及周边地理数据' / '数字高程模型数据（DEM）' / '镇龙乡及周边30米DEM.tif'

NS = {'a':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def colnum(ref):
    n = 0
    for ch in ref:
        if ch.isalpha(): n = n * 26 + ord(ch.upper()) - 64
    return n

def read_xlsx(path):
    """Return list of sheets; each sheet is list of row lists, using first row as headers."""
    with zipfile.ZipFile(path) as z:
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            sr=ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in sr.findall('a:si', NS):
                shared.append(''.join(t.text or '' for t in si.findall('.//a:t', NS)))
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        rel=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        relmap={r.attrib['Id']:r.attrib['Target'] for r in rel}
        out={}
        for sh in wb.findall('a:sheets/a:sheet', NS):
            name=sh.attrib['name']
            target=relmap[sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target=target.lstrip('/')
            if not target.startswith('xl/'): target='xl/'+target
            root=ET.fromstring(z.read(target))
            rows=[]
            for row in root.findall('.//a:sheetData/a:row', NS):
                cells={}
                for c in row.findall('a:c', NS):
                    ref=c.attrib.get('r',''); idx=colnum(ref)
                    t=c.attrib.get('t'); v=c.find('a:v', NS)
                    if t=='inlineStr': val=''.join(x.text or '' for x in c.findall('.//a:t', NS))
                    elif v is None: val=''
                    else:
                        val=v.text or ''
                        if t=='s': val=shared[int(val)]
                        elif t=='b': val='TRUE' if val=='1' else 'FALSE'
                    cells[idx]=val
                if cells:
                    mx=max(cells); rows.append([cells.get(i,'') for i in range(1,mx+1)])
            out[name]=rows
        return out

def fnum(x, default=0.0):
    try:
        if x is None or x=='': return default
        return float(x)
    except Exception:
        return default

def read_dem(path=DEM_PATH):
    b=path.read_bytes(); fmt='<' if b[:2]==b'II' else '>'
    ifd=struct.unpack_from(fmt+'I',b,4)[0]; n=struct.unpack_from(fmt+'H',b,ifd)[0]
    typelen={1:1,2:1,3:2,4:4,5:8,6:1,7:1,8:2,9:4,10:8,11:4,12:8}
    tags={}
    for i in range(n):
        p=ifd+2+12*i; tag,typ,count=struct.unpack_from(fmt+'HHI',b,p)
        size=typelen.get(typ,1)*count
        raw=b[p+8:p+8+size] if size<=4 else b[struct.unpack_from(fmt+'I',b,p+8)[0]:struct.unpack_from(fmt+'I',b,p+8)[0]+size]
        if typ==3: vals=list(struct.unpack(fmt+('H'*count),raw))
        elif typ==4: vals=list(struct.unpack(fmt+('I'*count),raw))
        elif typ==11: vals=list(struct.unpack(fmt+('f'*count),raw))
        elif typ==12: vals=list(struct.unpack(fmt+('d'*count),raw))
        elif typ==5: vals=[struct.unpack(fmt+'II',raw[j:j+8]) for j in range(0,size,8)]
        else: vals=[]
        tags[tag]=vals
    width, height = tags[256][0], tags[257][0]
    bits=tags[258][0]; compression=tags[259][0]
    tilew, tileh=tags[322][0], tags[323][0]
    offsets, counts=tags[324], tags[325]
    if compression != 32773 or bits != 32:
        raise ValueError(f'Unsupported DEM compression={compression}, bits={bits}')
    arr=[[0.0]*width for _ in range(height)]
    def unpack_packbits(data):
        out=bytearray(); i=0
        while i<len(data):
            c=struct.unpack('b',data[i:i+1])[0]; i+=1
            if 0<=c<=127:
                out.extend(data[i:i+c+1]); i+=c+1
            elif -127<=c<=-1:
                if i>=len(data): break
                out.extend(data[i:i+1]* (1-c)); i+=1
            else:
                pass
        return out
    tile_cols=(width+tilew-1)//tilew; tile_rows=(height+tileh-1)//tileh
    for tr in range(tile_rows):
        for tc in range(tile_cols):
            k=tr*tile_cols+tc
            raw=unpack_packbits(b[offsets[k]:offsets[k]+counts[k]])
            vals=struct.unpack('<'+('f'*(len(raw)//4)),raw)
            for rr in range(tileh):
                r=tr*tileh+rr
                if r>=height: break
                base=rr*tilew
                for cc in range(tilew):
                    c=tc*tilew+cc
                    if c>=width: break
                    arr[r][c]=vals[base+cc]
    # GeoTIFF model tiepoint and pixel scale. Coordinates are the upper-left pixel.
    scale=tags[33550]; tie=tags[33922]
    lon0, lat0 = tie[3], tie[4]; dx, dy = scale[0], scale[1]
    return arr, width, height, lon0, lat0, dx, dy

class DEM:
    def __init__(self,path=DEM_PATH):
        self.a,self.w,self.h,self.lon0,self.lat0,self.dx,self.dy=read_dem(path)
    def elev(self, lon, lat):
        c=(lon-self.lon0)/self.dx; r=(self.lat0-lat)/self.dy
        c0=max(0,min(self.w-1,int(round(c)))); r0=max(0,min(self.h-1,int(round(r))))
        return self.a[r0][c0]
    def max_along(self, lon1,lat1,lon2,lat2):
        d=geo_dist(lon1,lat1,lon2,lat2); n=max(2,int(d/30)+1); mx=-1e9
        for k in range(n+1):
            t=k/n; mx=max(mx,self.elev(lon1+t*(lon2-lon1),lat1+t*(lat2-lat1)))
        return mx

def geo_dist(lon1,lat1,lon2,lat2):
    R=6371000.0; p=math.radians((lat1+lat2)/2)
    return R*math.sqrt(math.radians(lon2-lon1)**2*math.cos(p)**2 + math.radians(lat2-lat1)**2)

def load_data():
    s=read_xlsx(DATA/'调度中心与服务区.xlsx')['数据']
    center={'id':s[2][0],'name':s[2][1],'lon':fnum(s[2][2]),'lat':fnum(s[2][3]),'z':fnum(s[2][4])}
    zones={}
    for r in s[5:20]:
        zones[r[0]]={'id':r[0],'name':r[1],'lon':fnum(r[2]),'lat':fnum(r[3]),'z':fnum(r[4]),'pop':int(fnum(r[5]))}
    md=read_xlsx(DATA/'物资需求与配送时限.xlsx')
    rows=md['逐箱货箱清单']; boxes=[]
    for r in rows[1:]:
        if not r or not r[0]: continue
        boxes.append({'id':r[0],'zone':r[1],'type':r[2],'mass':fnum(r[3]),'vol':fnum(r[4]),'first':r[5]=='是','cutoff':fnum(r[6],1e99),'due':fnum(r[7],1e99),'prio':fnum(r[8])})
    ud=read_xlsx(DATA/'运输无人机数据.xlsx')['数据']
    types={}
    for r in ud[2:5]:
        types[r[0]]={'id':r[0],'name':r[1],'empty':fnum(r[2]),'maxmass':fnum(r[3]),'vol':fnum(r[4]),'vc':fnum(r[5]),'L0':fnum(r[6]),'LF':fnum(r[7]),'Euse':fnum(r[8]),'rho':fnum(r[9])/100,'prep':fnum(r[10]),'loadt':fnum(r[11]),'handoff':fnum(r[12]),'perbox':fnum(r[13]),'vup':fnum(r[14]),'vdown':fnum(r[15]),'eta':fnum(r[16]),'rdown':fnum(r[17])}
    drones=[]
    for r in ud[8:16]:
        if r and r[0]: drones.append({'id':r[0],'type':r[1],'pos':r[2]})
    batteries={r[0]:{'n':int(fnum(r[1])),'charge':fnum(r[2])} for r in ud[19:22] if r and r[0]}
    return center,zones,boxes,types,drones,batteries

def node_info(center,zones):
    nodes={'O01':center}; nodes.update(zones); return nodes

def leg_geom(dem,nodes,i,j):
    a,b=nodes[i],nodes[j]
    d=geo_dist(a['lon'],a['lat'],b['lon'],b['lat']); terrain=dem.max_along(a['lon'],a['lat'],b['lon'],b['lat'])
    cruise=max(terrain,a['z'],b['z'])+50
    hi=a['z'] if i=='O01' else a['z']+30
    hj=b['z'] if j=='O01' else b['z']+30
    return {'d':d,'terrain':terrain,'cruise':cruise,'hu':max(0,cruise-hi),'hd':max(0,cruise-hj)}

def L_eff(g,q):
    if q<0 or q>g['maxmass']+1e-9: return 0
    return g['L0']-(g['L0']-g['LF'])*(q/g['maxmass'])**1.5

def leg_time(g,geom):
    return geom['hu']/g['vup']+geom['d']/g['vc']+geom['hd']/g['vdown']

def leg_energy(g,geom,q):
    L=L_eff(g,q)
    if L<=0: return 1e99
    # Standard-range horizontal energy plus gravitational climb energy; masses are kg and heights m.
    ehor=g['Euse']*geom['d']/L
    eup=(g['empty']+q)*9.80665*geom['hu']/(3.6e6*max(g['eta'],1e-9))
    return ehor+eup

def route_metrics(g,dem,nodes,route,loads):
    # route is O01, zones..., O01; loads[k] is payload carried on leg k (after prior deliveries).
    total_t=0; total_e=0; geoms=[]
    for k,(i,j) in enumerate(zip(route[:-1],route[1:])):
        geom=leg_geom(dem,nodes,i,j); geoms.append(geom)
        q=loads[k]
        total_t+=leg_time(g,geom); total_e+=leg_energy(g,geom,q)
    return total_t,total_e,geoms

def direct_metrics(g,dem,nodes,zone,q):
    route=['O01',zone,'O01']; return route_metrics(g,dem,nodes,route,[q,0])

def max_safe_payload(g,dem,nodes,zone):
    lo,hi=0.0,g['maxmass']
    for _ in range(70):
        mid=(lo+hi)/2; t,e,_=direct_metrics(g,dem,nodes,zone,mid)
        if e <= (1-g['rho'])*g['Euse'] and mid<=g['maxmass']:
            lo=mid
        else: hi=mid
    return lo

def zone_pattern_opt(g,dem,nodes,zone_boxes, zone):
    # Enumerate all feasible patterns by counts of four goods. Use DP over delivered-count state.
    types_order=['医疗物资','饮用水','应急食品','生活卫生用品']
    maxcounts=tuple(sum(1 for b in zone_boxes if b['type']==t) for t in types_order)
    masses={t:next(b['mass'] for b in zone_boxes if b['type']==t) for t in types_order if any(b['type']==t for b in zone_boxes)}
    vols={t:next(b['vol'] for b in zone_boxes if b['type']==t) for t in types_order if any(b['type']==t for b in zone_boxes)}
    patterns=[]
    def rec(k,cur):
        if k==4:
            if sum(cur)==0: return
            m=sum(cur[i]*masses.get(types_order[i],0) for i in range(4)); v=sum(cur[i]*vols.get(types_order[i],0) for i in range(4))
            if m>g['maxmass']+1e-9 or v>g['vol']+1e-9: return
            tflight,e,_=direct_metrics(g,dem,nodes,zone,m)
            nbox=sum(cur)
            t=g['prep'] + nbox*g['loadt'] + tflight + g['handoff'] + nbox*g['perbox']
            if e>(1-g['rho'])*g['Euse']+1e-9: return
            patterns.append((tuple(cur),m,v,t,e))
            return
        for x in range(maxcounts[k]+1):
            cur.append(x); rec(k+1,cur); cur.pop()
    rec(0,[])
    # Keep nondominated patterns (larger counts with lower/equal resources dominate only if all counts >=). Leave all for DP.
    dp={tuple([0]*4):(0,0.0,0.0,[])}
    for _ in range(sum(maxcounts)+2):
        changed=False; nd=dict(dp)
        for state,(cnt,en,tm,patlist) in dp.items():
            for pat in patterns:
                nxt=tuple(min(maxcounts[i],state[i]+pat[0][i]) for i in range(4))
                if nxt==state: continue
                val=(cnt+1,en+pat[4],tm+pat[3],patlist+[pat])
                if nxt not in nd or val[:3] < nd[nxt][:3]: nd[nxt]=val; changed=True
        dp=nd
        if not changed: break
    target=maxcounts
    best=dp.get(target)
    if best is None: raise RuntimeError(f'No feasible patterns for {zone} {maxcounts}')
    # Prioritize first-batch boxes by marking the first pattern; the DP pattern count is enough for Q1.
    return patterns,best

def q1(dem):
    center,zones,boxes,types,drones,batteries=load_data(); nodes=node_info(center,zones)
    results=[]
    for tid,g in types.items():
        for zid,z in zones.items():
            results.append((tid,zid,max_safe_payload(g,dem,nodes,zid)))
    print('MAX_SAFE_PAYLOAD')
    for tid in types:
        vals=[v for t,z,v in results if t==tid]
        print(tid, 'min/max', min(vals),max(vals), 'avg',sum(vals)/len(vals))
    print('Q1_ZONE_SOLUTIONS')
    sols={}
    for zid in zones:
        zb=[b for b in boxes if b['zone']==zid]
        cand=[]
        for tid,g in types.items():
            try:
                patterns,best=zone_pattern_opt(g,dem,nodes,zb,zid)
                cand.append((best[0],best[1],best[2],tid,best[3]))
            except Exception as e: pass
        cand.sort(key=lambda x:(x[0],x[1],x[2]))
        sols[zid]=cand[0]
        c=cand[0]
        print(zid,'type',c[3],'trips',c[0],'energy',round(c[1],4),'time',round(c[2],1),'patterns',[p[0] for p in c[4]])
    return center,zones,boxes,types,drones,batteries,nodes,sols

def charge_time(s, full):
    if s < 0.90:
        return full*(0.65*(0.90-s)/0.90 + 0.35)
    return full*0.35*(1-s)/0.10

def expand_zone_patterns(g,dem,nodes,zone_boxes,zone):
    """Build direct trips for a zone, keeping all boxes and placing first-batch boxes as early as possible."""
    _,best=zone_pattern_opt(g,dem,nodes,zone_boxes,zone)
    patterns=best[3]
    bytype=defaultdict(list)
    for b in sorted(zone_boxes,key=lambda x:(not x['first'],x['due'],x['id'])):
        bytype[b['type']].append(b)
    # Reserve first-batch boxes for the first trips; each pattern gets earliest due boxes first.
    trips=[]
    for pi,pat in enumerate(patterns):
        ids=[]
        for ti,tname in enumerate(['医疗物资','饮用水','应急食品','生活卫生用品']):
            n=pat[0][ti]
            take=bytype[tname][:n]; bytype[tname]=bytype[tname][n:]
            ids.extend(take)
        q=sum(b['mass'] for b in ids); v=sum(b['vol'] for b in ids)
        tt,e,_=direct_metrics(g,dem,nodes,zone,q)
        trips.append({'zone':zone,'type':g['id'],'boxes':ids,'mass':q,'vol':v,'flight':tt,'energy':e})
    return trips

def q2_schedule(dem, nodes, zones, boxes, types, drones, batteries, sols=None):
    # Use the minimum-sortie per-zone solution from Q1 as a feasible direct-trip baseline.
    trips=[]
    for zid in zones:
        zb=[b for b in boxes if b['zone']==zid]
        # Pick the lexicographically best type as in Q1.
        cand=[]
        for tid,g in types.items():
            try:
                _,best=zone_pattern_opt(g,dem,nodes,zb,zid)
                cand.append((best[0],best[1],best[2],tid))
            except Exception: pass
        cand.sort(key=lambda x:(x[0],x[1],x[2]))
        tid=cand[0][3]; trips.extend(expand_zone_patterns(types[tid],dem,nodes,zb,zid))
    # Priority: trips containing first boxes with earliest cutoff, then the earliest due box.
    def trip_key(tr):
        first=[b['cutoff'] for b in tr['boxes'] if b['first']]
        due=[b['due'] for b in tr['boxes']]
        return (min(first) if first else 1e99, min(due), -max(b['prio'] for b in tr['boxes']))
    trips.sort(key=trip_key)
    # Build resource states. Batteries are shared within a type.
    drone_state={d['id']:{'id':d['id'],'type':d['type'],'avail':0.0,'trips':[]} for d in drones}
    batt_state={tid:[{'id':f'{tid}-B{k+1}','avail':0.0} for k in range(batteries[tid]['n'])] for tid in batteries}
    for idx,tr in enumerate(trips,1):
        tid=tr['type']; g=types[tid]
        candidates=[]
        for did,ds in drone_state.items():
            if ds['type']!=tid: continue
            for bs in batt_state[tid]:
                st=max(ds['avail'],bs['avail'])
                candidates.append((st,did,bs['id']))
        if not candidates: raise RuntimeError(f'No resource for type {tid}')
        start,did,bid=min(candidates)
        n=len(tr['boxes']); prep=g['prep']; loadtime=n*g['loadt']; hand=g['handoff']+n*g['perbox']
        deliver=start+prep+loadtime+tr['flight']/2+hand
        end=start+prep+loadtime+tr['flight']+hand
        soc=max(0.0,1-tr['energy']/g['Euse']); recharge=charge_time(soc,batteries[tid]['charge'])
        drone_state[did]['avail']=end; drone_state[did]['trips'].append(idx)
        for bs in batt_state[tid]:
            if bs['id']==bid: bs['avail']=end+recharge
        tr.update({'idx':idx,'drone':did,'battery':bid,'start':start,'deliver':deliver,'end':end,'soc_end':soc,'recharge':recharge})
    # Check all deadline constraints.
    checks=[]
    for tr in trips:
        for b in tr['boxes']:
            checks.append({'box':b['id'],'zone':b['zone'],'deliver':tr['deliver'],'deadline':b['cutoff'] if b['first'] else b['due'],'first':b['first'],'ok':tr['deliver'] <= (b['cutoff'] if b['first'] else b['due'])+1e-9})
    feasible=all(x['ok'] for x in checks)
    makespan=max((tr['end'] for tr in trips),default=0.0)
    total_energy=sum(tr['energy'] for tr in trips); total_time=sum(tr['end']-tr['start'] for tr in trips)
    return trips, checks, {'feasible':feasible,'makespan':makespan,'total_energy':total_energy,'total_time':total_time,'sorties':len(trips),'drones':drone_state,'batteries':batt_state}

def q2_priority_schedule(dem, nodes, zones, boxes, types, drones, batteries):
    """Deadline-oriented direct-trip heuristic: send all first-batch boxes on A-type trips, then bulk remainder."""
    trips=[]
    for zid in zones:
        zb=[b for b in boxes if b['zone']==zid]
        first=[b for b in zb if b['first']]
        rest=[b for b in zb if not b['first']]
        # A is sufficient for every first batch under the given data and provides four parallel airframes.
        ga=types['A']; q=sum(b['mass'] for b in first); v=sum(b['vol'] for b in first)
        if q>ga['maxmass'] or v>ga['vol']:
            raise RuntimeError(f'First batch does not fit A at {zid}')
        ft,fe,_=direct_metrics(ga,dem,nodes,zid,q)
        trips.append({'zone':zid,'type':'A','boxes':first,'mass':q,'vol':v,'flight':ft,'energy':fe,'kind':'first'})
        if rest:
            cand=[]
            for tid,g in types.items():
                try:
                    _,best=zone_pattern_opt(g,dem,nodes,rest,zid)
                    cand.append((best[0],best[1],best[2],tid))
                except Exception: pass
            cand.sort(key=lambda x:(x[0],x[1],x[2]))
            tid=cand[0][3]
            remtr=expand_zone_patterns(types[tid],dem,nodes,rest,zid)
            for tr in remtr: tr['kind']='bulk'
            trips.extend(remtr)
    # First-batch trips are ordered by cutoffs; bulk trips by earliest due time and priority.
    def key(tr):
        if tr['kind']=='first': return (0,min(b['cutoff'] for b in tr['boxes']),-max(b['prio'] for b in tr['boxes']))
        return (1,min(b['due'] for b in tr['boxes']),-max(b['prio'] for b in tr['boxes']))
    trips.sort(key=key)
    drone_state={d['id']:{'id':d['id'],'type':d['type'],'avail':0.0,'trips':[]} for d in drones}
    batt_state={tid:[{'id':f'{tid}-B{k+1}','avail':0.0} for k in range(batteries[tid]['n'])] for tid in batteries}
    for idx,tr in enumerate(trips,1):
        tid=tr['type']; g=types[tid]; candidates=[]
        for did,ds in drone_state.items():
            if ds['type']!=tid: continue
            for bs in batt_state[tid]: candidates.append((max(ds['avail'],bs['avail']),did,bs['id']))
        if not candidates: raise RuntimeError(f'No resource for type {tid}')
        start,did,bid=min(candidates); n=len(tr['boxes'])
        prep=g['prep']; loadtime=n*g['loadt']; hand=g['handoff']+n*g['perbox']
        deliver=start+prep+loadtime+tr['flight']/2+hand
        end=start+prep+loadtime+tr['flight']+hand
        soc=max(0.0,1-tr['energy']/g['Euse']); recharge=charge_time(soc,batteries[tid]['charge'])
        drone_state[did]['avail']=end; drone_state[did]['trips'].append(idx)
        for bs in batt_state[tid]:
            if bs['id']==bid: bs['avail']=end+recharge
        tr.update({'idx':idx,'drone':did,'battery':bid,'start':start,'deliver':deliver,'end':end,'soc_end':soc,'recharge':recharge})
    checks=[]
    for tr in trips:
        for b in tr['boxes']:
            dl=b['cutoff'] if b['first'] else b['due']
            checks.append({'box':b['id'],'zone':b['zone'],'deliver':tr['deliver'],'deadline':dl,'first':b['first'],'ok':tr['deliver']<=dl+1e-9})
    return trips,checks,{'feasible':all(x['ok'] for x in checks),'makespan':max((tr['end'] for tr in trips),default=0.0),'total_energy':sum(tr['energy'] for tr in trips),'total_time':sum(tr['end']-tr['start'] for tr in trips),'sorties':len(trips),'drones':drone_state,'batteries':batt_state}

def schedule_trip_list(trips, types, drones, batteries):
    """Schedule already-built direct trips on heterogeneous drones and shared batteries."""
    trips=[dict(t) for t in trips]
    def key(tr):
        dl=[(b['cutoff'] if b['first'] else b['due']) for b in tr['boxes']]
        return (min(dl), -max(b['prio'] for b in tr['boxes']))
    trips.sort(key=key)
    drone_state={d['id']:{'id':d['id'],'type':d['type'],'avail':0.0,'trips':[]} for d in drones}
    batt_state={tid:[{'id':f'{tid}-B{k+1}','avail':0.0} for k in range(batteries[tid]['n'])] for tid in batteries}
    for idx,tr in enumerate(trips,1):
        tid=tr['type']; g=types[tid]; candidates=[]
        for did,ds in drone_state.items():
            if ds['type']!=tid: continue
            for bs in batt_state[tid]: candidates.append((max(ds['avail'],bs['avail']),did,bs['id']))
        if not candidates: return None
        start,did,bid=min(candidates); n=len(tr['boxes'])
        prep=g['prep']; loadtime=n*g['loadt']; hand=g['handoff']+n*g['perbox']
        deliver=start+prep+loadtime+tr['flight']/2+hand
        end=start+prep+loadtime+tr['flight']+hand
        soc=max(0.0,1-tr['energy']/g['Euse']); recharge=charge_time(soc,batteries[tid]['charge'])
        drone_state[did]['avail']=end; drone_state[did]['trips'].append(idx)
        for bs in batt_state[tid]:
            if bs['id']==bid: bs['avail']=end+recharge
        tr.update({'idx':idx,'drone':did,'battery':bid,'start':start,'deliver':deliver,'end':end,'soc_end':soc,'recharge':recharge})
    checks=[]
    for tr in trips:
        for b in tr['boxes']:
            dl=b['cutoff'] if b['first'] else b['due']
            checks.append({'box':b['id'],'zone':b['zone'],'deliver':tr['deliver'],'deadline':dl,'first':b['first'],'ok':tr['deliver']<=dl+1e-9})
    lateness=[max(0,x['deliver']-x['deadline']) for x in checks]
    return trips,checks,{'feasible':max(lateness,default=0)<=1e-9,'viol':sum(x>1e-9 for x in lateness),'late_sec':sum(lateness),'max_late':max(lateness,default=0),'makespan':max((tr['end'] for tr in trips),default=0.0),'total_energy':sum(tr['energy'] for tr in trips),'total_time':sum(tr['end']-tr['start'] for tr in trips),'sorties':len(trips),'drones':drone_state,'batteries':batt_state}

def candidate_parts(dem,nodes,zones,boxes,types):
    """Generate per-zone candidate direct-trip partitions for urgent and non-urgent boxes."""
    out={}
    for zid in zones:
        zb=[b for b in boxes if b['zone']==zid]
        first=[b for b in zb if b['first']]
        base=min([b['cutoff'] for b in first]+[b['due'] for b in first]+[1e99])
        urgent=[b for b in zb if b['first'] or b['due']<=base+1e-9]
        rest=[b for b in zb if b not in urgent]
        out[zid]={'urgent':{},'bulk':{}}
        for label,arr in [('urgent',urgent),('bulk',rest)]:
            if not arr: continue
            for tid,g in types.items():
                try:
                    _,best=zone_pattern_opt(g,dem,nodes,arr,zid)
                    # Rebuild the exact box list from the selected patterns.
                    out[zid][label][tid]=expand_zone_patterns(g,dem,nodes,arr,zid)
                except Exception:
                    pass
    return out

def optimize_q2_choices(dem,nodes,zones,boxes,types,drones,batteries):
    cand=candidate_parts(dem,nodes,zones,boxes,types)
    # Initial choice: minimum trips, then energy, then A/B/C preference for light tasks.
    choice={}
    for zid in zones:
        choice[zid]={}
        for label in ['urgent','bulk']:
            opts=cand[zid][label]
            if not opts: continue
            choice[zid][label]=min(opts,key=lambda tid:(len(opts[tid]),sum(t['energy'] for t in opts[tid]),tid))
    def build(ch):
        alltr=[]
        for zid in zones:
            for label in ['urgent','bulk']:
                if label in ch[zid]: alltr.extend(cand[zid][label][ch[zid][label]])
        return schedule_trip_list(alltr,types,drones,batteries)
    def score(res):
        if res is None: return (999,1e99,1e99,1e99,999)
        s=res[2]
        return (s['viol'],s['late_sec'],s['makespan'],s['total_energy'],s['sorties'])
    best=build(choice); bestscore=score(best)
    # Coordinate descent over zone and urgency/bulk type; repeat until no improvement.
    for _ in range(6):
        improved=False
        for zid in zones:
            for label in ['urgent','bulk']:
                if not cand[zid][label]: continue
                old=choice[zid][label]
                for tid in cand[zid][label]:
                    choice[zid][label]=tid
                    res=build(choice); sc=score(res)
                    if sc < bestscore:
                        best,bestscore=res,sc; improved=True; old=tid
                    else:
                        choice[zid][label]=old
        if not improved: break
    return best,choice,cand

if __name__=='__main__':
    dem=DEM(); print('DEM',dem.w,dem.h,'sample',dem.elev(109.2308517,23.0085095),dem.elev(109.2760168,23.0194009))
    c,z,b,t,d,ba,n,sols=q1(dem)
    trips,checks,summary=q2_schedule(dem,n,z,b,t,d,ba,sols)
    print('Q2_SUMMARY',summary['feasible'],summary['sorties'],round(summary['makespan'],1),round(summary['total_energy'],4),round(summary['total_time'],1))
    print('Q2_DEADLINE_VIOLATIONS',sum(1 for x in checks if not x['ok']))
    for tr in trips:
        print('TRIP',tr['idx'],tr['drone'],tr['battery'],tr['zone'],[b['id'] for b in tr['boxes']],round(tr['mass'],1),round(tr['start'],1),round(tr['deliver'],1),round(tr['end'],1),round(tr['energy'],3))
    trips2,checks2,summary2=q2_priority_schedule(dem,n,z,b,t,d,ba)
    print('Q2_PRIORITY_SUMMARY',summary2['feasible'],summary2['sorties'],round(summary2['makespan'],1),round(summary2['total_energy'],4),round(summary2['total_time'],1),'viol',sum(1 for x in checks2 if not x['ok']))
    for tr in trips2:
        print('P_TRIP',tr['idx'],tr['drone'],tr['battery'],tr['zone'],tr['kind'],[b['id'] for b in tr['boxes']],round(tr['mass'],1),round(tr['start'],1),round(tr['deliver'],1),round(tr['end'],1),round(tr['energy'],3))
    opt,choice,cand=optimize_q2_choices(dem,n,z,b,t,d,ba)
    if opt:
        tr3,ch3,s3=opt
        print('Q2_OPT_SUMMARY',s3['feasible'],s3['sorties'],round(s3['makespan'],1),round(s3['total_energy'],4),round(s3['total_time'],1),'viol',s3['viol'],'late',round(s3['late_sec'],1))
        print('Q2_OPT_CHOICE',choice)
        for tr in tr3:
            print('O_TRIP',tr['idx'],tr['drone'],tr['battery'],tr['zone'],[b['id'] for b in tr['boxes']],round(sum(b['mass'] for b in tr['boxes']),1),round(tr['start'],1),round(tr['deliver'],1),round(tr['end'],1),round(tr['energy'],3))

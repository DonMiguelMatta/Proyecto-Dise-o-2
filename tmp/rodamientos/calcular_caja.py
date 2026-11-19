from pathlib import Path
import math,json,hashlib
from openpyxl import load_workbook
OUT=Path('outputs/rodamientos_caja');OUT.mkdir(parents=True,exist_ok=True)
source=Path(r'D:\migue\OneDrive - UVG\A2UVG 2026\Diseño_2\Proyecto\Calculos\CALCULADORA EJES.xlsx')
source_hash=hashlib.sha256(source.read_bytes()).hexdigest();w=load_workbook(source,data_only=True);inp=w['INICIAR P1']
LB=4.4482216152605;g=9.81;fw=1.2;target=50000
tn=3580;ts=20;rpm_start=.5;navg_factor=(tn+rpm_start*ts)/3600
f=(rpm_start*ts)/(tn+rpm_start*ts)
catalog={
 '6001':dict(kind='bola',d=12,D=28,B=8,C=5.10,C0=2.39,fo=13.2,da_min=14,da_max=None,Da_max=26,ra=.3,p=3,ew=10/9,page='B-8/B-9'),
 '6000':dict(kind='bola',d=10,D=26,B=8,C=4.55,C0=1.96,fo=12.4,da_min=12,da_max=None,Da_max=24,ra=.3,p=3,ew=10/9,page='B-8/B-9'),
 '6300':dict(kind='bola',d=10,D=35,B=11,C=8.20,C0=3.50,fo=11.4,da_min=14,da_max=17,Da_max=31,ra=.6,p=3,ew=10/9,page='B-8/B-9'),
 '4T-30302':dict(kind='cono',d=15,D=42,B=14.25,C=23.2,C0=20.8,Y=2.11,Y0=1.16,e=.29,a=9.5,da_min=20.5,db_max=22,Da_max=36.5,Da_min=35,Db_min=38,ra=1,p=10/3,ew=9/8,page='B-142/B-143'),
 '4T-30304CA':dict(kind='cono',d=20,D=52,B=16.25,C=31.0,C0=31.0,Y=1.10,Y0=.60,e=.55,a=13.5,da_min=28.5,db_max=27.5,Da_max=43.5,Da_min=39.5,Db_min=48,ra=1.5,p=10/3,ew=9/8,page='B-142/B-143')}
def interp(q,xs,ys):
 if q<=xs[0]:return ys[0]
 if q>=xs[-1]:return ys[-1]
 for j in range(1,len(xs)):
  if q<=xs[j]:return ys[j-1]+(ys[j]-ys[j-1])*(q-xs[j-1])/(xs[j]-xs[j-1])
def ball(c,fr,fa):
 x=[.172,.345,.689,1.03,1.38,2.07,3.45,5.17,6.89]
 e=interp(c['fo']*fa/(c['C0']*1000),x,[.19,.22,.26,.28,.30,.34,.38,.42,.44])
 y=interp(c['fo']*fa/(c['C0']*1000),x,[2.3,1.99,1.71,1.55,1.45,1.31,1.15,1.04,1.0])
 P=fr if fa/fr<=e else .56*fr+y*fa
 return P,max(fr,.6*fr+.5*fa),e,y
def cone(c,fr,fa):
 P=fr if fa/fr<=c['e'] else .4*fr+c['Y']*fa
 return P,max(fr,.5*fr+c['Y0']*fa)
def pair(c1,c2,fr1,fr2,fa_ext):
 # Positive external load is resisted by bearing 2; no preload.
 s1=.5*fr1/c1['Y'];s2=.5*fr2/c2['Y']
 fa2=max(s2,s1+fa_ext);fa1=fa2-fa_ext
 assert math.isclose(fa2-fa1,fa_ext,rel_tol=1e-12,abs_tol=1e-9)
 return (cone(c1,fr1,fa1),cone(c2,fr2,fa2)),(fa1,fa2)
rows=[]
def row(shaft,pos,number,frn,frs,fan,fas,fn,old_d,details=None):
 c=catalog[number]
 if c['kind']=='bola':
  pn,p0n,en,yn=ball(c,frn,fan);ps,p0s,es,ys=ball(c,frs,fas)
 else:pn,ps,p0n,p0s=details
 pe=((1-f)*pn**c['p']+f*ps**c['p'])**(1/c['p'])
 pd=fw*pe;pm=fw*max(p0n,p0s)
 nmean=fn*navg_factor
 life=1e6/(60*nmean)*(1000*c['C']/pd)**c['p']
 c_ind=pd/1000*(60*nmean*target/1e6)**(1/c['p'])
 r=dict(shaft=shaft,position=pos,number=number,kind=c['kind'],d_mm=c['d'],D_mm=c['D'],B_mm=c['B'],old_d_in=old_d,Fr_nom_N=frn,Fr_start_N=frs,Fa_nom_bound_N=fan,Fa_start_bound_N=fas,P_nom_N=pn,P_start_N=ps,P_eq_N=pe,P_design_N=pd,P0_design_N=pm,C_kN=c['C'],C0_kN=c['C0'],C_required_individual_50k_kN=c_ind,L10_h=life,S0=1000*c['C0']/pm,rpm=fn,nmean=nmean,p=c['p'],ew=c['ew'],catalog=c)
 assert pm<1000*c['C0']
 assert fw*max(pn,ps)<=500*c['C']
 rows.append(r)
# Reactions are derived from shaft sketches, not stale data in the bearings tab.
xa=4+.625;xb=4+1.25+1/3+2+.25+.2+.625;xg=4+1.25+1/3+1
F=inp['E25'].value;R=inp['E26'].value;factor=inp['E31'].value/F
rad=math.hypot(F,R);fr11=rad*(xb-xg)/(xb-xa)*LB;fr12=rad*(xg-xa)/(xb-xa)*LB
assert math.isclose(fr11+fr12,rad*LB,rel_tol=1e-12)
# Previous larger gears' CAD masses are used only as conservative preliminary upper bounds.
# Add 1 kg per shaft/fasteners until current CAD weights are supplied.
weights=[(1.670+1)*g,(15.086+2.227+1)*g,(20.114+1)*g]
row('Eje 1','B','6001',fr11,fr11*factor,0,0,1800,.5)
row('Eje 1','G','6001',fr12,fr12*factor,weights[0],weights[0],1800,.5)
s=w['Eje 2'];fr21=math.hypot(s['S12'].value,s['S14'].value)*LB;fr22=math.hypot(s['S13'].value,s['S15'].value)*LB
frs21=math.hypot(s['U12'].value,s['U14'].value)*LB;frs22=math.hypot(s['U13'].value,s['U15'].value)*LB
row('Eje 2','A','6000',fr21,frs21,0,0,600,.375)
row('Eje 2','G','6300',fr22,frs22,weights[1],weights[1],600,.375)
s=w['Eje 3'];fr31=math.hypot(s['S12'].value,s['S14'].value)*LB;fr32=math.hypot(s['S13'].value,s['S15'].value)*LB
frs31=math.hypot(s['U12'].value,s['U14'].value)*LB;frs32=math.hypot(s['U13'].value,s['U15'].value)*LB
cu=catalog['4T-30302'];cl=catalog['4T-30304CA'];cut=803.5943444082303;peak=9500
def envelope(fr1,fr2,thrust):
 # Each bearing is bounded over cut with zero/deadweight and idle weight-only rotation.
 cases=[pair(cu,cl,fr1,fr2,fa) for fa in [thrust,thrust-weights[2],-weights[2]]]
 P=[max(cases[k][0][j][0] for k in range(3)) for j in range(2)]
 P0=[max(cases[k][0][j][1] for k in range(3)) for j in range(2)]
 Fa=[max(cases[k][1][j] for k in range(3)) for j in range(2)]
 return P,P0,Fa
pn,p0n,fan=envelope(fr31,fr32,cut);ps,p0s,fas=envelope(frs31,frs32,peak)
row('Eje 3','G','4T-30302',fr31,frs31,fan[0],fas[0],200,.5,(pn[0],ps[0],p0n[0],p0s[0]))
row('Eje 3','B','4T-30304CA',fr32,frs32,fan[1],fas[1],200,.625,(pn[1],ps[1],p0n[1],p0s[1]))
def joint(factor=1):
 lo=0;hi=min(x['L10_h']*factor for x in rows)
 for _ in range(100):
  mid=(lo+hi)/2
  if sum((mid/(x['L10_h']*factor))**x['ew'] for x in rows)>1:hi=mid
  else:lo=mid
 return (lo+hi)/2
conservative=lambda factor:factor*sum(x['L10_h']**(-10/9) for x in rows)**(-9/10)
life=joint();lifehalf=joint(.5)
assert life>=target and lifehalf>=target
assert conservative(1)<=life
for r in rows:assert r['S0']>=(2 if r['kind']=='bola' else 3)
assert source_hash==hashlib.sha256(source.read_bytes()).hexdigest()
res=dict(rows=rows,L_joint_h=life,L_joint_conservative_h=conservative(1),L_joint_a3_05_h=lifehalf,weight_bounds_N=weights,nominal_seconds=tn,start_seconds=ts,start_speed_fraction=rpm_start,start_revolution_fraction=f,fw=fw,target_joint_h=target,shaft1_geometry=dict(left=xa,right=xb,gear=xg),source_sha256=source_hash)
(OUT/'calculo.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(rows=[{k:x[k] for k in ['shaft','position','number','Fr_nom_N','Fr_start_N','Fa_nom_bound_N','P_nom_N','P_start_N','P_eq_N','L10_h','S0']} for x in rows],joint=life,half=lifehalf,weight_bounds=weights),ensure_ascii=False))
